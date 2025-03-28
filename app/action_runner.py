import argparse
import json
import os
import subprocess

from app import config
from core.parsers.contribution_builder import (
    get_contribution,
    get_previous_contributions,
)
from core.parsers.metrics_extractor_factory import MetricsExtractorFactory
from core.parsers.process_metric_calculation import ProcessMetrics
from core.use_cases.analyze_tf_code import AnalyzeTFCode
from core.use_cases.detect_tf_changes import DetectTFChanges
from core.use_cases.feature_vector_builder import FeatureVectorBuilder
from core.use_cases.report_generator import ReportGenerator
from infrastructure.git.git_adapter import GitAdapter
from infrastructure.ml.defect_history_manager import (
    load_defect_history,
    update_defect_history,
)
from infrastructure.ml.model_factory import ModelFactory
from utils.logger_utils import logger

subprocess.run(
    ["git", "config", "--global", "--add", "safe.directory", "/github/workspace"],
    check=False,
)


def verify_jar():
    """Vérifie la présence du fichier JAR TerraMetrics."""
    if not os.path.exists(config.TERRAMETRICS_JAR_PATH):
        logger.error(f"TerraMetrics JAR introuvable : `{config.TERRAMETRICS_JAR_PATH}`")
        raise SystemExit(1)


def run_prediction_flow(model_type: str):
    logger.info("Formatage des fichiers Terraform (terraform fmt)...")
    run_terraform_fmt(config.REPO_PATH)

    logger.info("Construction des vecteurs de caractéristiques...")
    builder = FeatureVectorBuilder(config.REPO_PATH, config.TERRAMETRICS_JAR_PATH)
    vectors = builder.build_vectors()

    if not vectors:
        logger.warning("Aucun vecteur généré - aucun bloc Terraform modifié.")
        return

    logger.info(f"Chargement du modèle : {model_type}")
    model = ModelFactory.get_model(model_type)
    logger.info(model.describe())

    logger.info("Prédictions des défauts...")
    predictions_with_confidence = model.predict_with_confidence(vectors)

    # Extraire juste les labels pour la sauvegarde dans defect history
    predictions = {k: v[0] for k, v in predictions_with_confidence.items()}

    logger.info(f"Sauvegarde des prédictions dans `{config.DEFECT_HISTORY_PATH}`")
    update_defect_history(predictions)

    # Génération du rapport HTML
    report_path = ReportGenerator().generate(predictions, model.describe())
    logger.info(f"Rapport disponible ici : {report_path}")

    # Affichage avec historique
    defect_history = load_defect_history()
    print("=" * 60)
    print("📊 Résultats de la prédiction :")

    total = 0
    defectives = 0

    for block_id, (label, confidence) in predictions_with_confidence.items():
        try:
            file_path, block_identifiers = block_id.split("::", 1)
            contrib = get_contribution(config.REPO_PATH, file_path, block_identifiers)
            previous = get_previous_contributions(
                config.REPO_PATH, file_path, block_identifiers, defect_history
            )
            if contrib:
                pm = ProcessMetrics(contrib, previous)
                count = pm.num_defects_in_block_before()

                status_icon = "🔴" if label else "🟢"
                status_label = "Defective" if label else "Clean"

                print(f"\n{status_icon} Block: {block_id}")
                print(f"    -> État: {status_label}")
                print(f"    -> Score de confiance: {confidence:.2f}")
                print(f"    -> Défauts précédents: {count}")

                total += 1
                defectives += 1 if label else 0
            else:
                logger.warning(f"Contribution introuvable pour {block_id}")
        except Exception as e:
            logger.error(f"Erreur sur le bloc {block_id} : {e}")

    print("\n" + "=" * 60)
    print(
        f"🧾 Résumé : {total} blocs analysés - {defectives} defectives, {total - defectives} clean"
    )
    print("=" * 60)


