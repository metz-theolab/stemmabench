import json
from pathlib import Path
from typing import Dict, List, Union
from stemmabench.algorithms.manuscript import Manuscript
from stemmabench.algorithms.manuscript_base import ManuscriptBase
from stemmabench.algorithms.utils import Utils
#from stemmabench.algorithms.stemma_algorithm import StemmaAlgo
import os


class Stemma:
    """Class that represents a stemma tree."""

    def __init__(self,
                 folder_path: str = None,
                 edge_file: str = None,
                 generation_info: dict = None) -> None:
        """A class to perform variant generation.
        To instansite the class use one of the build methods.

        Args:
            folder_path(str, Optional): The path to the folder that contains the texts.
            edge_file (str, Optional): An edge file from which the tree can be built. 
            !!! The labels used in the edge file must be the same as the name used for the text .txt names !!!
            generation_info (dict, Optional): A dictionnary containing information about the stemma's generation.

        Generation_info content:
            config: The path to the config file used to generate the tree.
            has_ground_truth: Boolean indicating if the true tree is known. If false the path_to_original attribute will indicate the 
            estimated original text.
        """
        self._set_folder_path(folder_path=folder_path)
        self._edge_file: str = edge_file
        self._generation_info: dict = generation_info
        self._root: ManuscriptBase = None
        self._text_lookup: dict[str, ManuscriptBase] = {}
        self._fitted: bool = False

    @property
    def root(self):
        return self._root

    @property
    def folder_path(self):
        return self._folder_path
    
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
    
    def _set_folder_path(self, folder_path: str):
        """Checks that the folder path is an existing directory and sets the folder_path attribute.
        
        Args:
            folder_path (str, Requiered): The path to the folder containing all the texts.

        Raises:
            ValueError: If the specified folder_path is not an existing directory.
        
        """
        if folder_path != None and not os.path.isdir(folder_path):
            raise ValueError("The folder_path specified is not an existing folder path.")
        self._folder_path = folder_path
    
    def get_edges(self):
        """Return array of all the edge values."""
        raise NotImplementedError()

    def dict(self, include_edges = False) -> Dict[str, Union[List[str], Dict[str, List[str]]]]:
        """Return a dict representation of the tree.
        Dict is empty until tree is fitted (fitting can be done using .fit() method)
        """
        if self.fitted == False:
            raise RuntimeError("Stemma not fitted yet.")
        return self.root.dict(include_edges)
    
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
        if not self.folder_path and not folder:
            raise ValueError("This stemmas path_to_folder varaibles is not set. Therefor folder must be specified.")
        if not folder and self.folder_path:
            folder = self.folder_path
        if not os.path.isdir(folder):
                Path(folder).mkdir(exist_ok=True)
        for key in self.text_lookup:
            self.text_lookup[key].dump(folder)

    def compute(self,
                algo = None,
                edge_file: Union[str, None] = None,
                folder_path: Union[str, None] = None,
                generation_info: Union[Dict, None] = None,
                *args,
                **kargs) -> None:
        """Builds the stemma based on given algorithm or edge file. Builds the stemma in place. 
           Meaning it does not return anything.

        Args:
            algo (StemmaAlgo, Optinal): indicating the function used to build the tree.
            edge_file (str, Optional): Path to the edge file used to build the tree. If given will ignore all other parameters.
            folder_path (str, Optional): The path to the folder containing all the stemma texts. 
            If specified with the algo perameter this path will overwrite all other
            **kargs: The parameters to be passed to the algo parameter for the stemma generation.
        """
        # TODO: Test kargs parameter passing. (width)
        self._generation_info = generation_info
        if edge_file:
            if not folder_path:
                raise ValueError("If edge_file is specified path_to_folder must be specified.")
            self._folder_path = folder_path
            self._root = Manuscript(parent= None, recursive=Utils.dict_from_edge(edge_path=edge_file))
            self._text_lookup = self._root.build_text_lookup()
            for text in self.text_lookup.values():
                text._text = Utils.load_text(self.folder_path + "/" + text.label + ".txt")
            self._fitted = True
            self._edge_file = edge_file
        elif algo:
            # Implemented in next Pull Request
            raise NotImplementedError()
            if folder_path != None:
                self._set_folder_path(folder_path=folder_path)
            elif self.folder_path != None:
                folder_path = self.folder_path
            elif algo.folder_path != None:
                folder_path = algo.folder_path
                self._set_folder_path(folder_path=algo.folder_path)
            else:
                raise RuntimeError("The folder_path is not specified as an attribute of this stemma instance or as an attribute of the algo parameter instance. Therefore the parameter folder_path must be specified.")  
            self._root = algo.compute(folder_path=folder_path,*args,**kargs)
            self._text_lookup = self._root.build_text_lookup()
            for text in self.text_lookup.values():
                text._text = Utils.load_text(folder_path + "/" + text.label + ".txt")
            self._fitted = True
        else:
            raise RuntimeError("At least one of edge_file or algo parameters must be specified.")