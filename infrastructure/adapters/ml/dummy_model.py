import numpy as np
from sklearn.dummy import DummyClassifier

from infrastructure.adapters.ml.base_model import BaseMLModel
from utils.logger_utils import logger


class DummyMLModel(BaseMLModel):
    """Modèle ML naïf basé sur un DummyClassifier."""

    def __init__(self, strategy="stratified", random_state=42):
        self.model = DummyClassifier(strategy=strategy, random_state=random_state)

    def predict_defects(self, X: np.ndarray, num_samples: int) -> list:
        """Retourne des prédictions aléatoires pour chaque bloc Terraform analysé."""

        # Fake labels pour DummyClassifier (0: sans défaut, 1: défectueux)
        y_dummy = np.random.choice([0, 1], size=num_samples)

        # Entraînement fictif du modèle
        self.model.fit(X, y_dummy)

        predictions = self.model.predict(X)

        # Conversion des prédictions
        labels = [
            "🐞 Défectueux" if pred == 1 else "✅ Sans défaut" for pred in predictions
        ]

        logger.info(f"Prédictions ML générées : {labels}")
        return labels