def run_terraform_fmt(repo_path: str) -> None:
    """
    Applique `terraform fmt -recursive` pour garantir un formatage correct.
    """
    try:
        result = subprocess.run(
            ["terraform", "fmt", "-recursive", repo_path],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.stdout.strip():
            logger.info("🔧 terraform fmt appliqué :")
            print(result.stdout.strip())
        else:
            logger.info(
                "Aucun fichier à reformater : tous les fichiers .tf sont propres."
            )
    except FileNotFoundError:
        logger.warning(
            "Terraform n'est pas installé. Impossible d'appliquer terraform fmt."
        )
    except Exception as e:
        logger.error(f"Erreur lors de terraform fmt : {e}")


def generate_report_from_history():
    """
    Génère un rapport HTML uniquement à partir du fichier defect_history.json,
    sans relancer d'analyse ou de prédiction.
    """
    history = load_defect_history()

    if not history:
        logger.warning("Impossible de générer le rapport : defect_history.json vide.")
        return

    # Construit les prédictions à partir des dernières entrées de l'historique
    latest_predictions = {
        block_id: entries[-1]["fault_prone"]
        for block_id, entries in history.items()
        if entries
    }

    report_path = ReportGenerator().generate(latest_predictions)
    logger.info(f"Rapport généré depuis l'historique : {report_path}")


def detect_and_analyze(extractor_type):
    """
    Détecte les blocs Terraform modifiés et exécute l'analyse des métriques.

    Args:
        extractor_type (str): Type d'extracteur de métriques à utiliser.

    Returns:
        dict: Résultats de l'analyse des métriques.
    """
    logger.info(f"Démarrage de l'analyse avec l'extracteur [{extractor_type}]...")

    detect_changes = DetectTFChanges(config.REPO_PATH)

    if extractor_type == "delta":
        modified_blocks = detect_changes.get_changed_blocks()
    else:
        modified_blocks = detect_changes.get_modified_tf_blocks()

    if not modified_blocks:
        logger.warning("Aucun bloc Terraform modifié détecté.")
        return {}

    try:
        metrics_extractor = MetricsExtractorFactory.get_extractor(
            extractor_type, config.TERRAMETRICS_JAR_PATH
        )
    except (ValueError, NotImplementedError) as e:
        logger.error(f"Erreur lors de la sélection de l'extracteur : {e}")
        raise SystemExit(1)

    analyzer = AnalyzeTFCode(config.REPO_PATH, metrics_extractor)
    metrics_results = analyzer.analyze_blocks(modified_blocks)

    logger.info("Analyse terminée avec succès.")
    return metrics_results


def save_results(results, output_path):
    """
    Sauvegarde les résultats de l'analyse dans un fichier JSON.

    Args:
        results (dict): Résultats de l'analyse des métriques.
        output_path (str): Chemin du fichier de sortie JSON.
    """
    try:
        with open(output_path, "w") as json_file:
            json.dump(results, json_file, indent=4)
        logger.info(f"Résultats sauvegardés dans `{output_path}`")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des résultats : {e}")


def display_analysis_results(results, extractor_type):
    """Affiche les résultats de l'analyse Terraform avec les métriques extraites."""
    for file, content in results.items():
        msg = (
            "📂 Fichier analysé : "
            if extractor_type in ["delta", "codemetrics"]
            else "🧱 Bloc analysé : "
        )
        print("\n" + "=" * 60)
        print(f"{msg} {file}")
        print("=" * 60)

        if extractor_type in ["delta", "process"]:
            formatted_metrics = json.dumps(content, indent=4, ensure_ascii=False)
            print(formatted_metrics)
        else:
            if "data" in content:
                for block in content["data"]:
                    block_name = block.get("block_name", "[Nom Inconnu]")
                    block_type = block.get("block", "[Type Inconnu]")
                    print(f"    🔹 {block_type} {block_name}")

        print("=" * 60)


def show_defect_history():
    """
    Affiche le contenu du fichier defect_history.json (s'il existe),
    avec l'historique complet par commit.
    """
    history = load_defect_history()

    if not history:
        logger.warning(
            "Aucune prédiction trouvée - defect_history.json est vide ou inexistant."
        )
        return

    print("=" * 60)
    print("📘 Contenu de defect_history.json :")
    for block_id, predictions in history.items():
        print(f"🔹 {block_id}")
        for entry in predictions:
            fault = entry.get("fault_prone", "?")
            date = entry.get("date", "?")
            commit = entry.get("commit", "?")
            print(f"    - commit {commit} -> fault_prone = {fault} (prédit le {date})")
    print("=" * 60)


def main():
    """Point d'entrée principal pour exécuter l'analyse et sauvegarder les résultats."""
    parser = argparse.ArgumentParser(
        description="TFDefectGA - Analyse et prédiction de défauts Terraform"
    )
    parser.add_argument(
        "--model", type=str, help="Nom du modèle de prédiction à utiliser (ex: dummy)"
    )
    parser.add_argument(
        "--extractor",
        type=str,
        choices=["codemetrics", "delta", "process"],
        default="codemetrics",
        help="Type d'extracteur à utiliser",
    )
    parser.add_argument(
        "--show-history",
        action="store_true",
        help="Afficher le contenu de defect_history.json",
    )
    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="Générer uniquement le rapport HTML à partir de defect_history.json",
    )

    args = parser.parse_args()

    if args.show_history:
        show_defect_history()
        return

    if args.generate_report:
        generate_report_from_history()
        return

    GitAdapter.verify_git_repo()

    if args.model:
        try:
            run_prediction_flow(args.model)
        except ValueError as e:
            logger.error(str(e))
            raise SystemExit(1)
        return

    if args.extractor in ["codemetrics", "delta"]:
        verify_jar()

    results = detect_and_analyze(args.extractor)

    if results:
        if args.extractor == "delta":
            output_file = config.DELTA_METRICS_JSON_PATH
        elif args.extractor == "process":
            output_file = config.PROCESS_METRICS_JSON_PATH
        else:
            output_file = config.CODE_METRICS_JSON_PATH

        display_analysis_results(results, args.extractor)
        save_results(results, output_file)
    else:
        logger.warning("Aucun résultat à sauvegarder.")


if __name__ == "__main__":
    main()
