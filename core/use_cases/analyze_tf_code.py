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

    def compare_metrics(self, before_metrics: Dict[str, dict], after_metrics: Dict[str, dict]) -> Dict[str, dict]:
        """
        Compare les métriques avant et après les changements.

        Args:
            before_metrics (Dict[str, dict]): Métriques avant les changements.
            after_metrics (Dict[str, dict]): Métriques après les changements.

        Returns:
            Dict[str, dict]: Différences entre les métriques avant et après les changements.
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
