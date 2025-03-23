import json
import os
import subprocess
import tempfile
from typing import Dict, List

from core.parsers.base_metrics_extractor import BaseMetricsExtractor
from utils.logger_utils import logger


class CodeMetricsExtractor(BaseMetricsExtractor):
    """
    Classe permettant d'exécuter TerraMetrics et d'extraire les métriques des blocs Terraform modifiés.
    """

    def __init__(self, jar_path: str = "libs/terraform_metrics-1.0.jar"):
        """
        Initialise l'extracteur de métriques.

        Args:
            jar_path (str): Chemin vers le fichier JAR de TerraMetrics.
        """
        self.jar_path = jar_path
        if not os.path.exists(self.jar_path):
            raise FileNotFoundError(f"TerraMetrics JAR introuvable : {self.jar_path}")

    def extract_metrics(self, modified_blocks: Dict[str, List[str]]) -> Dict[str, dict]:
        """
        Exécute TerraMetrics sur les blocs Terraform modifiés et extrait les métriques.

        Args:
            modified_blocks (Dict[str, List[str]]): Fichiers et leurs blocs modifiés.

        Returns:
            Dict[str, dict]: Métriques extraites pour chaque fichier.
        """
        if not modified_blocks:
            logger.warning("Aucun bloc Terraform à analyser.")
            return {}

        metrics_results = {}

        for file_name, blocks in modified_blocks.items():
            try:
                tf_path, json_path = self._create_temp_files(blocks)
                self._run_terrametrics(tf_path, json_path)

                if os.path.exists(json_path):
                    with open(json_path, "r") as f:
                        metrics_results[file_name] = json.load(f)
                else:
                    logger.error(f"Fichier JSON non généré pour {file_name}.")

            except subprocess.CalledProcessError as e:
                logger.error(f"Erreur TerraMetrics ({file_name}) : {e}")
                metrics_results[file_name] = {"error": "TerraMetrics execution failed"}

            except Exception as e:
                logger.error(f"Erreur inattendue ({file_name}): {e}")
                metrics_results[file_name] = {"error": str(e)}

            finally:
                self._cleanup_temp_files([tf_path, json_path])

        return metrics_results

    def _create_temp_files(self, blocks: List[str]) -> tuple:
        """
        Crée les fichiers temporaires Terraform (.tf) et sortie (.json).

        Args:
            blocks (List[str]): Liste de blocs à écrire.

        Returns:
            Tuple[str, str]: Chemins des fichiers .tf et .json.
        """
        tf_file = tempfile.NamedTemporaryFile(suffix=".tf", delete=False, mode="w")
        json_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)

        tf_file.write("\n\n".join(blocks))
        tf_file.close()

        return tf_file.name, json_file.name

    def _run_terrametrics(self, tf_path: str, output_path: str):
        """
        Exécute TerraMetrics pour un fichier donné.

        Args:
            tf_path (str): Chemin du fichier Terraform.
            output_path (str): Chemin du fichier de sortie JSON.
        """
        command = [
            "java",
            "-jar",
            self.jar_path,
            "--file",
            tf_path,
            "-b",
            "--target",
            output_path,
        ]

        logger.info(f"[CODE] Exécution de TerraMetrics pour {tf_path}...")
        subprocess.run(command, check=True)

    def _cleanup_temp_files(self, file_paths: List[str]):
        """
        Supprime les fichiers temporaires.

        Args:
            file_paths (List[str]): Chemins des fichiers à supprimer.
        """
        for path in file_paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logger.warning(f"Impossible de supprimer {path} : {e}")
