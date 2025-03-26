import pytest

from core.parsers.terraform_parser import TerraformParser


def test_find_block_simple_resource():
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
    content = """
resource "aws_s3_bucket" "x" {
  bucket = "x"
}
"""
    parser = TerraformParser.from_string(content)
    assert parser.find_block(-1) == ""
    assert parser.find_block(100) == ""


def test_empty_content_raises_error():
    with pytest.raises(ValueError, match="contenu Terraform fourni est vide"):
        TerraformParser.from_string("")
