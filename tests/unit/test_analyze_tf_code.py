import json
import numpy as np
import pytest
from pathlib import Path

from core.use_cases.analyze_tf_code import AnalyzeTFCode
from core.parsers.BaseMetricsExtractor import BaseMetricsExtractor
from core.parsers.metrics_extractor import TerraformMetricsExtractor


# ----- Fake Extractors & ML Model for Testing ----- #

class FakeMetricsExtractorSuccess(BaseMetricsExtractor):
    """
    Fake metrics extractor that returns a fixed, valid analysis result.
    Total blocks: 1 (from file1.tf) + 1 (from file2.tf) = 2.
    """
    def extract_metrics(self, modified_blocks):
        return {
            "file1.tf": {"data": [
                {
                    "loc": 10,
                    "num_blocks": 2,
                    "num_resources": 1,
                    "num_variables": 3,
                    "numFunctions": 1,
                    "avgMccabeCC": 2.0,
                }
            ]},
            "file2.tf": {"data": [
                {
                    "loc": 20,
                    "num_blocks": 4,
                    "num_resources": 2,
                    "num_variables": 6,
                    "numFunctions": 1,
                    "avgMccabeCC": 3.0,
                }
            ]},
        }


class FakeMetricsExtractorMismatch(BaseMetricsExtractor):
    """
    Fake metrics extractor that returns a result with two blocks
    (from a single file) to be used for dimension mismatch testing.
    """
    def extract_metrics(self, modified_blocks):
        return {
            "file1.tf": {"data": [
                {
                    "loc": 10,
                    "num_blocks": 2,
                    "num_resources": 1,
                    "num_variables": 3,
                    "numFunctions": 1,
                    "avgMccabeCC": 2.0,
                },
                {
                    "loc": 15,
                    "num_blocks": 3,
                    "num_resources": 2,
                    "num_variables": 4,
                    "numFunctions": 1,
                    "avgMccabeCC": 2.5,
                }
            ]}
        }


class FakeMLModel:
    """
    Fake ML model that returns a fixed prediction for each block.
    """
    def predict_defects(self, X: np.ndarray, num_samples: int) -> list:
        return ["Predicted"] * num_samples


# ----- Test Cases ----- #

def test_empty_modified_blocks(tmp_path: Path):
    """
    Test that analyze_blocks returns an empty dict when no modified blocks are provided.
    """
    fake_extractor = FakeMetricsExtractorSuccess()
    fake_ml_model = FakeMLModel()
    metrics_file = tmp_path / "output.json"

    analyzer = AnalyzeTFCode(
        jar_path="dummy.jar",
        metrics_path=str(metrics_file),
        metrics_extractor=fake_extractor,
        ml_model=fake_ml_model,
    )
    result = analyzer.analyze_blocks({})

    assert result == {}


def test_analyze_blocks_success(tmp_path: Path):
    """
    Test a successful analysis:
    - The fake extractor returns a fixed JSON structure.
    - The temporary file is written.
    - Each Terraform block in the result has a defect prediction appended.
    """
    fake_extractor = FakeMetricsExtractorSuccess()
    fake_ml_model = FakeMLModel()
    metrics_file = tmp_path / "output.json"
    modified_blocks = {"dummy.tf": ["irrelevant block content"]}

    analyzer = AnalyzeTFCode(
        jar_path="dummy.jar",
        metrics_path=str(metrics_file),
        metrics_extractor=fake_extractor,
        ml_model=fake_ml_model,
    )
    result = analyzer.analyze_blocks(modified_blocks)

    # Verify that the metrics file was written correctly.
    assert metrics_file.exists()
    with open(metrics_file, "r") as f:
        file_content = json.load(f)
    expected = fake_extractor.extract_metrics(modified_blocks)
    assert file_content == expected

    # Verify that each block now includes the defect prediction.
    for file_data in result.values():
        for block in file_data.get("data", []):
            assert block.get("defect_prediction") == "Predicted"


def test_analyze_blocks_dimension_mismatch(tmp_path: Path, monkeypatch):
    """
    Test that a ValueError is raised when the number of features extracted
    does not match the number of Terraform blocks analyzed.
    This is simulated by monkeypatching TerraformMetricsExtractor.extract_features.
    """
    fake_extractor = FakeMetricsExtractorMismatch()
    fake_ml_model = FakeMLModel()
    metrics_file = tmp_path / "output.json"
    modified_blocks = {"dummy.tf": ["block content doesn't matter"]}

    # Monkeypatch extract_features to return an array with only one row,
    # while the extractor returns 2 blocks (dimension mismatch).
    def fake_extract_features(self):
        return np.array([[1, 2, 3, 4, 5, 6]]), np.array([0])
    monkeypatch.setattr(
        TerraformMetricsExtractor, "extract_features", fake_extract_features
    )

    analyzer = AnalyzeTFCode(
        jar_path="dummy.jar",
        metrics_path=str(metrics_file),
        metrics_extractor=fake_extractor,
        ml_model=fake_ml_model,
    )

    with pytest.raises(ValueError, match="Les dimensions des prédictions et des blocs analysés ne correspondent pas."):
        analyzer.analyze_blocks(modified_blocks)
