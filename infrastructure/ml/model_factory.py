from infrastructure.ml.base_model import BaseModel
from infrastructure.ml.dummy_model import DummyModel


class ModelFactory:
    @staticmethod
    def get_model(model_type: str) -> BaseModel:
        """
        Retourne une instance de modèle prédictif selon le type spécifié.

        Args:
            model_type (str): Type du modèle (ex: 'dummy', 'sklearn', etc.)

        Returns:
            BaseModel: instance du modèle
        """
        if model_type == "dummy":
            return DummyModel()
        else:
            raise ValueError(f"Modèle non supporté : {model_type}")
