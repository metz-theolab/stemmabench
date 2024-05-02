import json
from pathlib import Path
from typing import Dict, List, Tuple, Union
from stemmabench.config_parser import StemmaBenchConfig
from stemmabench.textual_units.text import Text as text_util
from stemma.manuscript_base import ManuscriptBase


class Stemma:
    
    def __init__(
        self,
        root: ManuscriptBase = None, 
        path_to_folder: str = None,
        path_to_original: str = None, 
        edge_file: str = None,
        generation_info: dict = None,
        fitted: bool = False, # TODO: Simply check if root is set to None instead.
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

    def dict(self, include_edges = False) -> Dict[str, Union[List[str], Dict[str, List[str]]]]:
        """Return a dict representation of the tree.
        Dict is empty until tree is fitted (fitting can be done using .fit() method)
        """
        # TODO: Test if it works and see if include_edges parameter should be removed.
        return self.root.dict()
    
    def __repr__(self) -> str:
        """String representation of the tree"""
        # TODO: Test print method.
        return "Tree(" + json.dumps(self.dict(), indent=2) + ")"

    def dump(self, folder: str) -> None:
        """Dump the generated stemma into a folder:
            - The texts
            - The corresponding tree structure

        Args:
            folder (str): The folder where the text should be written.
        """
        # TODO: Fix dump method.
        Path(folder).mkdir(exist_ok=True)
        for file_name, file_content in self.texts_lookup.items():
            file_path = Path(folder) / f"{file_name.replace(':', '_')}.txt"
            with file_path.open("w", encoding="utf-8") as f:
                f.write(file_content)
        with (Path(folder) / "edges.txt").open("w", encoding="utf-8") as f:
            for edge in self.edges:
                f.write(f"{edge}\n")

    def compute(self,
                algo = None, # Use string of lambda.
                params: list = None,
                edge_file: str = None) -> None:
        """Builds the stemma based on given algorithm or edge file. Builds the stemma in place. 
           Meaning it does not return anything.

        Args:
            algo (, optinal): indicating the function used to build the tree.
            params (list, optinal): The list of parameters to be passed by the given function building the tree.
            edge_file (str, optional): Path to the edge file used to build the tree. If given will ignore all other parameters.

        """
        if edge_file:
            # TODO: Construct stemma from edge file. (Used mainly for building the original.)
            self._fitted = True

        elif algo:
            # TODO: Build tree using the stated algo present in the algo folder.
            self._fitted = True

        else:
            raise TypeError("At least one of the folowing edge_file, algo must be specified.")