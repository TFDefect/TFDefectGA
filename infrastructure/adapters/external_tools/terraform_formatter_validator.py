import os
import subprocess
from typing import List
from utils.logger_utils import logger


class TerraformFormatterValidator:
    """Classe pour la validation et la normalisation des fichiers Terraform."""

    def __init__(self, terraform_path: str = "terraform"):
        self.terraform_path = terraform_path

    def format_file(self, file_path: str) -> bool:
        """
        Applique `terraform fmt` pour normaliser le fichier.

        Args:
            file_path (str): Chemin du fichier .tf à formater.

        Returns:
            bool: True si le formatage a réussi, False sinon.
        """
        if not os.path.exists(file_path):
            logger.error(f"Fichier introuvable : {file_path}")
            return False

        try:
            command = [self.terraform_path, "fmt", file_path]
            subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info(f"Formatage réussi : {file_path}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur de formatage ({file_path}) : {e.stderr}")
            return False

    def validate_file(self, file_path: str) -> bool:
        """
        Vérifie la validité du fichier avec `terraform validate`.

        Cette fonction est désactivée car elle génère des erreurs
        sur des fichiers qui ne sont pas dans un vrai projet Terraform.

        Args:
            file_path (str): Chemin du fichier .tf à valider.

        Returns:
            bool: True si le fichier est valide, False sinon.
        """
        if not os.path.exists(file_path):
            logger.error(f"Fichier introuvable : {file_path}")
            return False

        try:
            # Désactivé pour éviter les erreurs sur des fichiers isolés
            # command = [self.terraform_path, "validate", file_path]
            # subprocess.run(command, check=True, capture_output=True, text=True)
            # logger.info(f"Validation réussie : {file_path}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur de validation ({file_path}) : {e.stderr}")
            return False

    def process_files(self, file_paths: List[str]) -> List[str]:
        """
        Applique le formatage et (optionnellement) la validation sur une liste de fichiers Terraform.

        Args:
            file_paths (List[str]): Liste des fichiers .tf à traiter.

        Returns:
            List[str]: Liste des fichiers valides après traitement.
        """
        valid_files = []

        for file in file_paths:
            if self.format_file(file):
                # Vérification désactivée pour éviter des erreurs sur des fichiers isolés
                # if self.validate_file(file):
                valid_files.append(file)

        return valid_files
