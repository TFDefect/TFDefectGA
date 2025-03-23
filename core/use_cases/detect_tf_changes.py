from typing import Dict, List

from infrastructure.git.git_changes import GitChanges


class DetectTFChanges:
    """Orchestration de la détection des blocs Terraform modifiés."""

    def __init__(self, repo_path: str = "."):
        """
        Initialise la classe en configurant l'analyse des changements Git.

        Args:
            repo_path (str, optional): Chemin du dépôt Git (par défaut, le répertoire courant).
        """
        self.git_changes = GitChanges(repo_path)

    def get_modified_tf_blocks(self) -> Dict[str, List[str]]:
        """
        Récupère les blocs Terraform modifiés à partir du dernier commit (pour CodeMetrics).

        Returns:
            Dict[str, List[str]]: Dictionnaire contenant les fichiers Terraform et leurs blocs modifiés.
        """
        return self.git_changes.get_modified_blocks()

    def get_changed_blocks(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Récupère les blocs Terraform avant et après modification (pour DeltaMetrics).

        Returns:
            Dict[str, Dict[str, List[str]]]: Dictionnaire contenant les fichiers Terraform,
                                             avec leurs blocs avant et après modification.
        """
        return self.git_changes.get_changed_blocks()
