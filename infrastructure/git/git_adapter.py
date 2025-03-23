from typing import List, Tuple

from pydriller import ModificationType, Repository

from utils.logger_utils import logger


def get_latest_commit_hash(repo_path: str = ".") -> str:
    latest = next(Repository(repo_path, order="reverse").traverse_commits())
    return latest.hash


class GitAdapter:
    """
    Service centralisé pour les opérations Git, utilisant PyDriller.
    """

    def __init__(self, repo_path: str = "."):
        """
        Initialise le service Git et configure l'analyse du dépôt.

        Args:
            repo_path (str): Chemin du dépôt local (par défaut le répertoire courant).
        """
        self.repo_path = repo_path
        self.repo = Repository(repo_path, order="reverse", only_no_merge=True)

    @staticmethod
    def verify_git_repo(repo_path: str = "."):
        """
        Vérifie que le répertoire est un dépôt Git valide en utilisant PyDriller.
        """
        try:
            repo = Repository(repo_path)
            commits = list(repo.traverse_commits())
            if not commits:
                raise ValueError("Aucun commit trouvé dans le dépôt.")
            logger.info(
                f"Git est bien initialisé et accessible. Dernier commit : {commits[0].hash}"
            )
        except Exception as e:
            logger.error(
                f"ERREUR : Ce répertoire n'est pas un dépôt Git valide ou il est vide. Détails : {str(e)}"
            )
            exit(1)

    def get_latest_commit_files(self) -> List[Tuple[str, str]]:
        """
        Récupère la liste des fichiers Terraform modifiés ou supprimés dans le dernier commit.

        Returns:
            List[Tuple[str, str]]: Liste des fichiers `.tf` modifiés avec leur statut (modified/deleted).
        """
        try:
            latest_commit = next(self.repo.traverse_commits())
            modified_files = []

            for file in latest_commit.modified_files:
                if file.filename.endswith(".tf"):
                    if file.change_type == ModificationType.DELETE:
                        status = "deleted"
                    elif file.change_type == ModificationType.MODIFY:
                        status = "modified"
                    elif file.change_type == ModificationType.ADD:
                        status = "added"
                    else:
                        status = "unknown"

                    modified_files.append((file.new_path or file.old_path, status))

            return modified_files
        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération des fichiers modifiés : {str(e)}"
            )
            return []

    def get_modified_tf_files_with_content(self) -> List[Tuple[str, str, str, str]]:
        """
        Récupère les fichiers .tf modifiés avec leur contenu avant et après le commit.

        Returns:
            List[Tuple[str, str, str, str]]: (chemin, statut, contenu_actuel, contenu_précédent)
        """
        try:
            commits = list(self.repo.traverse_commits())
            if len(commits) < 2:
                logger.warning("Aucun commit précédent trouvé.")
                return []

            latest_commit = commits[0]  # Dernier commit

            files = []

            for file in latest_commit.modified_files:
                if file.filename.endswith(".tf"):
                    # Déterminer le statut du fichier
                    status = "modified"
                    if file.change_type == ModificationType.DELETE:
                        status = "deleted"
                    elif file.change_type == ModificationType.ADD:
                        status = "added"

                    # Déterminer le chemin du fichier
                    file_path = (
                        file.new_path or file.old_path
                    )  # Prendre l'ancien chemin si renommé ou supprimé

                    # Vérifier si le contenu actuel ou précédent est disponible
                    current_content = (
                        file.source_code if file.source_code is not None else ""
                    )
                    previous_content = (
                        file.source_code_before
                        if file.source_code_before is not None
                        else ""
                    )

                    # Ajouter les informations à la liste
                    files.append((file_path, status, current_content, previous_content))

            return files

        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération des fichiers modifiés : {str(e)}"
            )
            return []
