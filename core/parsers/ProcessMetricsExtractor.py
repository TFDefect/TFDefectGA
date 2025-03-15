import os
import subprocess
from datetime import datetime
from typing import Dict, List

from core.parsers.BaseMetricsExtractor import BaseMetricsExtractor
from core.parsers.process_metric_calculation import ProcessMetrics
from utils.logger_utils import logger


class ProcessMetricsExtractor(BaseMetricsExtractor):
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def extract_metrics(self, modified_blocks: Dict[str, List[str]]) -> Dict[str, dict]:
        """
        Pour chaque fichier et bloc Terraform modifié, calcule l'ensemble des métriques
        de processus et renvoie un dictionnaire contenant ces métriques.
        """
        if not modified_blocks:
            logger.warning("Aucun bloc Terraform modifié à analyser.")
            return {}

        process_metrics = {}
        for file_path, blocks in modified_blocks.items():
            process_metrics[file_path] = []
            for block in blocks:
                # Récupère la contribution actuelle via Git
                contribution = self.get_contribution_details(file_path, block)
                # Récupère l'historique des contributions précédentes
                previous_contributions = self.get_previous_contributions(file_path, block)

                # Calcule les métriques de base via la classe ProcessMetrics
                pm = ProcessMetrics(contribution, previous_contributions)
                base_metrics = pm.resume_process_metrics()

                # Calcule des métriques additionnelles liées aux processus
                base_metrics["time_interval"] = self.get_time_interval(previous_contributions, contribution)
                base_metrics["num_same_instances_changed_before"] = self.get_num_same_instances_changed_before(
                    previous_contributions,
                    contribution
                )
                base_metrics["num_unique_change"] = self.get_num_unique_change(previous_contributions, contribution)
                base_metrics["sexp"] = self.get_s_exp(contribution, previous_contributions)
                base_metrics["bexp"] = self.get_b_exp(contribution, previous_contributions)

                process_metrics[file_path].append(base_metrics)

        return process_metrics

    def get_contribution_details(self, file_path: str, block: str) -> dict:
        """
        Récupère les détails de la contribution actuelle pour un bloc donné,
        en utilisant les commandes Git.
        """
        abs_file_path = os.path.join(self.repo_path, file_path)

        # Commit le plus récent affectant le fichier
        last_commit_proc = subprocess.run(
            ["git", "log", "-n", "1", "--pretty=format:%H", "--", abs_file_path],
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
        current_commit = last_commit_proc.stdout.strip()

        # Récupère la date du commit
        date_proc = subprocess.run(
            ["git", "show", "-s", "--format=%ci", current_commit],
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
        date_str = date_proc.stdout.strip()
        commit_date = self._parse_git_datetime(date_str)

        # Récupère l'auteur du commit
        author_proc = subprocess.run(
            ["git", "show", "-s", "--format=%an", current_commit],
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
        author = author_proc.stdout.strip()

        # Calcul de l'expérience (exp) de cet auteur
        exp = self._calculate_experience(author)

        return {
            "author": author,
            "file": file_path,
            "block_identifiers": block,
            "commit": current_commit,
            "date": commit_date,
            "exp": exp,
            "isResource": 1,
            "isData": 0,
            "block": "resource",
            "block_id": "block_id"
        }

    def get_previous_contributions(self, file_path: str, block: str) -> List[dict]:
        """
        Récupère les contributions précédentes pour un bloc donné à partir de l'historique Git.
        """
        abs_file_path = os.path.join(self.repo_path, file_path)
        # Liste des commits (du plus récent au plus ancien)
        commits_output = subprocess.run(
            ["git", "log", "--pretty=format:%H", "--", abs_file_path],
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
        commit_list = commits_output.stdout.strip().split("\n")

        previous_contributions = []
        if len(commit_list) > 1:
            # On ignore le plus récent (pointé par get_contribution_details)
            for chash in commit_list[1:]:
                date_str, author = self._get_commit_date_author(chash)
                cdate = self._parse_git_datetime(date_str)
                cexp = self._calculate_experience(author)

                previous_contributions.append({
                    "author": author,
                    "file": file_path,
                    "block_identifiers": block,
                    "commit": chash,
                    "date": cdate,
                    "fault_prone": 0,  # Peut être déterminé à partir de logs ou de tickets
                    "exp": cexp,
                    "isResource": 1,
                    "isData": 0,
                    "block": "resource",
                    "block_id": "block_id"
                })

        return previous_contributions

    def get_time_interval(self, previous_contributions: List[dict], current: dict) -> float:
        """
        Calcule la moyenne d’intervalle (en jours) entre chaque contribution précédente et la contribution actuelle.
        """
        if not previous_contributions:
            return 0.0
        intervals = []
        for contrib in previous_contributions:
            diff = current["date"] - contrib["date"]
            intervals.append(abs(diff.days))
        return float(sum(intervals) / len(intervals)) if intervals else 0.0

    def get_num_same_instances_changed_before(self, previous_contributions: List[dict], current: dict) -> int:
        """
        Calcule le nombre de fois où le bloc identique a été modifié dans l’historique.
        """
        same_instances = [
            p for p in previous_contributions
            if p["block_identifiers"] == current["block_identifiers"]
               and p["file"] == current["file"]
        ]
        return len(same_instances)

    def get_num_unique_change(self, previous_contributions: List[dict], current: dict) -> int:
        """
        Calcule le nombre de commits distincts qui ont affecté ce bloc.
        """
        unique_commits = {p["commit"] for p in previous_contributions}
        return len(unique_commits)

    def get_s_exp(self, current: dict, previous_contributions: List[dict]) -> float:
        """
        Calcule l’expérience s_exp basée sur un critère spécifique (ex: nombre de modifications successives).
        """
        # Exemple : s_exp = nombre de commits successifs de l’auteur sur ce bloc
        same_author_commits = [
            p for p in previous_contributions if p["author"] == current["author"]
        ]
        return float(len(same_author_commits))

    def get_b_exp(self, current: dict, previous_contributions: List[dict]) -> float:
        """
        Calcule l’expérience b_exp basée sur un autre critère (ex: modifications de blocs similaires).
        """
        # Exemple : b_exp = nombre de fois où l’auteur a modifié 'block' dans n’importe quel fichier
        same_block_commits = [
            p for p in previous_contributions
            if p["block"] == current["block"] and p["author"] == current["author"]
        ]
        return float(len(same_block_commits))

    def _get_commit_date_author(self, commit_hash: str) -> (str, str):
        """
        Retourne la date et l’auteur d’un commit donné.
        """
        # Récupère la date
        date_proc = subprocess.run(
            ["git", "show", "-s", "--format=%ci", commit_hash],
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
        date_str = date_proc.stdout.strip()

        # Récupère l’auteur
        author_proc = subprocess.run(
            ["git", "show", "-s", "--format=%an", commit_hash],
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
        author_str = author_proc.stdout.strip()

        return date_str, author_str

    def _parse_git_datetime(self, date_str: str) -> datetime:
        """
        Parse la date renvoyée par Git au format '%ci' vers un objet datetime.
        """
        # Format Git : 'YYYY-MM-DD HH:MM:SS ±HHMM'
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")

    def _calculate_experience(self, author: str) -> int:
        """
        Extrait un indice d'expérience en se basant sur le nombre total de commits
        de l'auteur dans le repo.
        """
        commit_count_proc = subprocess.run(
            ["git", "log", "--author", author, "--pretty=format:%H"],
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
        commits_auth = commit_count_proc.stdout.strip().split("\n")
        # L'expérience pourrait se mesurer par le total de commits de l’auteur
        return len(commits_auth)