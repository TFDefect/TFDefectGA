from unittest.mock import MagicMock

from core.use_cases.analyze_tf_code import AnalyzeTFCode


def test_analyze_blocks_returns_expected_result():
    mock_extractor = MagicMock()
    mock_extractor.extract_metrics.return_value = {
        "main.tf": {"lines": 12, "complexity": 3}
    }

    analyzer = AnalyzeTFCode(repo_path=".", metrics_extractor=mock_extractor)

    fake_blocks = {
        "main.tf": ['resource "aws_instance" "example" {\n  ami = "ami-123"\n}']
    }

    result = analyzer.analyze_blocks(fake_blocks)

    mock_extractor.extract_metrics.assert_called_once_with(fake_blocks)
    assert result == {"main.tf": {"lines": 12, "complexity": 3}}
