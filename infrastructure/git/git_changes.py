import os
from typing import Dict, List, Tuple

from core.parsers.terraform_parser import TerraformParser
from infrastructure.git.git_adapter import GitAdapter
from utils.logger_utils import logger


class GitChanges:
    """
    Classe permettant d'extraire les lignes modifiées des fichiers Terraform et d'identifier les blocs impactés.
    """

    def __init__(self, repo_path: str = "."):
        """
        Initialise la classe pour analyser les changements Git.

        Args:
            repo_path (str): Chemin du dépôt local.
        """
        self.repo_path = repo_path
        self.git_adapter = GitAdapter(repo_path)

    def get_modified_lines(self) -> List[Tuple[str, List[int], List[int]]]:
        """
        Récupère les lignes ajoutées et supprimées dans les fichiers Terraform modifiés.

        Returns:
            List[Tuple[str, List[int], List[int]]]: Une liste contenant le chemin du fichier,
            les numéros des lignes ajoutées et les numéros des lignes supprimées.
        """
        try:
            modified_files = self.git_adapter.get_latest_commit_files()
            modified_files_with_lines = []

            for file_path, _ in modified_files:
                abs_file_path = os.path.join(self.repo_path, file_path)
                if not os.path.exists(abs_file_path):
                    logger.error(f"Fichier introuvable : {abs_file_path}")
                    continue

                added_lines = []
                deleted_lines = []
                latest_commit = next(self.git_adapter.repo.traverse_commits())

                for file in latest_commit.modified_files:
                    if file.new_path == file_path or file.old_path == file_path:
                        added_lines = [line[0] for line in file.diff_parsed["added"]]
                        deleted_lines = [
                            line[0] for line in file.diff_parsed["deleted"]
                        ]
                        break

                modified_files_with_lines.append(
                    (file_path, added_lines, deleted_lines)
                )

            return modified_files_with_lines
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des lignes modifiées : {str(e)}")
            return []

    def get_modified_blocks(self) -> Dict[str, List[str]]:
        """
        Récupère les blocs Terraform modifiés à partir des lignes impactées.

        Returns:
            Dict[str, List[str]]: Dictionnaire où la clé est le chemin du fichier,
            et la valeur est une liste de blocs Terraform modifiés.
        """
        try:
            modified_lines = self.get_modified_lines()
            modified_blocks = {}

            for file_path, added_lines, _ in modified_lines:
                abs_file_path = os.path.join(self.repo_path, file_path)
                if not os.path.exists(abs_file_path):
                    logger.error(f"Fichier introuvable : {abs_file_path}")
                    continue

                parser = TerraformParser(abs_file_path)
                blocks = parser.find_blocks(added_lines)
                if blocks:
                    modified_blocks[file_path] = blocks

            return modified_blocks
        except Exception as e:
            logger.error(
                f"Erreur lors de l'extraction des blocs Terraform modifiés : {str(e)}"
            )
            return {}

    def get_changed_blocks(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Compare les blocs Terraform avant et après modification.

        Returns:
            Dict[str, Dict[str, List[str]]]: Dictionnaire contenant les fichiers modifiés
                                            avec leurs blocs avant et après modification.
        """
        try:
            changed_blocks = {}

            # Récupérer les fichiers modifiés avec leur contenu avant et après modification
            modified_files = self.git_adapter.get_modified_tf_files_with_content()

            for file_path, _, current_content, previous_content in modified_files:
                if not file_path.endswith(".tf"):
                    continue

                if not current_content or not previous_content:
                    logger.warning(
                        f"Contenu manquant pour {file_path}, impossible de comparer."
                    )
                    continue

                # Extraire les blocs Terraform AVANT et APRÈS modification
                parser_before = TerraformParser.from_string(previous_content)
                parser_after = TerraformParser.from_string(current_content)

                blocks_before = parser_before.find_blocks(
                    range(len(previous_content.split("\n")))
                )
                blocks_after = parser_after.find_blocks(
                    range(len(current_content.split("\n")))
                )

                # Comparer les blocs
                modified = [
                    block for block in blocks_after if block not in blocks_before
                ]
                removed = [
                    block for block in blocks_before if block not in blocks_after
                ]

                if modified or removed:
                    changed_blocks[file_path] = {
                        "before": (
                            removed if removed else ["(Aucun changement supprimé)"]
                        ),
                        "after": (
                            modified if modified else ["(Aucun changement ajouté)"]
                        ),
                    }
                    logger.info(f"Blocs réellement modifiés détectés dans {file_path}")

            return changed_blocks

        except Exception as e:
            logger.error(f"Erreur lors de la comparaison des blocs : {str(e)}")
            return {}
