import json
import os
import subprocess
import tempfile
from typing import Dict, List

from core.parsers.base_metrics_extractor import BaseMetricsExtractor
from infrastructure.git.git_changes import GitChanges
from utils.logger_utils import logger


class DeltaMetricsExtractor(BaseMetricsExtractor):
    """
    Extracteur de métriques Delta pour les fichiers Terraform modifiés.
    Compare les métriques des blocs avant et après modification.
    """

    def __init__(self, jar_path: str):
        self.jar_path = jar_path
        self.git_changes = GitChanges()
        if not os.path.exists(self.jar_path):
            raise FileNotFoundError(f"TerraMetrics JAR introuvable : {self.jar_path}")

    def extract_metrics(
        self, modified_blocks: Dict[str, Dict[str, List[str]]]
    ) -> Dict[str, dict]:
        """
        Analyse les blocs Terraform avant et après modification et calcule les deltas.

        Args:
            modified_blocks (dict): Dictionnaire contenant les fichiers et blocs modifiés.

        Returns:
            dict: Dictionnaire des métriques delta.
        """
        if not modified_blocks:
            logger.warning("Aucun bloc Terraform modifié.")
            return {}

        results = {}

        for file_name, blocks in modified_blocks.items():
            temp_tf_before, temp_tf_after = None, None
            temp_output_before, temp_output_after = None, None

            try:
                # Récupérer les blocs AVANT et APRÈS modification
                blocks_before = blocks.get("before", [])
                blocks_after = blocks.get("after", [])

                # Créer des fichiers temporaires pour stocker ces blocs
                temp_tf_before, temp_output_before = self._create_temp_files(
                    blocks_before
                )
                temp_tf_after, temp_output_after = self._create_temp_files(blocks_after)

                # Exécuter TerraMetrics AVANT et APRÈS commit
                self._run_terrametrics(temp_tf_before, temp_output_before)
                self._run_terrametrics(temp_tf_after, temp_output_after)

                # Charger les métriques JSON
                metrics_before = self._load_metrics(temp_output_before)
                metrics_after = self._load_metrics(temp_output_after)

                # Calcul des métriques Delta
                results[file_name] = self._compute_delta_metrics(
                    metrics_before, metrics_after
                )

            except subprocess.CalledProcessError as e:
                logger.error(
                    f"Erreur TerraMetrics ({file_name}): {e.stdout}\n{e.stderr}"
                )
                results[file_name] = {"error": "TerraMetrics execution failed"}

            except Exception as e:
                logger.error(f"Erreur inattendue ({file_name}): {e}")
                results[file_name] = {"error": str(e)}

            finally:
                # Nettoyage des fichiers temporaires
                self._cleanup_temp_files(
                    [
                        temp_tf_before,
                        temp_tf_after,
                        temp_output_before,
                        temp_output_after,
                    ]
                )

        return results

    def _create_temp_files(self, blocks: List[str]) -> tuple:
        """
        Crée des fichiers temporaires pour stocker les blocs Terraform en les formattant correctement.

        Args:
            blocks (List[str]): Liste des blocs Terraform.

        Returns:
            Tuple[str, str]: Chemins des fichiers temporaires (Terraform et JSON).
        """
        temp_tf = tempfile.NamedTemporaryFile(suffix=".tf", delete=False, mode="w")
        temp_json = tempfile.NamedTemporaryFile(suffix=".json", delete=False)

        # Écriture correcte avec des retours à la ligne
        formatted_blocks = "\n\n".join(blocks)
        temp_tf.write(formatted_blocks)
        temp_tf.close()

        return temp_tf.name, temp_json.name

    def _run_terrametrics(self, tf_path: str, output_path: str):
        """
        Exécute TerraMetrics sur un fichier Terraform.

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

        logger.info(f"[DELTA] Exécution de TerraMetrics pour {tf_path}...")

        subprocess.run(command, check=True)

    def _load_metrics(self, json_path: str) -> dict:
        """
        Charge les métriques depuis un fichier JSON.

        Args:
            json_path (str): Chemin du fichier JSON.

        Returns:
            dict: Données de métriques.
        """
        if not os.path.exists(json_path):
            logger.warning(f"Fichier JSON introuvable : {json_path}")
            return {}

        with open(json_path, "r") as f:
            metrics = json.load(f)

        return metrics

    def _compute_delta_metrics(self, metrics_before: dict, metrics_after: dict) -> dict:
        """
        Calcule la différence entre les métriques avant et après modification.

        Args:
            metrics_before (dict): Métriques avant commit.
            metrics_after (dict): Métriques après commit.

        Returns:
            dict: Métriques delta organisées par bloc.
        """
        if "data" not in metrics_before or "data" not in metrics_after:
            logger.warning("Métriques manquantes (clé 'data' absente).")
            return {"error": "Structure des métriques invalide (clé 'data' absente)."}

        before_data = metrics_before["data"]
        after_data = metrics_after["data"]

        if not before_data or not after_data:
            logger.warning("Une des versions des métriques ne contient pas de blocs.")
            return {"error": "Aucune métrique à comparer (données vides)."}

        delta_results = {}

        for after_block in after_data:
            block_id = after_block.get("block_identifiers", "unknown_block")

            # Recherche du bloc correspondant dans les métriques avant
            before_block = next(
                (b for b in before_data if b.get("block_identifiers") == block_id), None
            )

            if before_block is None:
                logger.warning(
                    f"Nouveau bloc détecté : {block_id} (aucune version précédente trouvée)."
                )
                continue

            # Calculer les deltas pour les clés numériques
            deltas = {}
            for key, after_value in after_block.items():
                if isinstance(after_value, (int, float)):
                    before_value = before_block.get(key, 0)
                    if isinstance(before_value, (int, float)):
                        deltas[f"{key}_delta"] = after_value - before_value

            if deltas:
                delta_results[block_id] = deltas

        return delta_results

    def _cleanup_temp_files(self, file_paths: List[str]):
        """
        Supprime les fichiers temporaires.

        Args:
            file_paths (List[str]): Liste des chemins de fichiers à supprimer.
        """
        for path in file_paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logger.warning(f"Impossible de supprimer {path} : {e}")
