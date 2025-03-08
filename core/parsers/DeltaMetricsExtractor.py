import json
import os
import subprocess
from typing import Dict, List

from core.parsers.BaseMetricsExtractor import BaseMetricsExtractor
from infrastructure.adapters.external_tools.terra_metrics import TerraMetricsAdapter
from utils.logger_utils import logger

class DeltaMetricsExtractor(BaseMetricsExtractor):
    def __init__(self, jar_path: str):
        """
        Initialise l'extracteur Delta Metrics.

        Args:
            jar_path (str): Chemin vers le fichier JAR de TerraMetrics.
        """
        self.terra_adapter = TerraMetricsAdapter(jar_path)
        self.old_metrics = {}
        self.new_metrics = {}
    
    def extract_metrics(self, modified_blocks: Dict[str, List[str]]) -> Dict[str, dict]:
        """
        Analyse les blocs modifiés et calcule l'évolution des métriques par rapport à leur version précédente.

        Args:
            modified_blocks (dict): Dictionnaire contenant les fichiers et leurs blocs modifiés.

        Returns:
            dict: Dictionnaire des métriques différentielles.
        """
        if not modified_blocks:
            logger.warning("Aucun bloc Terraform modifié à analyser.")
            return {}

        self.new_metrics = self.terra_adapter.extract_metrics(modified_blocks)
        self.old_metrics = self.get_previous_metrics(modified_blocks)
        
        delta_metrics = {}
        for file, new_data in self.new_metrics.items():
            old_data = self.old_metrics.get(file, {})
            delta_metrics[file] = self.calculate_deltas(new_data, old_data)

        return delta_metrics
    
    def get_previous_metrics(self, modified_blocks: Dict[str, List[str]]) -> Dict[str, dict]:
        """
        Récupère les métriques des versions précédentes des blocs Terraform modifiés.
        Pour chaque bloc, cherche spécifiquement le dernier commit qui a modifié ce bloc.

        Args:
            modified_blocks (dict): Dictionnaire contenant les fichiers et leurs blocs modifiés.

        Returns:
            dict: Mappings des métriques des versions précédentes.
        """
        previous_metrics = {}
        
        for file, blocks in modified_blocks.items():
            logger.info(f"Analyse des blocs modifiés dans {file}")
            previous_file_metrics = {"data": []}
            
            # Identifier les blocs par leur contenu ou signature
            for block_content in blocks:
                # Extraire l'identifiant du bloc à partir de son contenu
                # Par exemple, pour 'resource "aws_s3_bucket" "my_bucket"'
                block_lines = block_content.strip().split("\n")
                if not block_lines:
                    continue
                    
                # Récupérer la ligne de déclaration du bloc (première ligne non vide)
                block_declaration = next((line for line in block_lines if line.strip()), "")
                if not block_declaration:
                    continue
                    
                logger.info(f"Recherche de la dernière modification pour le bloc: {block_declaration}")
                
                # Utiliser git log avec -p pour trouver le dernier commit qui a modifié ce bloc spécifique
                # L'option -S cherche les commits où une chaîne a été ajoutée ou supprimée
                git_cmd = [
                    "git", "log", "-p", "-1", "--format=format:%H", 
                    "-S", block_declaration, "--", file
                ]
                
                try:
                    result = subprocess.run(
                        git_cmd,
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    if result.returncode != 0 or not result.stdout:
                        logger.warning(f"Impossible de trouver l'historique du bloc '{block_declaration}' dans {file}")
                        continue
                    
                    # Extraire le hash du commit
                    commit_hash = result.stdout.split("\n")[0].strip()
                    
                    if not commit_hash:
                        logger.warning(f"Aucun commit précédent trouvé pour le bloc '{block_declaration}'")
                        continue
                    
                    logger.info(f"Dernier commit modifiant ce bloc: {commit_hash}")
                    
                    # Récupérer l'état du bloc à ce commit spécifique
                    block_state_cmd = ["git", "show", f"{commit_hash}:{file}"]
                    block_state_result = subprocess.run(
                        block_state_cmd,
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    if block_state_result.returncode != 0:
                        logger.warning(f"Impossible de récupérer l'état du bloc à {commit_hash}")
                        continue
                    
                    # Extraire le bloc spécifique du contenu du fichier
                    file_content = block_state_result.stdout
                    
                    # Cette partie est complexe car il faut parser le contenu pour trouver le bon bloc
                    # Pour simplifier, nous pouvons analyser tout le fichier à ce commit
                    temp_blocks = {file: [file_content]}
                    
                    # Extraire les métriques du fichier à ce commit
                    commit_metrics = self.terra_adapter.extract_metrics(temp_blocks)
                    
                    if file in commit_metrics and "data" in commit_metrics[file]:
                        # Filtrer pour ne garder que les métriques du bloc qui nous intéresse
                        for block_metrics in commit_metrics[file].get("data", []):
                            block_id = f"{block_metrics.get('block', '')} {block_metrics.get('block_name', '')}"
                            if block_declaration in block_id:
                                previous_file_metrics["data"].append(block_metrics)
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la recherche des métriques précédentes: {e}")
            
            # Ajouter les métriques des blocs précédents pour ce fichier
            if previous_file_metrics["data"]:
                previous_metrics[file] = previous_file_metrics
        
        return previous_metrics

    def calculate_deltas(self, new_data: dict, old_data: dict) -> dict:
        """
        Calcule la différence entre les nouvelles métriques et les anciennes.

        Args:
            new_data (dict): Nouvelles métriques.
            old_data (dict): Anciennes métriques.

        Returns:
            dict: Vecteur différentiel des métriques.
        """
        delta = {}
        for metric, new_value in new_data.items():
            if isinstance(new_value, dict):
                old_value = old_data.get(metric, {})
                delta[metric] = self.calculate_deltas(new_value, old_value)
            elif isinstance(new_value, (int, float)):
                old_value = old_data.get(metric, 0)
                delta[metric] = new_value - old_value
            else:
                delta[metric] = new_value 
        
        return delta
    
    def compare_metrics(self, before_metrics: dict, after_metrics: dict) -> dict:
        """
        Compare les métriques avant et après les changements.

        Args:
            before_metrics (dict): Métriques avant les changements.
            after_metrics (dict): Métriques après les changements.

        Returns:
            dict: Différences entre les métriques avant et après les changements.
        """
        differences = {}

        for file, before_content in before_metrics.items():
            after_content = after_metrics.get(file, {})

            if "data" not in before_content or "data" not in after_content:
                continue

            file_differences = {}
            
            # Organiser les blocs par identifiants pour faciliter la comparaison
            before_blocks = {}
            for block in before_content.get("data", []):
                block_id = f"{block.get('block', 'unknown')} {block.get('block_name', '')}"
                before_blocks[block_id.strip()] = block
                
            after_blocks = {}
            for block in after_content.get("data", []):
                block_id = f"{block.get('block', 'unknown')} {block.get('block_name', '')}"
                after_blocks[block_id.strip()] = block

            # Comparer chaque bloc qui existe dans les deux versions
            for block_id, before_block in before_blocks.items():
                if block_id not in after_blocks:
                    continue
                
                after_block = after_blocks[block_id]
                block_diffs = {}
                
                # Comparer toutes les métriques numériques
                all_keys = set(before_block.keys()).union(set(after_block.keys()))
                for key in all_keys:
                    if key in ['block', 'block_name', 'defect_prediction', 'block_id', 'block_identifiers']:
                        continue  # Ignorer les identifiants
                    
                    before_value = before_block.get(key)
                    after_value = after_block.get(key)
                    
                    # Comparer les valeurs numériques
                    if isinstance(before_value, (int, float)) and isinstance(after_value, (int, float)):
                        if before_value != after_value:
                            block_diffs[key] = {
                                "old": before_value,
                                "new": after_value,
                                "delta": after_value - before_value
                            }
                
                if block_diffs:
                    file_differences[block_id] = block_diffs
            
            if file_differences:
                differences[file] = file_differences
        
        return differences
    
    def display_differences(self, analysis_results: Dict[str, dict]):
        """
        Affiche les métriques avant, après, et leurs différences.

        Args:
            analysis_results (Dict[str, dict]): Dictionnaire des résultats d'analyse.
        """
        logger.info("\n📊 Comparaison des métriques avant et après les changements :")
        
        # Métriques à ignorer dans l'affichage détaillé
        ignore_metrics = ['block', 'block_name', 'defect_prediction', 'block_id', 'block_identifiers']
        
        # Trouver les blocs communs entre avant et après
        common_files = set(self.old_metrics.keys()) & set(self.new_metrics.keys())
        
        for file_path in common_files:
            logger.info(f"\n📂 Fichier: {file_path}")
            
            # Créer des dictionnaires pour faciliter la recherche des blocs par ID
            old_blocks = {}
            for block in self.old_metrics.get(file_path, {}).get("data", []):
                block_id = f"{block.get('block', 'unknown')} {block.get('block_name', '')}"
                old_blocks[block_id.strip()] = block
                
            new_blocks = {}
            for block in self.new_metrics.get(file_path, {}).get("data", []):
                block_id = f"{block.get('block', 'unknown')} {block.get('block_name', '')}"
                new_blocks[block_id.strip()] = block
            
            # Afficher les blocs communs
            common_block_ids = set(old_blocks.keys()) & set(new_blocks.keys())
            for block_id in common_block_ids:
                logger.info(f"\n  🔹 Bloc: {block_id}")
                old_block = old_blocks[block_id]
                new_block = new_blocks[block_id]
                
                # 1. Afficher les métriques AVANT
                logger.info("    📄 AVANT le changement:")
                for key, value in sorted(old_block.items()):
                    if key not in ignore_metrics:
                        logger.info(f"      • {key}: {value}")
                
                # 2. Afficher les métriques APRÈS
                logger.info("\n    📄 APRÈS le changement:")
                for key, value in sorted(new_block.items()):
                    if key not in ignore_metrics:
                        logger.info(f"      • {key}: {value}")
                
                # 3. Afficher les DIFFÉRENCES
                logger.info("\n    📈 DIFFÉRENCES:")
                differences_found = False
                
                # Comparer toutes les clés des deux blocs
                all_keys = set(old_block.keys()) | set(new_block.keys())
                for key in sorted(all_keys):
                    if key in ignore_metrics:
                        continue
                    
                    old_value = old_block.get(key)
                    new_value = new_block.get(key)
                    
                    # Si la clé existe dans les deux versions
                    if key in old_block and key in new_block:
                        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
                            if old_value != new_value:
                                delta = new_value - old_value
                                change_symbol = "↑" if delta > 0 else "↓" if delta < 0 else "="
                                logger.info(f"      • {key}: {old_value} → {new_value} ({change_symbol} {delta})")
                                differences_found = True
                        elif old_value != new_value:
                            logger.info(f"      • {key}: {old_value} → {new_value}")
                            differences_found = True
                    # Si la clé existe seulement dans la nouvelle version
                    elif key in new_block:
                        logger.info(f"      • {key}: [Ajouté] → {new_value}")
                        differences_found = True
                    # Si la clé existe seulement dans l'ancienne version
                    else:
                        logger.info(f"      • {key}: {old_value} → [Supprimé]")
                        differences_found = True
                
                if not differences_found:
                    logger.info("      Aucune différence détectée pour ce bloc.")
        
        # Sauvegarder les différences pour le rapport
        differences = self.compare_metrics(self.old_metrics, self.new_metrics)
        if differences:
            analysis_results["differences"] = differences