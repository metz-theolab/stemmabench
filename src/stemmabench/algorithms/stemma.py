import json
from pathlib import Path
from typing import Dict, List, Tuple, Union
from stemmabench.algorithms.manuscript import Manuscript
from stemmabench.algorithms.utils import Utils
import os


class Stemma:
    
    def __init__(
        self,
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
            !!! The labels used in the edge file must be the same as the name used for the text .txt names !!!
            generation_info (dict, optional): A dictionnary containing.

        Generation_info content:
            config: The path to the config file used to generate the tree.
            has_ground_truth: Boolean indicating if the true tree is known. If false the path_to_original attribute will indicate the 
            estimated original text.
        """
        self._path_to_folder = path_to_folder
        self._edge_file = edge_file
        self._generation_info = generation_info
        self._root = None
        self._text_lookup = {}
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
    def text_lookup(self):
        return self._text_lookup
    
    @property
    def generation_info(self):
        return self._generation_info
    
    def get_edges():
        """Return array of all the edge values."""
        raise NotImplemented

    def dict(self, include_edges = False) -> Dict[str, Union[List[str], Dict[str, List[str]]]]:
        """Return a dict representation of the tree.
        Dict is empty until tree is fitted (fitting can be done using .fit() method)
        """
        # TODO: Test if it works and see if include_edges parameter should be removed.
        if self.fitted == False:
            raise RuntimeError("Stemma not fitted yet.")
        return self.root.dict()
    
    def __eq__(self, value: object) -> bool:
        """Returns true if both stemmas are the same. !!! Only checks that both stemmas contain all the same texts !!!"""
        if isinstance(value, Stemma):
            # Check that both text_lookup exist and have same length.
            if self.text_lookup and value.text_lookup and len(self.text_lookup) == len(value.text_lookup):
                for lab in self.text_lookup:
                    if value.text_lookup.get(lab) == None or not self.text_lookup[lab].__eq__(value.text_lookup[lab]):
                        return False
                return True
        return False
    
    def __repr__(self) -> str:
        """String representation of the tree"""
        if self.fitted == True:
            return "Tree(" + json.dumps(self.dict(), indent=2) + ")"
        return "Empty"

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
            raise ValueError("This stemmas path_to_folder varaibles is not set. Therefor folder must be specified.")
        if not folder and self.path_to_folder:
            folder = self.path_to_folder
        if not os.path.isdir(folder):
                Path(folder).mkdir(exist_ok=True)
        for key in self.text_lookup:
            self.text_lookup[key].dump(folder)

    def compute(self,
                algo = None, # Use string of lambda.
                edge_file: Union[str, None] = None,
                path_to_folder: Union[str, None] = None, # Use just path to folder and look for edge_file
                generation_info: Union[Dict, None] = None,
                *args,
                **kargs) -> None:
        """Builds the stemma based on given algorithm or edge file. Builds the stemma in place. 
           Meaning it does not return anything.

        Args:
            algo (Algo, optinal): indicating the function used to build the tree.
            params (list, optinal): The list of parameters to be passed by the given function building the tree.
            edge_file (str, optional): Path to the edge file used to build the tree. If given will ignore all other parameters.
        """
        self._generation_info = generation_info
        if edge_file:
            if not path_to_folder:
                raise ValueError("If edge_file is specified path_to_folder must be specified.")
            self._path_to_folder = path_to_folder
            self._root = Manuscript(parent= None, recursive=Utils.dict_from_edge(edge_file))
            self._text_lookup = self._root.build_text_lookup()
            for text in self.text_lookup.values():
                text._text = Utils.load_text(self.path_to_folder + "/" + text.label + ".txt")
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