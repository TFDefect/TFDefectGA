from abc import ABC, abstractmethod
from typing import Dict, List

class BaseMetricsExtractor(ABC):
    """
    Classe abstraite pour les extracteurs de métriques Terraform.
    """

    @abstractmethod
    def extract_metrics(self, modified_blocks: Dict[str, List[str]]) -> Dict[str, dict]:
        """
        Méthode abstraite pour extraire les métriques à partir de blocs Terraform modifiés.

        Args:
            modified_blocks (Dict[str, List[str]]): Dictionnaire des fichiers et leurs blocs modifiés.

        Returns:
            Dict[str, dict]: Dictionnaire contenant les métriques extraites.
        """
        pass