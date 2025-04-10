import pytest

from core.parsers.terraform_parser import TerraformParser


def test_find_block_simple_resource():
    """
    Teste la méthode `find_block` pour vérifier qu'elle extrait correctement un bloc
    Terraform simple à partir de son numéro de ligne.

    Scénario :
        - Un contenu Terraform contenant un bloc `resource` est fourni.
        - La méthode `find_block` est appelée avec une ligne appartenant au bloc.

    Assertions :
        - Vérifie que le bloc retourné contient les attributs attendus (`bucket`, `acl`).
        - Vérifie que le bloc commence et se termine correctement avec `{` et `}`.

    Returns:
        None
    """

    content = """
    resource "aws_s3_bucket" "example" {
    bucket = "mybucket"
    acl    = "private"
    }
    """
    parser = TerraformParser.from_string(content)
    block = parser.find_block(1)
    assert 'resource "aws_s3_bucket" "example"' in block
    assert 'bucket = "mybucket"' in block
    assert 'acl    = "private"' in block
    assert block.strip().endswith("}")


def test_find_block_with_multiline_comments():
    """
    Teste la méthode `find_block` pour vérifier qu'elle gère correctement les blocs
    contenant des commentaires multilignes.

    Scénario :
        - Un contenu Terraform contenant un bloc `resource` avec des commentaires
          multilignes est fourni.
        - La méthode `find_block` est appelée avec une ligne appartenant au bloc.

    Assertions :
        - Vérifie que le bloc retourné contient les attributs attendus (`ami`, `tags`).
        - Vérifie que le nombre d'accolades ouvrantes et fermantes est équilibré.

    Returns:
        None
    """

    content = """
    /* Top-level comment */
    resource "aws_instance" "example" {
    ami           = "ami-123456"
    instance_type = "t2.micro"
    /*
        inside comment
    */
    tags = {
        Name = "Test"
    }
    }
    """

    parser = TerraformParser.from_string(content)
    block = parser.find_block(4)
    assert "aws_instance" in block
    assert "ami" in block
    assert "tags" in block
    assert block.count("{") == block.count("}")


def test_find_blocks_multiple_blocks():
    """
    Teste la méthode `find_blocks` pour vérifier qu'elle extrait plusieurs blocs
    Terraform à partir de plusieurs lignes modifiées.

    Scénario :
        - Un contenu Terraform contenant plusieurs blocs (`resource`, `output`) est fourni.
        - La méthode `find_blocks` est appelée avec une liste de lignes modifiées.

    Assertions :
        - Vérifie que le nombre de blocs retournés correspond au nombre de lignes modifiées.
        - Vérifie que chaque bloc retourné contient les identifiants attendus.

    Returns:
        None
    """

    content = """
    resource "aws_s3_bucket" "a" {
    bucket = "bucket-a"
    }

    resource "aws_s3_bucket" "b" {
    bucket = "bucket-b"
    }

    output "bucket_name" {
    value = "a"
    }
    """

    parser = TerraformParser.from_string(content)
    changed_lines = [1, 5, 9]
    blocks = parser.find_blocks(changed_lines)
    assert len(blocks) == 3
    assert any('aws_s3_bucket" "a"' in b for b in blocks)
    assert any('aws_s3_bucket" "b"' in b for b in blocks)
    assert any('output "bucket_name"' in b for b in blocks)


def test_find_block_out_of_bounds():
    """
    Teste la méthode `find_block` pour vérifier qu'elle retourne une chaîne vide
    lorsqu'une ligne hors des limites est fournie.

    Scénario :
        - Un contenu Terraform contenant un bloc `resource` est fourni.
        - La méthode `find_block` est appelée avec des lignes hors des limites.

    Assertions :
        - Vérifie que la méthode retourne une chaîne vide pour une ligne négative.
        - Vérifie que la méthode retourne une chaîne vide pour une ligne trop grande.

    Returns:
        None
    """

    content = """
    resource "aws_s3_bucket" "x" {
    bucket = "x"
    }
    """

    parser = TerraformParser.from_string(content)
    assert parser.find_block(-1) == ""
    assert parser.find_block(100) == ""


def test_empty_content_raises_error():
    """
    Teste la méthode `from_string` pour vérifier qu'elle lève une exception
    lorsqu'un contenu Terraform vide est fourni.

    Scénario :
        - Un contenu vide est fourni à la méthode `from_string`.

    Assertions :
        - Vérifie que la méthode lève une exception `ValueError` avec un message approprié.

    Returns:
        None
    """
    with pytest.raises(ValueError, match="contenu Terraform fourni est vide"):
        TerraformParser.from_string("")
