import json
import random
from typing import Tuple

import numpy as np

from utils.logger_utils import logger


class TerraformMetricsExtractor:
    """
    Classe pour extraire et transformer les métriques Terraform en un vecteur utilisable pour l'entraînement ML.
    """

    def __init__(self, json_path: str):
        self.json_path = json_path
        self.data = self._load_json()

    def _load_json(self):
        """Charge les métriques Terraform depuis le fichier JSON."""
        try:
            with open(self.json_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {self.json_path} : {e}")
            return {}

    def extract_features(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extrait les métriques essentielles et les transforme en vecteurs utilisables pour ML.
        Retourne :
            - X : Liste des features normalisées.
            - y : Liste des labels (0: non-defect, 1: defect) générés aléatoirement.
        """
        X, y = [], []

        for _, content in self.data.items():
            if "data" not in content:
                continue

            for block in content["data"]:
                features = [
                    block.get("loc", 0),
                    block.get("num_blocks", 0),
                    block.get("num_resources", 0),
                    block.get("num_variables", 0),
                    block.get("numFunctions", 0),
                    block.get("avgMccabeCC", 1.0),
                ]

                X.append(features)
                y.append(random.choice([0, 1]))

        return np.array(X), np.array(y)
