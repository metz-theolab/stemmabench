import json
from pathlib import Path
from typing import Dict, List, Tuple, Union

import numpy as np
from stemmabench.config_parser import StemmaBenchConfig
from stemmabench.textual_units.text import Text as text_util
from algorithms.text import Text

class Stemma:
    
    def __init__(
        self,
        root: text = None,
        path_to_folder: str = None,
        path_to_original: str = None, 
        edge_file: str = None,
        generation_info: dict = None,
        fitted: bool = False,
    ) -> None:
        """A class to perform variant generation.
        To instansite the class use one of the build methods.

        Args:
            text (Text, optional): The root text of the tree.
            path_to_folder (str, optional): The path to the folder that contains the texts.
            path_to_original (str, optional): The name of the txt file containing the original text.
            If the true original text is not known the path to the root text will be added here and
            that fact will be stated in the generation_info dictionary.
            edge_file (str, optional): An edge file from which the tree can be built.
            generation_info (dict, optional): A dictionnary containing.
            fitted (bool, required): Indicates if the tree has been built.

        Generation_info content:
            config: The path to the config file used to generate the tree.
            has_ground_truth: Boolean indicating if the true tree is known. If false the path_to_original attribute will indicate the 
            estimated original text.

        Raises:
            Exception: If no nodes dictionary specified.
            Exception: If no folder path specified.
            Exception: If no original text path specified.
        """

        self._fitted = fitted

        if fitted:

            if root:
                self._root = root
            else:
                raise TypeError("No root specified.")

            if path_to_folder:
                self._path_to_folder = path_to_folder
            else:
                raise TypeError("No folder path specified.")

            if path_to_original:
                self._path_to_original = path_to_original
            else:
                raise TypeError("No original text path specified.")


            if edge_file:
                self._edge_file = edge_file

            if generation_info:
                self._generation_info = generation_info




    # Build edges and nodes from edge_file


    # Getters
    @property
    def root(self):
        return self._root

    @property
    def path_to_folder(self):
        return self._path_to_folder
    
    @property
    def path_to_original(self):
        return self._path_to_original
    
    @property
    def edge_file(self):
        return self._edge_file
    
    @property
    def fitted(self):
        return self._fitted
    
    def edges(format: str = "dict"):
        """Returns representation of the edges of the tree in the specified format.

        Args:
            format (str, optional): Specifies the format of the edge representation.
            Accepted values are:
            - "disct"

        Returns:
            Edges in specified format.
        """
        pass


    # Setters
    @root.setter
    def root(self, root):
        # TODO: add checks
        self._root = root

    @path_to_folder.setter
    def path_to_folder(self, path_to_folder):
        # TODO: add checks
        self._path_to_folder = path_to_folder

    @path_to_original.setter
    def path_to_original(self, path_to_original):
        # TODO: add checks
        self._path_to_original = path_to_original

    @edge_file.setter
    def edge_file(self, edge_file):
        # TODO: check file exists
        self._edge_file = edge_file

    @fitted.setterd 
    def fitted(self, fitted):
        # TODO: add checks
        self._fitted = fitted

    ####################### Methods for generating the original stemma #########################
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
        else:
            raise ValueError("Only Gaussian and Uniform laws are supported.")

    def dict(self) -> Dict[str, Union[List[str], Dict[str, List[str]]]]:
        """Return a dict representation of the tree.
        Dict is empty until tree is fitted (fitting can be done using .fit() method)
        """
        return self.root.to_dict()
    
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
        n_mss_to_delete = int(self.missing_manuscripts_rate * len(self.texts_lookup))
        # Select the manuscripts to delete.
        mss_list = list(self.texts_lookup)
        missing_mss = np.random.choice(mss_list, n_mss_to_delete, replace=False)
        # Subset non-missing manuscripts and non-missing edges.
        mss_non_missing = {mss_id: mss_text
                           for mss_id, mss_text in self.texts_lookup.items()
                           if mss_id not in missing_mss}
        edges_non_missing = [
            edge for edge in self.edges
            if all(node not in missing_mss for node in edge)
        ]
        return mss_non_missing, edges_non_missing

    def generate(self):
        """Fit the tree, I.E, generate variants (Used to generate the "original" tree)"""

        if self.fitted:
            raise RuntimeError("This stemma has already been generated!")

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
                file_path = missing_tradition_folder / f"{file_name.replace(':', '_')}.txt"
                with file_path.open("w", encoding="utf-8") as f:
                    f.write(file_content)
            with (missing_tradition_folder / "edges_missing.txt").open("w", encoding="utf-8") as f:
                for edge in miss_edges:
                    f.write(f"{edge}\n")

    

    ####################### Methods for generating the estimated stemma #########################


    pass