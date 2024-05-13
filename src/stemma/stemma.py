import json
from pathlib import Path
from typing import Dict, List, Tuple, Union
import os
# from stemmabench.config_parser import StemmaBenchConfig
# from stemmabench.textual_units.text import Text as text_util
#import src.utils
from stemma.manuscript_base import ManuscriptBase
from stemmabench.stemma.manuscript import Manuscript
from utils import dict_from_edge, load_text



#import stemma.manuscript
#import stemma.manuscript_base


class Stemma:
    
    def __init__(
        self,
        #root: ManuscriptBase = None, 
        path_to_folder: str = None,
        edge_file: str = None,
        generation_info: dict = None) -> None:
        """A class to perform variant generation.
        To instansite the class use one of the build methods.

        Args:
            root (ManuscriptBase, optional): The root text of the tree.
            path_to_folder (str, optional): The path to the folder that contains the texts.
            If the true original text is not known the path to the root text will be added here and
            that fact will be stated in the generation_info dictionary.
            edge_file (str, optional): An edge file from which the tree can be built.
            generation_info (dict, optional): A dictionnary containing.
            fitted (bool, required): Indicates if the tree has been built.

        Generation_info content:
            config: The path to the config file used to generate the tree.
            has_ground_truth: Boolean indicating if the true tree is known. If false the path_to_original attribute will indicate the 
            estimated original text.
        """
        #if root:
        #    self._root = root
        #    self._lookup = {}
        #    self.root.lookup(self._lookup)
        #    self._fitted = True
        #else:
        #    self._fitted = False

        if path_to_folder:
            self._path_to_folder = path_to_folder

        if edge_file:
            self._edge_file = edge_file

        if generation_info:
            self._generation_info = generation_info

        self._lookup = {}
        self._fitted = False

    # Getters
    @property
    def root(self):
        return self._root

    @property
    def path_to_folder(self):
        return self._path_to_folder
    
    @property
    def edge_file(self):
        return self._edge_file
    
    @property
    def fitted(self):
        return self._fitted
    
    @property
    def lookup(self):
        return self._lookup
    
    @property
    def generation_info(self):
        return self._generation_info
    
    def get_edges():
        """Return array of all the edges."""
        raise NotImplemented

    def dict(self, include_edges = False) -> Dict[str, Union[List[str], Dict[str, List[str]]]]:
        """Return a dict representation of the tree.
        Dict is empty until tree is fitted (fitting can be done using .fit() method)
        """
        # TODO: Test if it works and see if include_edges parameter should be removed.
        if not self.fitted:
            raise RuntimeError("Stemma not fitted yet.")
        return self.root.dict()
    
    def __eq__(self, value: object) -> bool:
        """Returns true if both stemmas are the same. !!! Uses the lookup table to judge """
        if isinstance(value, Stemma):
            # Check that both lookup exist and have same length.
            if self.lookup and value.lookup and len(self.lookup) == len(value.lookup):
                for lab in self.lookup:
                    if value.lookup.get(lab) == None or not self.lookup[lab].__eq__(value.lookup[lab]):
                        return False
                return True
        return False
    
    def __repr__(self) -> str:
        """String representation of the tree"""
        # TODO: Test print method.
        return "Tree(" + json.dumps(self.dict(), indent=2) + ")"

    def dump(self, folder: str = None) -> None:
        """Dump the generated stemma into a folder:
            - The texts in own file.
            - The corresponding tree structure in edge file.
            If folder is not specified will use the stemas path_to_folder attribute as path.

        Args:
            folder (str): The folder where the text should be written.

        Raises:
            Exception: If folder is not specified and the folder_path variable is not set.
        """

        # TODO: Test
        if not self.path_to_folder and not folder:
            raise RuntimeError("This stemmas path_to_folder varaibles is not set. Therefor folder must be specified.")
        if not folder and self.path_to_folder:
            folder = self.path_to_folder
        Path(folder).mkdir(exist_ok=True)
        self.root.dump(folder, recurcive=True)

    def compute(self,
                algo = None, # Use string of lambda.
                edge_file: str = None,
                path_to_folder: str = None, # Use just path to folder and look for edge_file
                *args,
                **kargs) -> None:
        """Builds the stemma based on given algorithm or edge file. Builds the stemma in place. 
           Meaning it does not return anything.

        Args:
            algo (Algo, optinal): indicating the function used to build the tree.
            params (list, optinal): The list of parameters to be passed by the given function building the tree.
            edge_file (str, optional): Path to the edge file used to build the tree. If given will ignore all other parameters.
        """
        if edge_file:
            # TODO: Construct stemma from edge file. (Used mainly for building the original.)
            # Build tree
            self._root = Manuscript(parent= None, recursive=dict_from_edge(edge_file))
            # Set lookup
            # TODO: Check if passed by reference
            self.root.build_lookup(self._lookup)
            # Set texts
            # TODO: Check that text can be accesed in this way
            for text in self.lookup.values():
                text.text = load_text(self.path_to_folder + "/" + text.label + ".txt")
            self._fitted = True
            self._edge_file = edge_file
        elif algo:
            raise RuntimeError("Not implemented yet!")
            if not path_to_folder:
                raise RuntimeError("If algo is used the path to the folder containing the manuscripts must be specified.")
            # TODO: Build tree using the stated algo present in the algo folder.
            self._fitted = True
        else:
            raise RuntimeError("At least one of edge_file or algo parameters must be specified.")