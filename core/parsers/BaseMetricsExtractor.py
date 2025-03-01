from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np


class BaseMetricsExtractor(ABC):
    """
    Classe abstraite pour extraire et transformer les métriques Terraform.
    """

    @abstractmethod
    def _load_json(self):
        """Charge les métriques Terraform depuis le fichier JSON."""
        pass

    @abstractmethod
    def extract_features(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extrait les métriques essentielles et les transforme en vecteurs utilisables pour ML.
        Retourne :
            - X : Liste des features normalisées.
            - y : Liste des labels (0: non-defect, 1: defect) générés aléatoirement.
        """
        pass

    @abstractmethod
    def compare_metrics(self, before_metrics: dict, after_metrics: dict) -> dict:
        """
        Compare les métriques avant et après les changements.
        Retourne :
            - differences : Différences entre les métriques avant et après les changements.
        """
        pass