from abc import ABC, abstractmethod

import numpy as np


class BaseMLModel(ABC):
    """Classe de base pour tous les modèles ML utilisés dans le projet."""

    @abstractmethod
    def predict_defects(self, X: np.ndarray, num_samples: int) -> list:
        """Prédit si les blocs Terraform sont défectueux ou non."""
        pass
