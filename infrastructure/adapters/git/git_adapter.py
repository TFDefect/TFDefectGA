import subprocess
from typing import Dict, List, Tuple

from git import GitCommandError, Repo

from utils.logger_utils import logger


class GitAdapter:
    """Service centralisé pour les opérations Git."""

    def __init__(self, repo_path: str = None):
        """
        Initialise le service Git et vérifie le dépôt.

        Args:
            repo_path (str, optional): Chemin vers le dépôt Git. Si non fourni,
                                       utilise le dépôt local trouvé via les répertoires parents.
        """
        try:
            self.repo = Repo(
                repo_path or Repo(search_parent_directories=True).working_tree_dir
            )
        except GitCommandError:
            logger.error("ERREUR : Git n'est pas correctement initialisé.")
            exit(1)

    @staticmethod
    def verify_git_repo():
        """
        Vérifie que Git est bien initialisé et accessible.

        Cette méthode exécute la commande `git rev-parse HEAD` pour obtenir le hash du commit HEAD.
        Si la commande réussit, cela signifie que Git est correctement configuré.
        """
        try:
            commit_hash = (
                subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
            )
            logger.info(f"Git est bien initialisé. HEAD : {commit_hash}")
        except subprocess.CalledProcessError:
            logger.error("ERREUR : Git n'est pas correctement initialisé.")
            exit(1)

    def get_modified_files(self, commit_hash: str) -> List[Tuple[str, str]]:
        """
        Récupère la liste des fichiers `.tf` modifiés ou supprimés dans un commit.

        Args:
            commit_hash (str): Le hash du commit pour lequel récupérer les fichiers modifiés.

        Returns:
            List[Tuple[str, str]]: Une liste de tuples contenant le chemin du fichier et son statut.
                                   Le statut peut être "modified" ou "deleted".
        """
        commit = self.repo.commit(commit_hash)
        parent_commit = commit.parents[0] if commit.parents else None
        modified_files = []

        if parent_commit:
            diffs = parent_commit.diff(commit)

            for diff in diffs:
                status = "deleted" if diff.deleted_file else "modified"
                if diff.a_path.endswith(".tf"):
                    modified_files.append((diff.a_path, status))

        return modified_files

    def get_changed_lines(
        self, commit_hash: str, file_path: str
    ) -> Dict[int, Tuple[str, str]]:
        """
        Récupère les lignes modifiées avec leur contenu et leur type de modification.

        Args:
            commit_hash (str): Le hash du commit pour lequel récupérer les lignes modifiées.
            file_path (str): Le chemin du fichier pour lequel récupérer les lignes modifiées.

        Returns:
            Dict[int, Tuple[str, str]]: Un dictionnaire où la clé est le numéro de ligne et la valeur
                                        est un tuple contenant le type de modification ("added" ou "removed")
                                        et le contenu de la ligne.
        """
        commit = self.repo.commit(commit_hash)
        if not commit.parents:
            return {}

        try:
            commit.tree[file_path]
        except KeyError:
            logger.error(f"Fichier introuvable dans ce commit : {file_path}")
            return {}

        diff_output = self.repo.git.diff(
            commit.parents[0], commit, file_path, unified=0, diff_filter="ACMR"
        ).splitlines()
        changed_lines = {}
        current_line = None

        for line in diff_output:
            if line.startswith("@@"):
                parts = line.split(" ")
                if len(parts) > 2 and parts[2].startswith("+"):
                    start_line = int(parts[2][1:].split(",")[0])
                    current_line = start_line
            elif line.startswith("+") and not line.startswith("+++"):
                if current_line is not None:
                    changed_lines[current_line] = ("added", line[1:].strip())
                    current_line += 1
            elif line.startswith("-") and not line.startswith("---"):
                changed_lines[current_line] = ("removed", line[1:].strip())

        return changed_lines
