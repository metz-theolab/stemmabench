"""This module generates an artificial stemma given an initial text. 
"""
import json
from typing import Dict, List, Union
from random import uniform, gauss
from stemmabench.config_parser import StemmaBenchConfig, VariantConfig
from stemmabench.textual_units.text import Text


class Stemma:
    """Class to generate an artificial textual tradition,
    given a configuration file.
    """

    def __init__(
        self,
        original_text: str,
        config: StemmaBenchConfig
    ) -> None:
        """A class to perform variant generation.
        Use the .fit() method to actually perform variant generation.
        """
        self.original_text = original_text
        self.depth = config.stemma.depth
        self.config = config
        self._levels: List[Dict[str, List[str]]] = []

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
        # Keep track of remaining depth
        remaining_depth = self.depth - 1
        # Loop while there is reamining depth
        while remaining_depth >= 0:
            # Initialize new level
            new_level = {}
            # Gather values from last levels
            for values in self._levels[-1].values():
                for value in values:
                    new_variants = self._apply_level(value)
                    new_level[value] = new_variants
            # Append new level
            self._levels.append(new_level)
            # Decrease remaining depth
            remaining_depth -= 1
        # Return self
        return self

    def vizualize(self):
        """Vizualize the tree using a DAG representation.
        """
