import pytest
from core.use_cases.detect_tf_changes import DetectTFChanges

# Dummy class to simulate behavior of GitChanges used within DetectTFChanges.
class DummyGitChanges:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_modified_blocks(self, commit_hash: str):
        if commit_hash == "commit_with_changes":
            return {
                "main.tf": [
                    'resource "aws_instance" "example" {\n'
                    '  ami = "ami-123456"\n'
                    '  instance_type = "t2.micro"\n'
                    '}\n'
                ],
                "variables.tf": ["variable \"instance_type\" {}"]
            }
        elif commit_hash == "commit_empty":
            return {}
        elif commit_hash == "commit_error":
            raise Exception("dummy error")
        else:
            # Default dummy return for any other commit hash
            return {}

# Fixture to supply a dummy repository path (using tmp_path to simulate a repo folder)
@pytest.fixture
def dummy_repo_path(tmp_path):
    return str(tmp_path)

def test_get_modified_tf_blocks_with_changes(monkeypatch, dummy_repo_path):
    """
    Test that get_modified_tf_blocks returns the expected blocks
    when the GitChanges dependency reports modified Terraform files.
    """
    # Monkeypatch the GitChanges class used in DetectTFChanges with our dummy version.
    monkeypatch.setattr("core.use_cases.detect_tf_changes.GitChanges", DummyGitChanges)
    detect_tf = DetectTFChanges(dummy_repo_path)
    commit_hash = "commit_with_changes"
    result = detect_tf.get_modified_tf_blocks(commit_hash)
    expected = {
        "main.tf": [
            'resource "aws_instance" "example" {\n'
            '  ami = "ami-123456"\n'
            '  instance_type = "t2.micro"\n'
            '}\n'
        ],
        "variables.tf": ["variable \"instance_type\" {}"]
    }
    assert result == expected

def test_get_modified_tf_blocks_empty(monkeypatch, dummy_repo_path):
    """
    Test that get_modified_tf_blocks returns an empty dictionary
    when no Terraform changes are reported.
    """
    monkeypatch.setattr("core.use_cases.detect_tf_changes.GitChanges", DummyGitChanges)
    detect_tf = DetectTFChanges(dummy_repo_path)
    commit_hash = "commit_empty"
    result = detect_tf.get_modified_tf_blocks(commit_hash)
    assert result == {}

def test_get_modified_tf_blocks_exception(monkeypatch, dummy_repo_path):
    """
    Test that get_modified_tf_blocks propagates exceptions raised by the GitChanges dependency.
    """
    monkeypatch.setattr("core.use_cases.detect_tf_changes.GitChanges", DummyGitChanges)
    detect_tf = DetectTFChanges(dummy_repo_path)
    commit_hash = "commit_error"
    with pytest.raises(Exception, match="dummy error"):
        detect_tf.get_modified_tf_blocks(commit_hash)
