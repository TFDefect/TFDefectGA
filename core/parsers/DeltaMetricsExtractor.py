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
        Récupère les métriques des versions précédentes des blocs modifiés
        en extrayant directement les données du commit précédent.

        Args:
            modified_blocks (dict): Blocs Terraform modifiés dans le commit actuel.

        Returns:
            dict: Métriques calculées pour ces mêmes blocs dans leur version précédente.
        """
        previous_metrics = {}
        
        for file in modified_blocks.keys():
            logger.info(f"Récupération des métriques précédentes pour {file}")
            
            # Récupérer le commit précédent pour ce fichier
            previous_commit_output = subprocess.run(
                ["git", "log", "-n", "1", "--skip", "1", "--pretty=format:%H", "--", file],
                capture_output=True,
                text=True,
            )
            previous_commit_hash = previous_commit_output.stdout.strip()
            
            if not previous_commit_hash:
                logger.warning(f"Aucun commit précédent trouvé pour {file}.")
                continue
            
            logger.info(f"Récupération de l'ancienne version de {file} (commit {previous_commit_hash})")
            
            # Récupérer le contenu du fichier dans le commit précédent
            file_content = subprocess.run(
                ["git", "show", f"{previous_commit_hash}:{file}"],
                capture_output=True,
                text=True,
            )
            
            if file_content.returncode != 0:
                logger.error(f"Impossible de récupérer l'ancienne version de {file}.")
                continue
            
            # Créer des blocs à partir du contenu du fichier précédent
            # Note: nous utilisons la même logique de splitting que dans le fichier actuel
            temp_blocks = {file: []}
            
            # Nous pouvons essayer de recréer les mêmes blocs que dans le commit actuel
            # mais dans leur état précédent en utilisant leur signature ou position
            current_blocks = modified_blocks[file]
            
            # Approche simplifiée: nous extrayons tout le fichier précédent
            # Une approche plus précise serait de faire correspondre les blocs par identifiant
            temp_blocks[file] = file_content.stdout.split("\n\n")
            
            # Extraire les métriques du fichier précédent
            file_previous_metrics = self.terra_adapter.extract_metrics(temp_blocks)
            
            # Ajouter à previous_metrics
            if file in file_previous_metrics:
                previous_metrics[file] = file_previous_metrics[file]
            else:
                previous_metrics[file] = {}
        
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