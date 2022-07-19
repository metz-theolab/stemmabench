"""This module generates an artificial stemma given an initial text.
"""
import json
from pathlib import Path
from typing import Dict, List, Union
from random import uniform, gauss
from stemmabench.config_parser import StemmaBenchConfig
from stemmabench.textual_units.text import Text


class Stemma:
    """Class to generate an artificial textual tradition,
    given a configuration file.
    """

    def __init__(
        self,
        config: StemmaBenchConfig = None,
        config_path: str = None,
        original_text: str = None,
        path_to_text: str = None,
    ) -> None:
        """A class to perform variant generation.
        Use the .fit() method to actually perform variant generation.
        """
        if original_text:
            self.original_text = original_text
        elif path_to_text:
            self.original_text = self.load_text(path_to_text)
        else:
            raise Exception("No input text specified.")
        if config:
            self.config = config
        else:
            self.config = StemmaBenchConfig.from_yaml(config_path)
        self.depth = self.config.stemma.depth
        self._levels: List[Dict[str, List[str]]] = []
        self.texts_lookup = {}
        self.edges = []

    @property
    def width(self):
        """Get the width of the tree, based on the random law defined
        in the configuration file.
        """
        if self.config.stemma.width.law == "Uniform":
            return int(uniform(self.config.stemma.width.min, self.config.stemma.width.max))
        elif self.config.stemma.width.law == "Gaussian":
            return int(gauss(self.config.stemma.width.mean, self.config.stemma.width.sd))
        else:
            raise Exception("Only Gaussian and Uniform laws are supported.")

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

    def dict(self) -> Dict[str, Union[List[str], Dict[str, List[str]]]]:
        """Return a dict representation of the tree.
        Dict is empty until tree is fitted (fitting can be done using .fit() method)
        """
        # Create dicts from bottom to top
        _tree: Dict[str, Union[List[str], Dict[str, List[str]]]] = dict()
        # Iterate from bottom to top
        for level in reversed(self._levels):
            # Create tree using bottom values
            if not _tree:
                _tree.update(level)
            else:
                # Create new tree
                _tree = {
                    key: {subkey: _tree[subkey]
                          for subkey in values}  # type: ignore[misc]
                    for key, values in level.items()
                }
        return _tree

    def __repr__(self) -> str:
        """String representation of the tree"""
        return "Tree(" + json.dumps(self.dict(), indent=2) + ")"

    def _apply_level(self, manuscript: str) -> List[str]:
        """Apply transformation on a single generation"""
        return [Text(manuscript).transform(self.config.variants) for _ in range(self.width)]

    def generate(self):
        """Fit the tree, I.E, generate variants"""
        # Empty levels
        self._levels = []
        # Get first variants
        first_variants = self._apply_level(self.original_text)
        # Append first level
        self._levels.append({self.original_text: first_variants})
        self.texts_lookup["0"] = self.original_text
        self.texts_lookup.update(
            {f"0:{ix}": first_variants[ix] for ix in range(len(first_variants))})
        self.edges.extend([("0", f"0:{ix}")
                          for ix in range(len(first_variants))])
        level_name = "0"
        # Keep track of remaining depth
        remaining_depth = self.depth - 1

        # Loop while there is reamining depth
        while remaining_depth >= 0:
            # Initialize new level
            new_level = {}
            # Gather values from last levels
            for values in self._levels[-1].values():
                for i_index, value in enumerate(values):
                    new_variants = self._apply_level(value)
                    new_level[value] = new_variants
                    # Build text lookup by iterating over variants
                    for j_index, variant in enumerate(new_variants):
                        self.texts_lookup[f"{level_name}:{i_index}:{j_index}"] = variant
                        # Store graph edges
                        self.edges.append(
                            (f"{level_name}:{i_index}", f"{level_name}:{i_index}:{j_index}"))
            # Append new level
            self._levels.append(new_level)
            # Increase level name
            level_name += f":{self.depth - remaining_depth - 1}"
            # Decrease remaining depth
            remaining_depth -= 1
        # Return self
        return self

    def dump(self, folder: str) -> None:
        """Dump the generated stemma into a folder:
            - The texts
            - The corresponding tree structure

        Args:
            folder (str): The folder where the text should be
                written.
        """
        Path(folder).mkdir(exist_ok=True)
        for file_name, file_content in self.texts_lookup.items():
            file_path = Path(folder) / f"{file_name.replace(':', '_')}.txt"
            with file_path.open("w") as f:
                f.write(file_content)
        with (Path(folder) / "edges.txt").open("w") as f:
            for edge in self.edges:
                f.write(f"{edge}\n")
