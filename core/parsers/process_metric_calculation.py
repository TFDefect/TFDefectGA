import numpy as np


def get_subs_dire_name(fileDirs):
    """
    Extracts subsystem, directory, and file name from a given file path.

    :param fileDirs: Path to the file as a string.
    :return: A tuple containing (subsystem, directory, file_name).
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
    A class to compute various process metrics related to software changes,
    including developer experience, code ownership, historical defects, and change frequency.
    """

    def __init__(self, contribution, previous_contributions):
        """
        Initializes the ProcessMetrics object with contribution and historical changes.

        :param contribution: Dictionary containing details of the current change.
        :param previous_contributions: List of previous contributions.
        """
        self.contribution = contribution
        self.author = self.contribution["author"]
        self.file = self.contribution["file"]
        self.identifier = self.contribution["block_identifiers"]
        self.actualCommit = self.contribution["commit"]
        self.previous_contributions = previous_contributions

        # Filter previous contributions by the same author
        self.blocks_changed_before_by_current_author = [
            prev_contribution for prev_contribution in self.previous_contributions
            if prev_contribution["author"] == self.author
        ]

        # Filter blocks that were changed by the same author and have the same identifier
        self.blocks_changed_before_by_author_as_current_changed_block = [
            prev_contribution for prev_contribution in self.blocks_changed_before_by_current_author
            if prev_contribution["block_identifiers"] == self.identifier and
               prev_contribution["file"] == self.file
        ]

        # Filter blocks that match the current changed block (irrespective of the author)
        self.blocks_changed_before_as_current_changed_block_by_different_authors = [
            prev_contribution for prev_contribution in self.previous_contributions
            if prev_contribution["block_identifiers"] == self.identifier and
               prev_contribution["file"] == self.file
        ]

    def num_defects_in_block_before(self):
        """
        Computes the number of previous defects in the same block.

        :return: Count of past defects affecting the block.
        """
        defects = [prev_contribution for prev_contribution in
                   self.blocks_changed_before_as_current_changed_block_by_different_authors
                   if prev_contribution["fault_prone"] == 1]
        return len(defects)

    def kexp(self):
        """
        Computes the experience of the developer with specific resources or data types.

        :return: Experience count based on past interactions with similar resources.
        """
        k_exp = 0
        if self.contribution["isResource"] == 1 or self.contribution["isData"] == 1:
            near_blocks = [
                near_block for near_block in self.blocks_changed_before_by_current_author
                if near_block["block"] == self.contribution["block"] and
                   near_block["block_id"] == self.contribution["block_id"]
            ]
            k_exp = len(near_blocks)
        return k_exp

    def num_devs(self):
        """
        Computes the number of distinct developers who have modified the block before.

        :return: Count of unique developers.
        """
        unique_authors = set(prev_contribution["author"] for prev_contribution
                             in self.blocks_changed_before_as_current_changed_block_by_different_authors)
        return len(unique_authors)

    def num_commits(self):
        """
        Computes the number of commits that changed the block before.

        :return: Count of distinct commits affecting the block.
        """
        commits_before = set(prev_contribution["commit"] for prev_contribution
                             in self.blocks_changed_before_as_current_changed_block_by_different_authors)
        return len(commits_before)

    def code_ownership(self):
        """
        Computes the ownership of the block by the current author based on past contributions.

        :return: Ratio of author's past changes on the block relative to their overall contributions.
        """
        current_author_experience = self.contribution["exp"]
        if current_author_experience != 0:
            return len(self.blocks_changed_before_by_author_as_current_changed_block) / current_author_experience
        return 0

    def get_author_rexp(self):
        """
        Computes the recent experience of the developer weighted by recency.

        :return: Recent experience score.
        """
        rexp = 0
        if self.blocks_changed_before_by_current_author:
            for lastBlock in self.blocks_changed_before_by_current_author:
                age = (self.contribution["date"] - lastBlock["date"]).days
                age = max(age, 0)
                rexp += 1 / (age + 1)
        return rexp

    def age(self):
        """
        Computes the average time interval between past changes to the block.

        :return: Average age in days.
        """
        current_dt = self.contribution["date"]
        ages = []
        for lastBlock in self.blocks_changed_before_as_current_changed_block_by_different_authors:
            time_diff = current_dt - lastBlock["date"]
            ages.append(max(time_diff.days, 0))
        return np.mean(ages) if ages else 0.0

    def resume_process_metrics(self):
        """
        Collects and returns all computed process metrics.

        :return: Dictionary containing all calculated metrics.
        """
        return {
            "ndevs": self.num_devs(),
            "ncommits": self.num_commits(),
            "code_ownership": self.code_ownership(),
            "exp": self.contribution["exp"],
            "rexp": self.get_author_rexp(),
            "age": self.age(),
            "num_defects_before": self.num_defects_in_block_before(),
            "kexp": self.kexp()
        }
