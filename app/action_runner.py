import json
import os
import shutil
import sys
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from git import GitCommandError, Repo

from config.config import *
from core.use_cases.analyze_tf_code import AnalyzeTFCode
from core.use_cases.detect_tf_changes import DetectTFChanges
from infrastructure.adapters.git.git_adapter import GitAdapter
from utils.logger_utils import logger


def save_results(results, output_path=OUTPUT_JSON_PATH):
    """Sauvegarde les résultats de l'analyse dans un fichier JSON."""
    try:
        with open(output_path, "w") as json_file:
            json.dump(results, json_file, indent=4)
        logger.info(f"Résultats sauvegardés : `{output_path}`")
    except Exception as e:
        logger.error(f"Erreur de sauvegarde : {e}")


def verify_jar():
    """Vérifie la présence de TerraMetrics.jar."""
    if not os.path.exists(TERRAMETRICS_JAR_PATH):
        logger.error(f"TerraMetrics JAR introuvable : `{TERRAMETRICS_JAR_PATH}`")
        raise SystemExit(1)


def clone_repo_if_needed(repo_url):
    """Clone un repo distant si nécessaire et retourne son chemin."""
    if repo_url:
        temp_dir = tempfile.mkdtemp()
        try:
            logger.info(f"Clonage du repo `{repo_url}`...")
            Repo.clone_from(repo_url, temp_dir)
            return temp_dir
        except GitCommandError as e:
            logger.error(f"Erreur de clonage : {e}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise SystemExit(1)
    return Repo(search_parent_directories=True).working_tree_dir


def detect_and_analyze(commit_hash, repo_path):
    """Détecte les fichiers Terraform modifiés et les analyse avec TerraMetrics et ML."""
    detect_changes = DetectTFChanges(repo_path)
    analyze_code = AnalyzeTFCode(TERRAMETRICS_JAR_PATH, OUTPUT_JSON_PATH)

    try:
        logger.info("Extraction des modifications Terraform...")
        modified_blocks = detect_changes.get_modified_tf_blocks(commit_hash)
        blocks_before_change = detect_changes.get_tf_blocks_before_change(commit_hash)

        if not modified_blocks:
            logger.info("Aucun fichier Terraform modifié.")
            raise SystemExit(0)

        logger.info(
            "Analyse des fichiers modifiés avec TerraMetrics et prédiction ML..."
        )
        analysis_results = analyze_code.analyze_blocks(modified_blocks)
        before_metrics = analyze_code.analyze_blocks(blocks_before_change)
        differences = analyze_code.compare_metrics(before_metrics, analysis_results)

        return differences

    except Exception as e:
        logger.error(f"Erreur d'analyse : {e}")
        raise SystemExit(1)


def display_analysis_results(results):
    """Affiche les résultats de l'analyse Terraform avec prédictions ML."""
    logger.info("\n📊 Résumé de l'analyse des fichiers Terraform :")
    for file, content in results.items():
        print(f"\n📂 Fichier analysé : {file}")
        if "data" in content:
            for block in content["data"]:
                block_name = block.get("block_name", "[Nom Inconnu]")
                block_type = block.get("block", "[Type Inconnu]")
                defect_status = block.get("defect_prediction", "N/A")
                print(f"    - {block_type} {block_name} -> {defect_status}")


def cleanup_temp_repo(repo_url, repo_path):
    """Supprime le dossier temporaire s'il y a eu un clonage."""
    if repo_url:
        logger.info(f"Suppression du repo temporaire `{repo_path}`...")
        shutil.rmtree(repo_path, ignore_errors=True)


def main():
    """Exécute l’analyse Terraform avec la gestion correcte du commit hash."""

    # Vérifier que Git est bien initialisé
    GitAdapter.verify_git_repo()

    # Parsing des arguments
    args = sys.argv[1:]
    repo_url = None
    commit_hash = "HEAD"

    # Vérifier si un commit hash est fourni
    if args and not args[0].startswith("--"):
        commit_hash = args[0]

    # Vérifier si un repo distant est fourni
    if "--repo" in args:
        repo_index = args.index("--repo")
        if repo_index + 1 < len(args):
            repo_url = args[repo_index + 1]

    # Déterminer le chemin du dépôt (soit local, soit cloné)
    repo_path = clone_repo_if_needed(repo_url)

    # Vérification du fichier TerraMetrics JAR
    verify_jar()

    try:
        analysis_results = detect_and_analyze(commit_hash, repo_path)
        display_analysis_results(analysis_results)
    except SystemExit:
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erreur fatale : {e}")
        sys.exit(1)

    save_results(analysis_results)
    cleanup_temp_repo(repo_url, repo_path)


if __name__ == "__main__":
    main()
