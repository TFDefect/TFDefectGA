import re
from typing import Tuple


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
        return "".join(self.lines[start : end + 1])

    def _find_block_bounds(self, line_number: int) -> Tuple[int, int]:
        """
        Trouve les bornes exactes du bloc Terraform englobant une ligne donnée.

        Args:
            line_number (int): Numéro de la ligne pour laquelle trouver les bornes du bloc.

        Returns:
            Tuple[int, int]: Les indices de début et de fin du bloc Terraform.

        Explication de l'algorithme:
        - L'algorithme commence par définir les indices de début et de fin du bloc comme étant la ligne donnée.
        - Il remonte ensuite les lignes jusqu'à trouver le début d'un bloc Terraform (défini par des mots-clés comme resource, variable, etc.).
        - Ensuite, il parcourt les lignes à partir du début du bloc pour trouver la fin du bloc en comptant les accolades `{}`.
        - Il ignore les lignes de commentaires et les lignes à l'intérieur des commentaires multi-lignes.
        - Le bloc se termine lorsque le nombre d'accolades ouvrantes et fermantes est équilibré.
        """
        if line_number >= len(self.lines):
            raise IndexError(
                f"Ligne {line_number} hors des limites du fichier {len(self.lines)} lignes."
            )

        start, end = line_number, line_number

        # Remonter jusqu'au début du bloc Terraform
        while start > 0 and not re.match(
            r"^\s*(resource|variable|module|output|provider|data)\s", self.lines[start]
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
