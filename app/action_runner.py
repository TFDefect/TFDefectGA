import json
import os
import shutil
import sys
import tempfile

from git import GitCommandError, Repo

from config.config import *
from core.use_cases.analyze_tf_code import AnalyzeTFCode
from core.use_cases.detect_tf_changes import DetectTFChanges
from infrastructure.adapters.git.git_adapter import GitAdapter
from utils.logger_utils import setup_logger

logger = setup_logger()


def save_results_to_file(results, output_path=OUTPUT_JSON_PATH):
    """Enregistre les résultats de l'analyse dans un fichier JSON."""
    try:
        with open(output_path, "w") as json_file:
            json.dump(results, json_file, indent=4)
        logger.info(f"Résultats sauvegardés dans `{output_path}`")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des résultats : {e}")


def verify_jar_path(jar_path):
    """Vérifie que le fichier TerraMetrics JAR existe."""
    if not os.path.exists(jar_path):
        logger.error(
            f"Erreur : Le fichier TerraMetrics JAR est introuvable à `{jar_path}`"
        )
        raise SystemExit(1)


def clone_repository(repo_url):
    """Clone un dépôt distant et retourne le chemin local temporaire."""
    temp_dir = tempfile.mkdtemp()
    try:
        logger.info(f"Clonage du dépôt {repo_url} dans {temp_dir}...")
        Repo.clone_from(repo_url, temp_dir)
        return temp_dir
    except GitCommandError as e:
        logger.error(f"Erreur lors du clonage du dépôt {repo_url}: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise SystemExit(1)


def main():
    """Exécute l'analyse des modifications Terraform."""
    # Vérification que Git est bien initialisé
    GitAdapter.verify_git_repo()

    # Parsing des arguments
    args = sys.argv[1:]
    repo_url = None
    commit_hash = "HEAD"
    analyze_repo = "--repo" in args

    # Vérifier si un repo distant est fourni
    if "--repo" in args:
        repo_index = args.index("--repo")
        if repo_index + 1 < len(args):
            repo_url = args[repo_index + 1]

    # Déterminer le chemin du dépôt
    if repo_url:
        repo_path = clone_repository(repo_url)
        commit_hash = args[0] if args and not args[0].startswith("--") else "HEAD"
    else:
        repo_path = Repo(search_parent_directories=True).working_tree_dir
        commit_hash = args[0] if args and not args[0].startswith("--") else "HEAD"

    logger.info(f"Répertoire du repo détecté : {repo_path}")

    # Vérification du fichier TerraMetrics
    verify_jar_path(TERRAMETRICS_JAR_PATH)

    # Initialiser les use cases
    detect_changes = DetectTFChanges(repo_path)
    analyze_code = AnalyzeTFCode(TERRAMETRICS_JAR_PATH)

    try:
        if analyze_repo:
            logger.info("Analyse complète du repo Terraform avec TerraMetrics...")
            analysis_results = analyze_code.analyze_blocks(
                detect_changes.get_modified_tf_blocks(commit_hash)
            )
        else:
            logger.info("Extraction des modifications Terraform...")
            modified_blocks = detect_changes.get_modified_tf_blocks(commit_hash)

            if not modified_blocks:
                logger.info("Aucun fichier Terraform modifié.")
                raise SystemExit(0)

            logger.info("Analyse des fichiers modifiés avec TerraMetrics...")
            analysis_results = analyze_code.analyze_blocks(modified_blocks)

    except Exception as e:
        logger.error(f"Erreur lors de l'analyse avec TerraMetrics : {e}")
        raise SystemExit(1)

    # Affichage des résultats
    logger.info("Résultats de l'analyse des fichiers Terraform")
    separator = "-" * shutil.get_terminal_size().columns

    for file, analysis in analysis_results.items():
        print(f"Fichier analysé : {file}")
        print(json.dumps(analysis, indent=4))
        print("\n" + separator + "\n")

    # Sauvegarde des résultats
    save_results_to_file(analysis_results)

    # Nettoyage du dépôt cloné si applicable
    if repo_url:
        logger.info(f"Suppression du répertoire temporaire {repo_path}...")
        shutil.rmtree(repo_path, ignore_errors=True)


if __name__ == "__main__":
    main()
