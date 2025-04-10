from unittest.mock import MagicMock

from core.use_cases.analyze_tf_code import AnalyzeTFCode


def test_analyze_blocks_returns_expected_result():
    """
    Teste la méthode `analyze_blocks` de la classe AnalyzeTFCode.

    Ce test vérifie que la méthode `analyze_blocks` retourne les métriques attendues
    pour des blocs Terraform fictifs en utilisant un extracteur de métriques simulé.

    Scénario :
        - Un mock de l'extracteur de métriques est configuré pour retourner des métriques spécifiques.
        - La méthode `analyze_blocks` est appelée avec des blocs Terraform fictifs.
        - Les résultats retournés sont comparés aux métriques attendues.

    Assertions :
        - Vérifie que la méthode `extract_metrics` du mock est appelée avec les blocs fournis.
        - Vérifie que le résultat retourné par `analyze_blocks` correspond aux métriques attendues.

    Returns:
        None
    """
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
