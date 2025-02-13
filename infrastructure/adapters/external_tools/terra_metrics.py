import json
import os
import subprocess
import tempfile
from typing import Dict, List

from utils.logger_utils import setup_logger

logger = setup_logger()


class TerraMetricsAdapter:
    def __init__(self, jar_path: str):
        """
        Initialise l'adaptateur TerraMetrics avec le chemin vers le fichier JAR.

        Args:
            jar_path (str): Chemin vers le fichier JAR de TerraMetrics.
        """
        self.jar_path = jar_path
        if not os.path.exists(self.jar_path):
            raise FileNotFoundError(
                f"TerraMetrics JAR est introuvable : {self.jar_path}"
            )

    def analyze_blocks(self, modified_blocks: Dict[str, List[str]]) -> Dict[str, dict]:
        """
        Analyse plusieurs blocs Terraform modifiés.

        Args:
            modified_blocks (dict): Dictionnaire contenant les fichiers et leurs blocs modifiés.
                Format : { "fichier.tf": ["bloc1", "bloc2"] }

        Returns:
            dict: Résultats des métriques analysées.
        """
        if not modified_blocks:
            logger.warning("Aucun bloc Terraform à analyser.")
            return {}

        results = {}

        for file_name, blocks in modified_blocks.items():
            temp_tf_path = None
            temp_output_path = None

            try:
                # Créer un fichier temporaire pour stocker les blocs Terraform
                with tempfile.NamedTemporaryFile(
                    suffix=".tf", delete=False, mode="w"
                ) as temp_tf:
                    temp_tf_path = temp_tf.name
                    temp_tf.write("\n\n".join(blocks))

                # Créer un fichier temporaire pour stocker la sortie JSON
                with tempfile.NamedTemporaryFile(
                    suffix=".json", delete=False
                ) as temp_output:
                    temp_output_path = temp_output.name

                # Commande pour exécuter TerraMetrics
                command = [
                    "java",
                    "-jar",
                    self.jar_path,
                    "--file",
                    temp_tf_path,
                    "-b",
                    "--target",
                    temp_output_path,
                ]

                # Exécuter TerraMetrics
                _ = subprocess.run(command, check=True, capture_output=True, text=True)

                logger.info(f"[TerraMetrics] Output ({file_name}):")

                # Vérifier si le fichier de sortie JSON existe
                if not os.path.exists(temp_output_path):
                    logger.error(f"Aucun fichier de sortie généré pour {file_name}.")
                    continue

                # Lire et charger les résultats JSON
                with open(temp_output_path, "r") as f:
                    result_json = json.load(f)
                    results[file_name] = (
                        result_json
                    )

                # Afficher le contenu du fichier d'entré
                print("Fichier d'entrée:")
                with open(temp_tf_path, "r") as f:
                    print(f.read())

            except subprocess.CalledProcessError as e:
                logger.error(
                    f"Erreur TerraMetrics ({file_name}):\n{e.stdout}\n{e.stderr}"
                )
                results[file_name] = {"error": "TerraMetrics execution failed"}

            except Exception as e:
                logger.error(f"Erreur inattendue ({file_name}): {e}")
                results[file_name] = {"error": str(e)}

            finally:
                if temp_tf_path and os.path.exists(temp_tf_path):
                    os.remove(temp_tf_path)
                if temp_output_path and os.path.exists(temp_output_path):
                    os.remove(temp_output_path)

        return results

    def analyze_repo(self, repo_path: str) -> Dict[str, dict]:
        """
        Analyse l'ensemble d'un repository Terraform avec TerraMetrics.

        Args:
            repo_path (str): Chemin du repository Terraform (local ou GitHub).

        Returns:
            dict: Résultats des métriques analysées.
        """
        temp_output_path = None
        try:
            # Créer un fichier temporaire pour stocker les résultats JSON
            with tempfile.NamedTemporaryFile(
                suffix=".json", delete=False
            ) as temp_output:
                temp_output_path = temp_output.name

            # repo local (`-l`) ou repo GitHub (`-g`)
            if repo_path.startswith("http"):
                command = [
                    "java",
                    "-jar",
                    self.jar_path,
                    "-g",
                    "--repo",
                    repo_path,
                    "--target",
                    temp_output_path,
                ]
            else:
                command = [
                    "java",
                    "-jar",
                    self.jar_path,
                    "-l",
                    "--repo",
                    repo_path,
                    "--target",
                    temp_output_path,
                ]

            # Exécuter TerraMetrics
            _ = subprocess.run(command, check=True, capture_output=True, text=True)

            # Lire et charger les résultats JSON
            with open(temp_output_path, "r") as f:
                return json.load(f)

        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur TerraMetrics (Repo) :\n{e.stdout}\n{e.stderr}")
            return {"error": "TerraMetrics execution failed"}

        except Exception as e:
            logger.error(f"Erreur inattendue (Repo) : {e}")
            return {"error": str(e)}

        finally:
            if temp_output_path and os.path.exists(temp_output_path):
                os.remove(temp_output_path)
