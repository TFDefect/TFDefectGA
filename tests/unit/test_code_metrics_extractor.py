from unittest.mock import MagicMock, patch

from core.parsers.code_metrics_extractor import CodeMetricsExtractor


@patch("core.parsers.code_metrics_extractor.CodeMetricsExtractor._cleanup_temp_files")
@patch("core.parsers.code_metrics_extractor.open", create=True)
@patch("core.parsers.code_metrics_extractor.os.path.exists", return_value=True)
@patch("core.parsers.code_metrics_extractor.CodeMetricsExtractor._run_terrametrics")
@patch("core.parsers.code_metrics_extractor.CodeMetricsExtractor._create_temp_files")
def test_extract_metrics_success(
    mock_create_temp,
    mock_run_terrametrics,
    mock_exists,
    mock_open_file,
    mock_cleanup,
):
    """
    Teste la méthode `extract_metrics` de la classe CodeMetricsExtractor.

    Ce test simule les dépendances internes de la classe pour vérifier que la méthode
    `extract_metrics` retourne les métriques attendues pour des blocs Terraform fictifs.

    Scénario :
        - Les méthodes internes de CodeMetricsExtractor sont remplacées par des mocks.
        - Un fichier temporaire contenant des métriques simulées est créé.
        - La méthode `extract_metrics` est appelée avec des blocs Terraform modifiés.
        - Les résultats retournés sont comparés aux métriques simulées.

    Assertions :
        - Vérifie que le résultat contient les métriques pour le fichier "main.tf".
        - Vérifie que les métriques retournées correspondent aux données simulées.
        - Vérifie que la méthode `_run_terrametrics` est appelée une fois.
        - Vérifie que la méthode `_cleanup_temp_files` est appelée une fois.

    Returns:
        None
    """
    mock_open_file.return_value.__enter__.return_value.read.return_value = (
        '{"data": "ok"}'
    )
    mock_open_file.return_value.__enter__.return_value = MagicMock(
        read=MagicMock(return_value='{"data": "ok"}')
    )

    mock_create_temp.return_value = ("tmp.tf", "tmp.json")

    extractor = CodeMetricsExtractor(jar_path="fake_path.jar")
    modified_blocks = {
        "main.tf": ['resource "aws_instance" "example" {\n  ami = "ami-123456"\n}']
    }

    result = extractor.extract_metrics(modified_blocks)

    assert "main.tf" in result
    assert result["main.tf"] == {"data": "ok"}
    mock_run_terrametrics.assert_called_once()
    mock_cleanup.assert_called_once()
