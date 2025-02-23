from typing import Dict, List

from infrastructure.adapters.git.git_changes import GitChanges


class DetectTFChanges:
    """Orchestration de la détection des blocs Terraform modifiés."""

    def __init__(self, repo_path: str):
        self.git_changes = GitChanges(repo_path)

    def get_modified_tf_blocks(self, commit_hash: str) -> Dict[str, List[str]]:
        """
        Retourne les blocs Terraform modifiés dans un commit.

        Args:
            commit_hash (str): Le hash du commit à analyser.

        Returns:
            Dict[str, List[str]]: Dictionnaire contenant les fichiers Terraform et leurs blocs modifiés.
        """
        return self.git_changes.get_modified_blocks(commit_hash)
    
    def get_tf_blocks_before_change(self, commit_hash: str) -> Dict[str, List[str]]:
        """
        Retourne les blocs Terraform avant les changements dans un commit.

        Args:
            commit_hash (str): Le hash du commit à analyser.

        Returns:
            Dict[str, List[str]]: Dictionnaire contenant les fichiers Terraform et leurs blocs avant les changements.
        """
        return self.git_changes.get_blocks_before_change(commit_hash)