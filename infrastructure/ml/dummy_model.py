import random
from typing import Dict, List

from infrastructure.ml.base_model import BaseModel


class DummyModel(BaseModel):
    """
    Modèle fictif qui prédit 0 ou 1 au hasard pour chaque bloc.
    Utile pour tester l'intégration de la prédiction.
    """

    def predict(self, vectors: Dict[str, List[float]]) -> Dict[str, int]:
        predictions = {}
        for block_id in vectors:
            predictions[block_id] = random.choice([0, 1])
        return predictions
