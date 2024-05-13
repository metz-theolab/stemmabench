"""This module generates an artificial stemma given an initial text.
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple, Union

import numpy as np
from stemmabench.bench.config_parser import StemmaBenchConfig
from stemmabench.bench.textual_units.text import Text


class Stemma:
    """Class to generate an artificial textual tradition,
    given a configuration file.
    """

    def __init__(
        self,
        config: StemmaBenchConfig = None,
        config_path: str = None,
        original_text: str = None,
        path_to_text: str = None
    ) -> None:
        """A class to perform variant generation.
        Use the .fit() method to actually perform variant generation.

        Args:
            config (StemmaBenchConfig, optional): The configuration for the
                stemma generation. Defaults to None.
            config_path (str, optional): The path to a YAML file containing
                the configuration. Defaults to None.
            original_text (str, optional): The source text used to generate the
                tradition. Defaults to None.
            path_to_text (str, optional): The path to the source text used to
                generate the tradition. Defaults to None.

        Raises:
            Exception: If no input text is specified.
        """
        if original_text:
            self.original_text = original_text
        elif path_to_text:
            self.original_text = self.load_text(path_to_text)
        else:
            raise TypeError("No input text specified.")
        if config:
            self.config = config
        else:
            self.config = StemmaBenchConfig.from_yaml(config_path)
        self.depth = self.config.stemma.depth
        self.missing_manuscripts_rate = self.config.stemma.missing_manuscripts.rate
        
        self.tree = {}
        self._levels = [[]]  # Initialize the levels with an empty list
        self.texts_lookup = {}  # Dictionary to store manuscripts with their IDs
        self.edges = []  # List to store edges in the tree
        self.next_id = 1  # Next available ID

    @property
    def width(self):
        """Get the width of the tree, based on the random law defined
        in the configuration file.
        """
        if self.config.stemma.width.law == "Uniform":
            return int(np.random.uniform(self.config.stemma.width.min,
                                         self.config.stemma.width.max))
        elif self.config.stemma.width.law == "Gaussian":
            return int(np.random.normal(self.config.stemma.width.mean,
                                        self.config.stemma.width.sd))
        raise ValueError("Only Gaussian and Uniform laws are supported.")

    @staticmethod
    def load_text(path_to_text: str) -> str:
        """Load a text given a path to this text.

        Args:
            path_to_text (str): The path to the text to be loaded.

        Returns:
            str: The loaded text.
        """
        with open(Path(path_to_text), encoding="utf-8") as file:
            return file.read()

    def dict(self) -> Dict[str, List[str]]:
        """Return a dict representation of the tree.
        Dict is empty until tree is fitted (fitting can be done using .fit() method)
        """
        return self.tree

    def __repr__(self) -> str:
        """String representation of the tree"""
        return "Tree(" + json.dumps(self.dict(), indent=2) + ")"

    def _apply_level(self, manuscript: str) -> List[str]:
        """Apply transformation on a single generation"""
        return [Text(manuscript).transform(self.config.variants,
                                           meta_config=self.config.meta)
                for _ in range(self.width)]

    def missing_manuscripts(self) -> Tuple[Dict[str, str], List[Tuple[str]]]:
        """Remove some manuscripts from the tradition.
        """
        # Compute the number of manuscripts to delete.
        n_mss_to_delete = int(
            self.missing_manuscripts_rate * len(self.texts_lookup))
        # Select the manuscripts to delete.
        mss_list = list(self.texts_lookup)
        missing_mss = np.random.choice(
            mss_list, n_mss_to_delete, replace=False)
        # Subset non-missing manuscripts and non-missing edges.
        mss_non_missing = {mss_id: mss_text
                           for mss_id, mss_text in self.texts_lookup.items()
                           if mss_id not in missing_mss}
        edges_non_missing = [
            edge for edge in self.edges
            if all(node not in missing_mss for node in edge)
        ]
        return mss_non_missing, edges_non_missing

    def add_manuscript(self, text):
        """
        Add a manuscript to the tree.
        """
        manuscript_id = self.next_id
        self.texts_lookup[str(manuscript_id)] = text
        self.next_id += 1
        level = len(self._levels) - 1
        self._levels[level].append(manuscript_id)
        return manuscript_id

    def generate(self):
        """Fit the tree, I.E, generate variants"""
        self.add_manuscript(self.original_text)
        for depth in range(self.depth-1):
            self._levels.append([])
            for manuscript_id in self._levels[depth]:
                text = self.texts_lookup[str(manuscript_id)]
                transformed_texts = self._apply_level(text)
                for transformed_text in transformed_texts:
                    transformed_manuscript_id = self.add_manuscript(
                        transformed_text)
                    self.edges.append(
                        (manuscript_id, transformed_manuscript_id))
                self.tree[text] = transformed_texts
        return self

    def dump(self, folder: str) -> None:
        """Dump the generated stemma into a folder:
            - The texts
            - The corresponding tree structure

        Args:
            folder (str): The folder where the text should be written.
        """
        Path(folder).mkdir(exist_ok=True)
        for file_name, file_content in self.texts_lookup.items():
            file_path = Path(folder) / f"{file_name.replace(':', '_')}.txt"
            with file_path.open("w", encoding="utf-8") as f:
                f.write(file_content)
        with (Path(folder) / "edges.txt").open("w", encoding="utf-8") as f:
            for edge in self.edges:
                f.write(f"{edge}\n")

        # Missing tradition.
        if self.missing_manuscripts_rate > 0:
            missing_tradition_folder = Path(folder) / "missing_tradition"
            missing_tradition_folder.mkdir(exist_ok=True)
            miss_texts_lookup, miss_edges = self.missing_manuscripts()
            for file_name, file_content in miss_texts_lookup.items():
                file_path = missing_tradition_folder / \
                    f"{file_name.replace(':', '_')}.txt"
                with file_path.open("w", encoding="utf-8") as f:
                    f.write(file_content)
            with (missing_tradition_folder / "edges_missing.txt").open("w", encoding="utf-8") as f:
                for edge in miss_edges:
                    f.write(f"{edge}\n")
