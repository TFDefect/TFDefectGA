import re
from typing import List, Tuple


class TerraformParser:
    def __init__(self, file_path: str):
        """
        Initialise le parser avec le contenu du fichier.

        Args:
            file_path (str): Chemin vers le fichier Terraform à analyser.
        """
        with open(file_path, "r") as f:
            self.lines = f.readlines()

        # Vérifier si le fichier est vide
        if not self.lines:
            raise ValueError(
                f"Le fichier Terraform {file_path} est vide. Analyse ignorée."
            )

    @classmethod
    def from_string(cls, file_content: str):
        """
        Initialise un parser Terraform à partir d'une chaîne de caractères
        représentant le contenu d'un fichier Terraform.

        Args:
            file_content (str): Le contenu du fichier Terraform sous forme de string.

        Returns:
            TerraformParser: Une instance de la classe initialisée avec ce contenu.
        """
        instance = cls.__new__(cls)
        instance.lines = file_content.splitlines()

        if not instance.lines:
            raise ValueError("Le contenu Terraform fourni est vide. Analyse ignorée.")

        return instance

    def find_block(self, changed_line: int) -> str:
        """
        Trouve le bloc Terraform englobant une ligne modifiée.

        Args:
            changed_line (int): Numéro de la ligne modifiée.

        Returns:
            str: Le bloc Terraform englobant la ligne modifiée.
        """
        if changed_line < 0 or changed_line >= len(self.lines):
            return ""

        start, end = self._find_block_bounds(changed_line)
        return "\n".join(self.lines[start : end + 1])

    def _find_block_bounds(self, line_number: int) -> Tuple[int, int]:
        """
        Trouve les bornes exactes du bloc Terraform englobant une ligne donnée.

        Args:
            line_number (int): Numéro de la ligne pour laquelle trouver les bornes du bloc.

        Returns:
            Tuple[int, int]: Les indices de début et de fin du bloc Terraform.
        """
        if line_number >= len(self.lines):
            raise IndexError(
                f"Ligne {line_number} hors des limites du fichier {len(self.lines)} lignes."
            )

        start, end = line_number, line_number

        # Remonter jusqu'au début du bloc Terraform
        while start > 0 and not re.match(
            r"^\s*(resource|variable|module|output|provider|data|terraform)\s",
            self.lines[start],
        ):
            start -= 1

        # Trouver la fin du bloc en comptant les accolades `{}`
        brace_count = 0
        inside_multiline_comment = False

        for i in range(start, len(self.lines)):
            line = self.lines[i].strip()

            if line.startswith("#") or line.startswith("//"):
                continue

            if "/*" in line:
                inside_multiline_comment = True
            if "*/" in line:
                inside_multiline_comment = False
                continue

            if inside_multiline_comment:
                continue

            # Compter les accolades `{}` seulement si ce n'est pas un commentaire
            brace_count += line.count("{")
            brace_count -= line.count("}")

            if brace_count == 0:
                end = i
                break

        return start, end

    def find_blocks(self, changed_lines: List[int]) -> List[str]:
        """
        Trouve tous les blocs Terraform englobant une liste de lignes modifiées.

        Args:
            changed_lines (List[int]): Liste des lignes modifiées.

        Returns:
            List[str]: Liste des blocs Terraform impactés.
        """
        unique_blocks = set()
        for line in changed_lines:
            block = self.find_block(line)
            if block:
                unique_blocks.add(block)
        return list(unique_blocks)
