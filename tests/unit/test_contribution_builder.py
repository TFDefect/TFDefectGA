from unittest.mock import MagicMock, patch

from core.parsers.contribution_builder import (get_contribution,
                                               get_previous_contributions)


@patch("core.parsers.contribution_builder.Repository")
def test_get_contribution_success(mock_repo):
    """
    Teste la fonction `get_contribution` pour vérifier qu'elle retourne les informations
    correctes sur un bloc Terraform donné.

    Scénario :
        - Un commit fictif est simulé avec un auteur, un hash, une date et un fichier modifié.
        - La fonction `get_contribution` est appelée avec un chemin de dépôt, un fichier Terraform,
          et un identifiant de bloc.
        - Les résultats retournés sont comparés aux valeurs attendues.

    Assertions :
        - Vérifie que l'auteur du commit est correctement identifié.
        - Vérifie que le fichier modifié est correctement identifié.
        - Vérifie que l'identifiant du bloc est correctement retourné.
        - Vérifie les propriétés du bloc, telles que `isResource` et `isData`.

    Returns:
        None
    """
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
    """
    Teste la fonction `get_previous_contributions` pour vérifier qu'elle retourne
    correctement les contributions précédentes pour un bloc Terraform donné.

    Scénario :
        - Un bloc Terraform fictif est simulé avec un identifiant et un contenu.
        - Un commit git fictif est simulé avec un auteur, un hash, une date et un fichier modifié.
        - Un historique des défauts est fourni pour le bloc.
        - La fonction `get_previous_contributions` est appelée avec un chemin de dépôt,
          un fichier Terraform, un identifiant de bloc et l'historique des défauts.
        - Les résultats retournés sont comparés aux valeurs attendues.

    Assertions :
        - Vérifie que le nombre de contributions retournées est correct.
        - Vérifie que l'auteur du commit est correctement identifié.
        - Vérifie que le fichier modifié est correctement identifié.
        - Vérifie que l'identifiant du bloc est correctement retourné.
        - Vérifie que la propriété `fault_prone` est correctement associée au bloc.

    Returns:
        None
    """
    mock_extract_id.return_value = "aws_s3_bucket.mybucket"

    mock_parser = MagicMock()
    mock_parser.find_blocks.return_value = [
        'resource "aws_s3_bucket" "mybucket" { ... }'
    ]
    mock_parser.lines = ["..."] * 10
    mock_parser_cls.from_string.return_value = mock_parser

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
