def extract_block_identifier(block: str) -> str:
    """
    Extrait un identifiant unique pour un bloc Terraform.

    Exemple : 'resource "aws_s3_bucket" "mybucket"' -> 'aws_s3_bucket.mybucket'

    Args:
        block (str): Contenu brut du bloc.

    Returns:
        str: Identifiant unique du bloc (ou chaîne vide si non trouvé)
    """
    dq = '"'
    lines = block.strip().splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("resource") or line.startswith("data"):
            parts = line.split()
            if len(parts) >= 3:
                return f"{parts[1].strip(dq)}.{parts[2].strip(dq)}"
        elif line.startswith(("module", "provider", "variable", "output")):
            parts = line.split()
            if len(parts) >= 2:
                return f"{parts[0]}.{parts[1].strip(dq)}"
        elif line.startswith("terraform"):
            return "terraform"
    return ""
