import os
from typing import Dict, List

from core.parsers.terraform_parser import TerraformParser
from infrastructure.adapters.git.git_adapter import GitAdapter
from utils.logger_utils import logger


class GitChanges:
    def __init__(self, repo_path: str):
        """
        Initialise le service GitChanges avec un chemin vers le dépôt Git.

        Args:
            repo_path (str): Chemin vers le dépôt Git.
        """
        self.git_adapter = GitAdapter(repo_path)

    def get_modified_blocks(self, commit_hash: str) -> Dict[str, List[str]]:
        """
        Récupère les blocs Terraform modifiés dans un commit.

        Args:
            commit_hash (str): Le hash du commit pour lequel récupérer les blocs modifiés.

        Returns:
            Dict[str, List[str]]: Un dictionnaire où la clé est le chemin du fichier et la valeur
                                  est une liste de blocs modifiés dans ce fichier.
        """
        modified_files = self.git_adapter.get_modified_files(commit_hash)
        modified_blocks = {}

        for file_path, status in modified_files:
            if status == "deleted":
                logger.warning(f"Le fichier supprimé {file_path} est ignoré.")
                continue

            full_path = os.path.join(self.git_adapter.repo.working_tree_dir, file_path)

            # Vérifier que le fichier existe avant d'ouvrir
            if not os.path.exists(full_path):
                logger.error(f"Fichier Terraform introuvable : {full_path}")
                continue

            # Vérifier si le fichier est vide
            if os.stat(full_path).st_size == 0:
                logger.warning(f"Le fichier {file_path} est vide et sera ignoré.")
                continue

            try:
                parser = TerraformParser(full_path)
                changed_lines = self.git_adapter.get_changed_lines(
                    commit_hash, file_path
                )

                file_blocks = []
                for line_number in changed_lines:
                    try:
                        block = parser.find_block(line_number)
                        if block and block not in file_blocks:
                            file_blocks.append(block)
                    except IndexError as e:
                        logger.warning(str(e))
                        continue

                if file_blocks:
                    modified_blocks[file_path] = file_blocks

            except ValueError as ve:
                logger.warning(str(ve))  # Ignore les fichiers vides
                continue
            except FileNotFoundError:
                logger.error(f"Erreur lors de l'ouverture du fichier {file_path}.")
                continue

        return modified_blocks
