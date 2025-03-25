from typing import Dict, List

from core.parsers.base_metrics_extractor import BaseMetricsExtractor
from core.parsers.contribution_builder import (
    get_contribution,
    get_previous_contributions,
)
from core.parsers.process_metric_calculation import ProcessMetrics
from infrastructure.ml.defect_history_manager import load_defect_history
from utils.block_utils import extract_block_identifier
from utils.logger_utils import logger


class ProcessMetricsExtractor(BaseMetricsExtractor):
    """
    Extracteur de métriques de processus pour les blocs Terraform modifiés.
    """

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path

    def extract_metrics(self, modified_blocks: Dict[str, List[str]]) -> Dict[str, dict]:
        """
        Extrait les métriques de processus pour chaque bloc modifié dans les fichiers.

        Args:
            modified_blocks (Dict[str, List[str]]): Dictionnaire {fichier: [blocs Terraform modifiés]}

        Returns:
            Dict[str, dict]: Métriques de processus pour chaque bloc (clé = fichier::identifiant_bloc)
        """
        if not modified_blocks:
            logger.warning("Aucun bloc Terraform modifié reçu.")
            return {}

        results = {}
        defect_history = load_defect_history()

        for file_path, blocks in modified_blocks.items():
            for block in blocks:
                try:
                    block_identifier = extract_block_identifier(block)

                    if not block_identifier:
                        logger.warning(
                            f"Identifiant introuvable pour bloc dans {file_path}"
                        )
                        continue

                    # Générer la contribution actuelle
                    contribution = get_contribution(
                        self.repo_path, file_path, block_identifier
                    )

                    # Générer l'historique enrichi avec defect_history
                    previous_contributions = get_previous_contributions(
                        self.repo_path, file_path, block_identifier, defect_history
                    )

                    if contribution:
                        pm = ProcessMetrics(contribution, previous_contributions)
                        metrics = pm.resume_process_metrics()
                        results[f"{file_path}::{block_identifier}"] = metrics
                    else:
                        logger.warning(
                            f"Aucune contribution détectée pour {file_path} / {block_identifier}"
                        )

                except Exception as e:
                    logger.error(
                        f"Erreur lors du traitement de {file_path} / {block_identifier}: {e}"
                    )

        return results
