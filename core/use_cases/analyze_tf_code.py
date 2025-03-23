from typing import Dict

from core.parsers.base_metrics_extractor import BaseMetricsExtractor
from core.use_cases.detect_tf_changes import DetectTFChanges


class AnalyzeTFCode:
    """Orchestration de l'analyse des blocs Terraform modifiés."""

    def __init__(self, repo_path: str, metrics_extractor: BaseMetricsExtractor):
        """
        Initialise la classe en configurant la détection des changements et l'extraction des métriques.

        Args:
            repo_path (str): Chemin du dépôt Git.
            metrics_extractor (BaseMetricsExtractor): Instance de l'extracteur de métriques.
        """
        self.detect_changes = DetectTFChanges(repo_path)
        self.metrics_extractor = metrics_extractor

    def analyze_blocks(self, modified_blocks) -> Dict[str, dict]:
        """
        Analyse les blocs Terraform modifiés.

        Args:
            modified_blocks (dict): Dictionnaire des fichiers et leurs blocs modifiés.

        Returns:
            Dict[str, dict]: Dictionnaire contenant les fichiers Terraform et leurs métriques extraites.
        """

        return self.metrics_extractor.extract_metrics(modified_blocks)
