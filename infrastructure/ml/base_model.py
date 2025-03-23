from abc import ABC, abstractmethod
from typing import Dict, List


class BaseModel(ABC):
    """
    Interface pour tout modèle de prédiction de défauts Terraform.
    """

    @abstractmethod
    def predict(self, vectors: Dict[str, List[float]]) -> Dict[str, int]:
        """
        Prédit si chaque bloc est fault-prone ou non.

        Args:
            vectors (Dict[str, List[float]]): Dictionnaire {block_id: vecteur de caractéristiques}

        Returns:
            Dict[str, int]: Dictionnaire {block_id: 0 ou 1}, 1 si defectueux
        """
        pass
