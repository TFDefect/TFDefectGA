import os
from typing import Dict, List, Tuple

import joblib

from app import config
from infrastructure.ml.base_model import BaseModel
from infrastructure.ml.selected_features_loader import load_selected_features


class SklearnModel(BaseModel):
    """
    Implémentation générique d'un modèle scikit-learn pour la prédiction de défauts Terraform.
    Elle peut être utilisée pour plusieurs types de modèles (LightGBM, Logistic Regression, Naive Bayes, etc.)
    en fournissant dynamiquement le nom du modèle et le chemin vers le fichier .joblib.

    Le fichier .joblib doit contenir un dictionnaire avec :
        - 'model'  : le classificateur entraîné (doit implémenter predict + predict_proba)
        - 'scaler' : le scaler utilisé pour normaliser les données
    """

    def __init__(self, model_name: str, model_path: str):
        # Vérifie que le fichier modèle existe
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modèle non trouvé : {model_path}")

        # Charge le modèle et le scaler depuis le fichier joblib
        bundle = joblib.load(model_path)
        self.model = bundle.get("model")
        self.scaler = bundle.get("scaler")

        # Charge les features sélectionnées pour ce modèle (depuis le fichier CSV associé)
        self.selected_features = load_selected_features(model_name)

        if self.model is None or self.scaler is None:
            raise ValueError(
                "Le fichier joblib doit contenir les clés 'model' et 'scaler'"
            )

    def predict(self, vectors: Dict[str, List[float]]) -> Dict[str, int]:
        """
        Prédit le label (0 ou 1) pour chaque bloc après avoir appliqué le scaler.

        Args:
            vectors (Dict[str, List[float]]): Vecteurs de caractéristiques par bloc

        Returns:
            Dict[str, int]: Dictionnaire {block_id: 0|1}
        """
        block_ids = list(vectors.keys())
        X = list(vectors.values())

        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)

        return {block_id: int(pred) for block_id, pred in zip(block_ids, predictions)}

    def predict_with_confidence(
        self, vectors: Dict[str, List[float]]
    ) -> Dict[str, Tuple[int, float]]:
        """
        Prédit le label + la probabilité pour chaque bloc.

        Returns:
            Dict[str, Tuple[int, float]]: {block_id: (label, proba)}
        """
        block_ids = list(vectors.keys())
        X = list(vectors.values())

        X_scaled = self.scaler.transform(X)
        predicted_probs = self.model.predict_proba(X_scaled)

        return {
            block_id: (int(proba[1] >= 0.5), round(proba[1], 4))
            for block_id, proba in zip(block_ids, predicted_probs)
        }

    def describe(self) -> str:
        """
        Retourne une description textuelle du modèle et de son scaler.

        Returns:
            str: Description
        """
        model_type = type(self.model).__name__
        scaler_type = type(self.scaler).__name__

        if hasattr(self.model, "n_features_in_"):
            num_features = self.model.n_features_in_
        elif hasattr(self.scaler, "scale_"):
            num_features = len(self.scaler.scale_)
        else:
            num_features = "?"

        return f"🧠 Modèle : {model_type} | 🔧 Scaler : {scaler_type} | 🔁 Features : {num_features}"
