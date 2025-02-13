from typing import Dict, List

from infrastructure.adapters.external_tools.terra_metrics import TerraMetricsAdapter


class AnalyzeTFCode:
    """Orchestration de l'analyse des blocs Terraform modifiés."""

    def __init__(self, jar_path: str):
        self.terra_metrics = TerraMetricsAdapter(jar_path)

    def analyze_blocks(self, modified_blocks: Dict[str, List[str]]) -> Dict[str, dict]:
        """
        Analyse les blocs Terraform modifiés avec TerraMetrics.

        Args:
            modified_blocks (Dict[str, List[str]]): Blocs Terraform modifiés.

        Returns:
            Dict[str, dict]: Résultats de l'analyse TerraMetrics.
        """
        if not modified_blocks:
            return {}

        return self.terra_metrics.analyze_blocks(modified_blocks)
