import pytest
from git import Repo
from infrastructure.adapters.git.git_adapter import GitAdapter


@pytest.fixture
def valid_git_repo(tmp_path):
    """
    Create a temporary Git repository with an initial commit.
    """
    repo = Repo.init(tmp_path)
    # Create a dummy file and commit it to establish HEAD.
    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("dummy content")
    repo.index.add([str(dummy_file)])
    repo.index.commit("Initial commit")
    return repo


def test_verify_git_repo_valid(tmp_path, monkeypatch, valid_git_repo):
    """
    Test that verify_git_repo does not raise an exception when executed
    inside a valid Git repository that has at least one commit.
    """
    monkeypatch.chdir(tmp_path)
    # Should not exit since HEAD is properly set.
    GitAdapter.verify_git_repo()


def test_verify_git_repo_invalid(tmp_path, monkeypatch):
    """
    Test that verify_git_repo raises SystemExit when executed in a directory
    that is not a Git repository.
    """
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit):
        GitAdapter.verify_git_repo()


def test_verify_git_repo_nested(tmp_path, monkeypatch, valid_git_repo):
    """
    Test that verify_git_repo correctly finds the Git repository when the current
    directory is nested within the repository.
    """
    # Create a nested directory inside the repository.
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    monkeypatch.chdir(nested_dir)
    # Should locate the repository by searching parent directories.
    GitAdapter.verify_git_repo()
