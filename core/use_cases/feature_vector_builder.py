from typing import Dict, List

from core.parsers.metrics_extractor_factory import MetricsExtractorFactory
from core.use_cases.detect_tf_changes import DetectTFChanges


def normalize_block_identifier(block_str: str) -> str:
    """
    Normalise un identifiant de bloc pour qu'il soit cohérent entre tous les extracteurs.
    Exemple : "resource aws_s3_bucket my_bucket" -> "aws_s3_bucket.my_bucket"
    """
    if block_str.startswith("resource") or block_str.startswith("data"):
        parts = block_str.split()
        if len(parts) >= 3:
            return f"{parts[1]}.{parts[2]}"
    elif block_str.startswith("terraform"):
        return "terraform"
    return block_str.replace(" ", ".")


class FeatureVectorBuilder:
    """
    Construit des vecteurs de caractéristiques pour chaque bloc Terraform modifié
    en combinant les métriques codemetrics, delta et process.
    """

    def __init__(self, repo_path: str, terrametrics_jar_path: str):
        self.repo_path = repo_path
        self.terrametrics_jar_path = terrametrics_jar_path

        # Initialisation des extracteurs
        self.code_extractor = MetricsExtractorFactory.get_extractor(
            "codemetrics", self.terrametrics_jar_path
        )
        self.delta_extractor = MetricsExtractorFactory.get_extractor(
            "delta", self.terrametrics_jar_path
        )
        self.process_extractor = MetricsExtractorFactory.get_extractor(
            "process", self.terrametrics_jar_path
        )

    def build_vectors(self) -> Dict[str, List[float]]:
        """
        Construit un vecteur de caractéristiques pour chaque bloc modifié.

        Returns:
            Dict[str, List[float]]: Mapping block_id -> vecteur de caractéristiques (features)
        """
        detect = DetectTFChanges(self.repo_path)

        blocks_for_code_and_process = detect.get_modified_tf_blocks()
        blocks_for_delta = detect.get_changed_blocks()

        # Extraction des métriques
        code_metrics_raw = self.code_extractor.extract_metrics(
            blocks_for_code_and_process
        )
        delta_metrics_raw = self.delta_extractor.extract_metrics(blocks_for_delta)
        process_metrics_raw = self.process_extractor.extract_metrics(
            blocks_for_code_and_process
        )

        # Reformatage pour codemetrics
        code_by_block_id = {}
        for file_path, content in code_metrics_raw.items():
            for block in content.get("data", []):
                block_id = normalize_block_identifier(block["block_identifiers"])
                full_id = f"{file_path}::{block_id}"
                code_by_block_id[full_id] = block

        # Reformatage pour delta
        delta_by_block_id = {}
        for file_path, file_metrics in delta_metrics_raw.items():
            for block_name, metrics in file_metrics.items():
                block_id = normalize_block_identifier(block_name)
                full_id = f"{file_path}::{block_id}"
                delta_by_block_id[full_id] = metrics

        # Reformatage pour process
        process_by_block_id = {}
        for full_id, metrics in process_metrics_raw.items():
            file_path, raw_block_id = full_id.split("::", 1)
            normalized_id = normalize_block_identifier(raw_block_id)
            full_normalized_id = f"{file_path}::{normalized_id}"
            process_by_block_id[full_normalized_id] = metrics

        # Fusion des clés
        all_block_ids = (
            set(code_by_block_id) | set(delta_by_block_id) | set(process_by_block_id)
        )

        # Construction des vecteurs finaux
        vectors = {}
        for block_id in all_block_ids:
            vector = []
            for source in [code_by_block_id, delta_by_block_id, process_by_block_id]:
                metrics = source.get(block_id, {})
                for key in sorted(metrics):
                    value = metrics[key]
                    if isinstance(value, (int, float)):
                        vector.append(value)
            vectors[block_id] = vector

        return vectors
