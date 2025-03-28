from infrastructure.ml.base_model import BaseModel
from infrastructure.ml.dummy_model import DummyModel
from infrastructure.ml.random_forest_model import RandomForestModel


class ModelFactory:
    @staticmethod
    def get_model(model_type: str) -> BaseModel:
        """
        Retourne une instance de modèle prédictif selon le type spécifié.

        Args:
            model_type (str): Type du modèle (ex: 'dummy', 'randomforest', etc.)

        Returns:
            BaseModel: instance du modèle
        """
        if model_type == "dummy":
            return DummyModel()
        elif model_type == "randomforest":
            return RandomForestModel()
        else:
            raise ValueError(f"Modèle non supporté : {model_type}")
