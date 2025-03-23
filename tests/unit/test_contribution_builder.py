from unittest.mock import MagicMock, patch

from core.parsers.contribution_builder import (get_contribution,
                                               get_previous_contributions)


@patch("core.parsers.contribution_builder.Repository")
def test_get_contribution_success(mock_repo):
    # Configuration du mock de commit
    mock_commit = MagicMock()
    mock_commit.author.name = "alice"
    mock_commit.hash = "abc123"
    mock_commit.committer_date = "2025-03-23"
    mock_commit.author.total = 3

    mock_file = MagicMock()
    mock_file.new_path = "main.tf"
    mock_commit.modified_files = [mock_file]

    mock_repo.return_value.traverse_commits.return_value = iter([mock_commit])

    result = get_contribution(".", "main.tf", "resource.aws_s3_bucket.mybucket")

    assert result["author"] == "alice"
    assert result["file"] == "main.tf"
    assert result["block_identifiers"] == "resource.aws_s3_bucket.mybucket"
    assert result["isResource"] == 1
    assert result["isData"] == 0
    assert result["block"] == "resource"
    assert result["block_id"] == "resource.aws_s3_bucket.mybucket"


@patch("core.parsers.contribution_builder.extract_block_identifier")
@patch("core.parsers.contribution_builder.TerraformParser")
@patch("core.parsers.contribution_builder.Repository")
def test_get_previous_contributions_success(
    mock_repo, mock_parser_cls, mock_extract_id
):
    # Mock du bloc extrait
    mock_extract_id.return_value = "aws_s3_bucket.mybucket"

    # Faux contenu Terraform
    mock_parser = MagicMock()
    mock_parser.find_blocks.return_value = [
        'resource "aws_s3_bucket" "mybucket" { ... }'
    ]
    mock_parser.lines = ["..."] * 10
    mock_parser_cls.from_string.return_value = mock_parser

    # Faux commit git
    mock_commit = MagicMock()
    mock_commit.author.name = "alice"
    mock_commit.hash = "abc123"
    mock_commit.committer_date = "2025-03-20"
    mock_commit.author.total = 5

    mock_file = MagicMock()
    mock_file.new_path = "main.tf"
    mock_file.source_code = 'resource "aws_s3_bucket" "mybucket" { ... }'

    mock_commit.modified_files = [mock_file]
    mock_repo.return_value.traverse_commits.return_value = [mock_commit]

    # Historique des défauts simulé
    defect_history = {
        "main.tf::aws_s3_bucket.mybucket": [{"commit": "abc123", "fault_prone": 1}]
    }

    results = get_previous_contributions(
        ".", "main.tf", "aws_s3_bucket.mybucket", defect_history
    )

    assert len(results) == 1
    result = results[0]

    assert result["author"] == "alice"
    assert result["file"] == "main.tf"
    assert result["block_identifiers"] == "aws_s3_bucket.mybucket"
    assert result["fault_prone"] == 1
    assert result["block"] == "aws_s3_bucket"
    assert result["block_id"] == "aws_s3_bucket.mybucket"
