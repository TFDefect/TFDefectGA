import numpy as np


def get_subs_dire_name(fileDirs):
    """
    Extrait le sous-système, le répertoire et le nom du fichier à partir d'un chemin.
    """
    fileDirs = fileDirs.split("/")
    if len(fileDirs) == 1:
        subsystem = "root"
        directory = "root"
    else:
        subsystem = fileDirs[0]
        directory = "/".join(fileDirs[0:-1])
    file_name = fileDirs[-1]
    return subsystem, directory, file_name


class ProcessMetrics:
    """
    Classe pour calculer les métriques de processus à partir d'une contribution et de son historique.
    """

    def __init__(self, contribution, previous_contributions):
        self.contribution = contribution
        self.author = contribution["author"]
        self.file = contribution["file"]
        self.identifier = contribution["block_identifiers"]
        self.actualCommit = contribution["commit"]
        self.previous_contributions = previous_contributions

        # Contributions passées par le même auteur
        self.blocks_changed_before_by_current_author = [
            p for p in previous_contributions if p["author"] == self.author
        ]

        # Même bloc modifié par le même auteur
        self.blocks_changed_before_by_author_as_current_changed_block = [
            p
            for p in self.blocks_changed_before_by_current_author
            if p["block_identifiers"] == self.identifier and p["file"] == self.file
        ]

        # Même bloc modifié dans l'historique (tous auteurs confondus)
        self.blocks_changed_before_as_current_changed_block_by_different_authors = [
            p
            for p in previous_contributions
            if p["block_identifiers"] == self.identifier and p["file"] == self.file
        ]

    def num_defects_in_block_before(self):
        """
        Nombre de défauts passés sur ce bloc.
        """
        defects = [
            p
            for p in self.blocks_changed_before_as_current_changed_block_by_different_authors
            if p["fault_prone"] == 1
        ]
        return len(defects)

    def kexp(self):
        """
        Expérience du développeur sur ce type spécifique de ressource ou donnée.
        """
        if self.contribution["isResource"] == 1 or self.contribution["isData"] == 1:
            near_blocks = [
                b
                for b in self.blocks_changed_before_by_current_author
                if b["block"] == self.contribution["block"]
                and b["block_id"] == self.contribution["block_id"]
            ]
            return len(near_blocks)
        return 0

    def num_same_blocks_with_different_names_changed_before(self):
        """
        Compte le nombre d'instances où des blocs similaires ont été modifiés auparavant.
        """
        if self.contribution["isResource"] == 1 or self.contribution["isData"] == 1:
            near_duplicated = [
                p
                for p in self.previous_contributions
                if p["block"] == self.contribution["block"]
                and p["block_id"] == self.contribution["block_id"]
            ]
            return len(near_duplicated)
        return 0

    def num_devs(self):
        """
        Nombre de développeurs différents ayant modifié ce bloc.
        """
        return len(
            set(
                p["author"]
                for p in self.blocks_changed_before_as_current_changed_block_by_different_authors
            )
        )

    def num_commits(self):
        """
        Nombre total de commits ayant affecté ce bloc.
        """
        return len(
            set(
                p["commit"]
                for p in self.blocks_changed_before_as_current_changed_block_by_different_authors
            )
        )

    def num_unique_change(self):
        """
        Nombre de changements uniques ayant affecté ce bloc (1 commit = 1 changement unique).
        """
        commits_dict = {}

        for p in self.previous_contributions:
            commit = p["commit"]
            if commit not in commits_dict:
                commits_dict[commit] = []
            commits_dict[commit].append(p)

        impacted_current_block = sum(
            1
            for blocks in commits_dict.values()
            if len(blocks) == 1
            and blocks[0]["block_identifiers"] == self.identifier
            and blocks[0]["file"] == self.file
        )

        return impacted_current_block

    def code_ownership(self):
        """
        Propriété du code : part de l'auteur actuel sur les modifications de ce bloc.
        """
        exp = self.contribution["exp"]
        if exp != 0:
            return (
                len(self.blocks_changed_before_by_author_as_current_changed_block) / exp
            )
        return 0

    def get_author_rexp(self):
        """
        Expérience récente de l'auteur : pondérée selon l'ancienneté des modifications passées.
        """
        rexp = 0
        for p in self.blocks_changed_before_by_current_author:
            age = (self.contribution["date"] - p["date"]).days
            rexp += 1 / (max(age, 0) + 1)
        return rexp

    def get_author_bexp(self):
        """
        Expérience de l'auteur sur d'autres blocs du même type.
        """
        bexp = 0
        for p in self.blocks_changed_before_by_current_author:
            if (
                p["block"] == self.contribution["block"]
                and p["commit"] != self.contribution["commit"]
            ):
                bexp += 1
        return bexp

    def get_author_sexp(self):
        """
        Expérience de l'auteur dans le même sous-système (premier dossier du chemin).
        """
        sexp = 0
        current_subsystem, _, _ = get_subs_dire_name(self.contribution["file"])
        for p in self.blocks_changed_before_by_current_author:
            prev_subsystem, _, _ = get_subs_dire_name(p["file"])
            if (
                current_subsystem == prev_subsystem
                and p["commit"] != self.contribution["commit"]
            ):
                sexp += 1
        return sexp

    def age(self):
        """
        Âge moyen des modifications précédentes du bloc.
        """
        current_dt = self.contribution["date"]
        ages = [
            max((current_dt - p["date"]).days, 0)
            for p in self.blocks_changed_before_as_current_changed_block_by_different_authors
        ]
        return np.mean(ages) if ages else 0.0

    def time_interval(self):
        """
        Temps écoulé entre la modification actuelle et la précédente (si elle existe).
        """
        blocks = (
            self.blocks_changed_before_as_current_changed_block_by_different_authors
        )
        recent_block = blocks[-1] if blocks else None
        if recent_block:
            delta = self.contribution["date"] - recent_block["date"]
            return delta.days
        return 0

    def resume_process_metrics(self):
        """
        Regroupe toutes les métriques calculées en un seul dictionnaire.
        """
        return {
            "ndevs": self.num_devs(),
            "ncommits": self.num_commits(),
            "code_ownership": self.code_ownership(),
            "exp": self.contribution["exp"],
            "rexp": self.get_author_rexp(),
            "sexp": self.get_author_sexp(),
            "bexp": self.get_author_bexp(),
            "age": self.age(),
            "time_interval": self.time_interval(),
            "num_defects_before": self.num_defects_in_block_before(),
            "num_same_instances_changed_before": self.num_same_blocks_with_different_names_changed_before(),
            "kexp": self.kexp(),
            "num_unique_change": self.num_unique_change(),
        }
