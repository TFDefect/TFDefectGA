from unittest.mock import MagicMock, patch

from core.use_cases.detect_tf_changes import DetectTFChanges


@patch("core.use_cases.detect_tf_changes.GitChanges")
def test_get_modified_tf_blocks_returns_git_results(mock_git_cls):
    mock_git_instance = MagicMock()
    mock_git_instance.get_modified_blocks.return_value = {
        "main.tf": ['resource "aws_s3_bucket" "mybucket" { ... }']
    }
    mock_git_cls.return_value = mock_git_instance

    detector = DetectTFChanges(repo_path=".")
    result = detector.get_modified_tf_blocks()

    mock_git_cls.assert_called_once_with(".")
    mock_git_instance.get_modified_blocks.assert_called_once()

    assert "main.tf" in result
    assert isinstance(result["main.tf"], list)
