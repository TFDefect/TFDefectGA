import os
import tempfile
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

    def get_blocks_before_change(self, commit_hash: str) -> Dict[str, List[str]]:
        """
        Récupère les blocs Terraform avant les changements dans un commit.

        Args:
            commit_hash (str): Le hash du commit pour lequel récupérer les blocs avant les changements.

        Returns:
            Dict[str, List[str]]: Un dictionnaire où la clé est le chemin du fichier et la valeur
                                  est une liste de blocs avant les changements dans ce fichier.
        """
        modified_files = self.git_adapter.get_modified_files(commit_hash)
        blocks_before_change = {}

        for file_path, status in modified_files:
            if status == "deleted":
                logger.warning(f"Le fichier supprimé {file_path} est ignoré.")
                continue

            try:
                # Récupérer le contenu du fichier tel qu'il était dans le parent commit
                parent_commit_hash = f"{commit_hash}^"
                file_content = self.git_adapter.repo.git.show(f"{parent_commit_hash}:{file_path}")

                # Créer un fichier temporaire avec le contenu du parent commit
                with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name

                # Parser le contenu du fichier temporaire
                parser = TerraformParser(temp_file_path)
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
                    blocks_before_change[file_path] = file_blocks

            except ValueError as ve:
                logger.warning(str(ve))  # Ignore les fichiers vides
                continue
            except FileNotFoundError:
                logger.error(f"Erreur lors de l'ouverture du fichier {file_path}.")
                continue

        return blocks_before_change
