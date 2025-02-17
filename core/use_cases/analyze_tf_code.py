import json
from typing import Dict, List

from core.parsers.metrics_extractor import TerraformMetricsExtractor
from infrastructure.adapters.external_tools.terra_metrics import \
    TerraMetricsAdapter
from infrastructure.adapters.ml.dummy_model import DummyMLModel
from utils.logger_utils import logger


class AnalyzeTFCode:
    """Orchestration de l'analyse des blocs Terraform modifiés et prédiction de défauts."""

    def __init__(self, jar_path: str, metrics_path: str, ml_model=None):
        self.terra_metrics = TerraMetricsAdapter(jar_path)
        self.metrics_path = metrics_path
        self.ml_model = ml_model or DummyMLModel()

    def analyze_blocks(self, modified_blocks: Dict[str, List[str]]) -> Dict[str, dict]:
        """
        Analyse les blocs Terraform modifiés avec TerraMetrics et applique un modèle ML de détection de défauts.

        Args:
            modified_blocks (Dict[str, List[str]]): Blocs Terraform modifiés.

        Returns:
            Dict[str, dict]: Résultats de l'analyse TerraMetrics avec prédictions de défauts.
        """
        if not modified_blocks:
            return {}

        # Exécution de TerraMetrics pour obtenir les métriques
        analysis_results = self.terra_metrics.analyze_blocks(modified_blocks)

        with open(self.metrics_path, "w") as f:
            json.dump(analysis_results, f, indent=4)

        logger.info(
            f"`output.json` mis à jour avec {len(analysis_results)} fichiers analysés."
        )

        # Comptage du nombre de blocs analysés
        num_blocks = sum(
            len(content.get("data", [])) for content in analysis_results.values()
        )
        logger.info(f"Nombre de blocs Terraform analysés : {num_blocks}")

        # Extraction des métriques pour le modèle ML
        extractor = TerraformMetricsExtractor(self.metrics_path)
        X, _ = extractor.extract_features()

        # Vérification des dimensions
        num_features = X.shape[0]
        logger.info(f"Nombre de métriques extraites : {num_features}")

        if num_features != num_blocks:
            logger.error(
                f"Erreur : le nombre de métriques extraites ({num_features}) ne correspond pas au nombre de blocs Terraform analysés ({num_blocks})."
            )
            raise ValueError(
                "Les dimensions des prédictions et des blocs analysés ne correspondent pas."
            )

        # Prédiction des défauts via le modèle ML
        predictions = self.ml_model.predict_defects(X, num_blocks)

        # Ajout des prédictions aux résultats existants
        index = 0
        for _, content in analysis_results.items():
            if "data" in content:
                for block in content["data"]:
                    block["defect_prediction"] = predictions[index]
                    index += 1

        return analysis_results
