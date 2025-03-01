import json
import random
from typing import Tuple

import numpy as np

from core.parsers.BaseMetricsExtractor import BaseMetricsExtractor
from utils.logger_utils import logger


class DeltaMetricsExtractor(BaseMetricsExtractor):
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

    def compare_metrics(self, before_metrics: dict, after_metrics: dict) -> dict:
        """
        Compare les métriques avant et après les changements.
        Retourne :
            - differences : Différences entre les métriques avant et après les changements.
        """
        differences = {}

        for file, before_content in before_metrics.items():
            after_content = after_metrics.get(file, {})

            if "data" not in before_content or "data" not in after_content:
                continue

            before_blocks = {block["block_identifiers"]: block for block in before_content["data"]}
            after_blocks = {block["block_identifiers"]: block for block in after_content["data"]}

            for block_id, before_block in before_blocks.items():
                after_block = after_blocks.get(block_id)

                if not after_block:
                    continue

                block_parts = block_id.split()
                block_type = block_parts[0] if len(block_parts) > 0 else "[Type Inconnu]"
                block_name = block_parts[1] if len(block_parts) > 1 else "[Nom Inconnu]"

                logger.info(f"Comparaison des métriques pour {block_type} {block_name}")
                logger.info(f"Métriques avant : {json.dumps(before_block, indent=4)}")
                logger.info(f"Métriques après : {json.dumps(after_block, indent=4)}")

                diff = {}

                for key in set(before_block.keys()).union(set(after_block.keys())):
                    before_value = before_block.get(key)
                    after_value = after_block.get(key)

                    # Comparaison des valeurs numériques
                    if isinstance(before_value, (int, float)) and isinstance(after_value, (int, float)):
                        if before_value != after_value:
                            diff[key] = after_value - before_value

                    # Comparaison des chaînes de caractères (comme "version")
                    elif isinstance(before_value, str) and isinstance(after_value, str) and before_value != after_value:
                        diff[key] = f"{before_value} → {after_value}"

                if diff:
                    differences[f"{block_type} {block_name}"] = diff

        return differences