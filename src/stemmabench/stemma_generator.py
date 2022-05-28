"""Class to perform the variant simulation.
"""
from posixpath import split
import json
from typing import Dict, List, Union
from stemmabench.textual_units import text


def identity(string: str) -> str:
    return string


class VariantTree:
    """Class to generate an ensemble of manuscript.
    """

    def __init__(
        self,
        original_text: str,
        depth: int = 3,
        width: int = 4,
        config: Dict[str, str] = {}
    ) -> None:
        """A class to perform variant generation.
        Use the .fit() method to actually perform variant generation.
        """
        self.original_text = original_text
        self.depth = depth
        self.width = width
        self.config = config
        self._levels: List[Dict[str, List[str]]] = []

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

    def _apply_once(self, value: str) -> List[str]:
        """Apply transformation on a single value"""
        return [text(value).transform(**self.config) for _ in range(self.width)]

    def generate(self):
        """Fit the tree, I.E, generate variants"""
        # Empty levels
        self._levels = []
        # Get first variants
        first_variants = self._apply_once(self.original_text)
        # Append first level
        self._levels.append({self.original_text: first_variants})
        # Keep track of remaining depth
        remaining_depth = self.depth - 1
        # Loop while there is reamining depth
        while remaining_depth >= 0:
            # Initialize new level
            new_level: Dict[str, List[str]] = {}
            # Gather values from last levels
            for values in self._levels[-1].values():
                for value in values:
                    new_variants = self._apply_once(value)
                    new_level[value] = new_variants
            # Append new level
            self._levels.append(new_level)
            # Decrease remaining depth
            remaining_depth -= 1
        # Return self
        return self
