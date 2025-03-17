import re
import pytest
from pathlib import Path
from core.parsers.terraform_parser import TerraformParser


@pytest.fixture
def simple_tf_file(tmp_path: Path) -> Path:
    content = (
        'resource "aws_instance" "example" {\n'
        '  ami = "ami-123456"\n'
        '  instance_type = "t2.micro"\n'
        '}\n'
    )
    file_path = tmp_path / "simple.tf"
    file_path.write_text(content)
    return file_path


def test_empty_file(tmp_path: Path):
    """Test that an empty Terraform file raises a ValueError on initialization."""
    empty_file = tmp_path / "empty.tf"
    empty_file.write_text("")
    with pytest.raises(ValueError, match="vide"):
        TerraformParser(str(empty_file))


def test_find_block_invalid_index(simple_tf_file: Path):
    """Test that find_block returns an empty string when the index is out of range."""
    parser = TerraformParser(str(simple_tf_file))
    # Negative index should return an empty string.
    assert parser.find_block(-1) == ""
    # Index equal to the number of lines should return an empty string.
    assert parser.find_block(len(parser.lines)) == ""


def test_find_block_simple(simple_tf_file: Path):
    """Test extraction of a simple Terraform block."""
    parser = TerraformParser(str(simple_tf_file))
    # Pick a line inside the block (line index 1).
    block = parser.find_block(1)
    expected_block = (
        'resource "aws_instance" "example" {\n'
        '  ami = "ami-123456"\n'
        '  instance_type = "t2.micro"\n'
        '}\n'
    )
    assert block == expected_block


def test_find_block_with_multiline_comment(tmp_path: Path):
    """Test that the parser correctly handles multi-line comments inside a block."""
    content = (
        'resource "aws_instance" "example" {\n'
        '  /* This is a\n'
        '  multi-line comment */\n'
        '  ami = "ami-123456"\n'
        '}\n'
    )
    tf_file = tmp_path / "multiline.tf"
    tf_file.write_text(content)
    parser = TerraformParser(str(tf_file))
    # Choose a line within the block (line index 3, the "ami" line).
    block = parser.find_block(3)
    expected_block = (
        'resource "aws_instance" "example" {\n'
        '  /* This is a\n'
        '  multi-line comment */\n'
        '  ami = "ami-123456"\n'
        '}\n'
    )
    assert block == expected_block


def test_find_block_no_matching_keyword(tmp_path: Path):
    """
    Test the behavior when the file does not contain any Terraform block keywords.
    The parser should default to using the first line (after decrementing).
    """
    content = (
        'some random text\n'
        'another line\n'
        '{ a brace }\n'
    )
    tf_file = tmp_path / "non_tf.tf"
    tf_file.write_text(content)
    parser = TerraformParser(str(tf_file))
    # For changed_line=1, the parser will decrement to line 0.
    block = parser.find_block(1)
    expected_block = "some random text\n"
    assert block == expected_block


def test_find_block_bounds_index_error(simple_tf_file: Path):
    """Test that _find_block_bounds raises an IndexError when the given index is out of range."""
    parser = TerraformParser(str(simple_tf_file))
    with pytest.raises(IndexError, match="hors des limites"):
        # Directly calling the private method with an out-of-range index.
        parser._find_block_bounds(len(parser.lines))
