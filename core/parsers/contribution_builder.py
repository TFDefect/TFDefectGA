from typing import Dict, List

from pydriller import Repository

from core.parsers.terraform_parser import TerraformParser
from utils.block_utils import extract_block_identifier


def get_contribution(repo_path: str, file_path: str, block_identifiers: str) -> Dict:
    """
    Récupère les informations de la contribution actuelle à partir du dernier commit.
    """
    latest_commit = next(Repository(repo_path, order="reverse").traverse_commits())

    for file in latest_commit.modified_files:
        if file.new_path == file_path or file.old_path == file_path:
            return {
                "author": latest_commit.author.name,
                "file": file_path,
                "block_identifiers": block_identifiers,
                "commit": latest_commit.hash,
                "date": latest_commit.committer_date,
                "exp": (
                    latest_commit.author.total
                    if hasattr(latest_commit.author, "total")
                    else 1
                ),
                "isResource": 1 if "resource" in block_identifiers.lower() else 0,
                "isData": 1 if "data" in block_identifiers.lower() else 0,
                "block": (
                    block_identifiers.split(".")[0]
                    if "." in block_identifiers
                    else block_identifiers
                ),
                "block_id": block_identifiers,
            }

    return {}


def get_previous_contributions(
    repo_path: str,
    file_path: str,
    block_identifiers: str,
    defect_history: Dict[str, List[Dict]] = None,
) -> List[Dict]:
    """
    Reconstruit l'historique des contributions passées pour un bloc donné,
    en identifiant les blocs structurellement et en injectant le vrai fault_prone par commit.
    """
    contributions = []
    full_id = f"{file_path}::{block_identifiers}"

    for commit in Repository(repo_path).traverse_commits():
        for file in commit.modified_files:
            if file.new_path == file_path or file.old_path == file_path:
                if not file.source_code:
                    continue

                try:
                    parser = TerraformParser.from_string(file.source_code)
                    all_blocks = parser.find_blocks(list(range(len(parser.lines))))

                    for block in all_blocks:
                        extracted_id = extract_block_identifier(block)

                        if extracted_id == block_identifiers:
                            # Cherche la prédiction pour ce bloc à ce commit
                            fault_prone = 0
                            if defect_history:
                                for record in defect_history.get(full_id, []):
                                    if record["commit"] == commit.hash:
                                        fault_prone = record["fault_prone"]
                                        break

                            contributions.append(
                                {
                                    "author": commit.author.name,
                                    "file": file_path,
                                    "block_identifiers": block_identifiers,
                                    "commit": commit.hash,
                                    "date": commit.committer_date,
                                    "fault_prone": fault_prone,
                                    "exp": (
                                        commit.author.total
                                        if hasattr(commit.author, "total")
                                        else 1
                                    ),
                                    "block": (
                                        block_identifiers.split(".")[0]
                                        if "." in block_identifiers
                                        else block_identifiers
                                    ),
                                    "block_id": block_identifiers,
                                }
                            )
                except Exception:
                    continue

    return contributions
