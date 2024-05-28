import json
from pathlib import Path
from typing import Dict, List, Union, Any
from stemmabench.algorithms.manuscript import Manuscript
from stemmabench.algorithms.manuscript_base import ManuscriptBase
from stemmabench.algorithms.manuscript_empty import ManuscriptEmpty
from stemmabench.algorithms.utils import Utils
from stemmabench.algorithms.stemma_algorithm import StemmaAlgo
import os


class Stemma:
    """Class that represents a stemma tree.
    
    ### Attributes:
        - root (Manuscript): The root of the stemma tree.
        - folder_path (str): The path to the folder containing the texts for the stemma.
        - edge_file (str): The path to the .txt file that contains the edges for the stemma.
        - text_lookup (dict): Dictionary containing all the manuscripts contained in the stemma tree.
          With manuscript as labels as keys and reference of manuscripte as value.
        - fitted (bool): Indicates if the stemma has been built.
        - generation_info (dict): Dictionary containing info about how the tree was generated.
    """

    def __init__(self,
                 folder_path: Union[str, None] = None,
                 edge_file: Union[str, None] = None,
                 generation_info: Dict[str, Any] = {}) -> None:
        """A class to perform variant generation.
        To instansite the class use one of the build methods.

        ### Args:
            - folder_path (str, Optional): The path to the folder that contains the texts.
            - edge_file (str, Optional): An edge file from which the tree can be built. 
            !!! The labels used in the edge file must be the same as the name used for the text .txt names !!!
            - generation_info (dict, Optional): A dictionnary containing information about the stemma's generation.

        ### Generation_info:
            This dictionary is ment to contain all manner of miscellaneous information relating to the generation of the stemma.
            The following section is a suggestion of the possible contents of the dictionary.
        #### Content:
            - config (str, Optional): The path to the config file used to generate the tree.
            - has_ground_truth (bool, Optional): Boolean indicating if the true tree is known. If false the path_to_original attribute will indicate the 
            estimated original text.
        """
        self._set_folder_path(folder_path=folder_path)
        self._edge_file: Union[str, None] = edge_file
        self._generation_info: Union[Dict[str, Any], None] = generation_info
        self._root: Union[ManuscriptBase, None] = None
        self._text_lookup: Dict[str, ManuscriptBase] = {}
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
    
    def _set_folder_path(self, folder_path: Union[str, None]) -> None:
        """Checks that the folder path is an existing directory and sets the folder_path attribute.
        
        ### Args:
            - folder_path (str): The path to the folder containing all the texts.

        ### Raises:
            - ValueError: If the specified folder_path is not an existing directory.
        """
        if folder_path and not os.path.isdir(folder_path):
            raise ValueError("The folder_path specified is not an existing folder path.")
        self._folder_path = folder_path
    
    def get_edge_values(self) -> Dict[str, float]:
        """Return dictionary with edges as keys an edge distances as values.
        
        ### Returns:
            - dict: Dictionary with edges as keys and edge distances as values.
        """
        out = {}
        for key in self.text_lookup:
            for i in range(len(self.text_lookup[key].edges)):
                out.update({self.text_lookup[key].label + "," + self.text_lookup[key].children[i].label: self.text_lookup[key].edges[i]})
        return out
    
    def to_edge_list(self) -> list[list[str]]:
        """Returns a list of edges. Uses the text_lookup attribute to generate list.
        
        ### Returns:
            - list: A list of lists containing all the edges of the stemma.
        """
        out = []
        for key in self.text_lookup:
            for child in self.text_lookup[key].children:
                out.append([self.text_lookup[key].label, child.label])
        return out

    def dict(self, include_edges: bool = False) -> Dict[str, dict]:
        """Return a dict representation of the tree.
        Dict is empty until tree is fitted (fitting can be done using .fit() method)

        ### Args:
            - include_edges (bool): Indicates if the dictionary should include

        ### Returns:
            - dict: A dictionay representaion of the calling stemma tree.

        ### Raises:
            - RuntimeError: If the stemma has not been fited yet.
        """
        if not self.fitted:
            raise RuntimeError("Stemma not fitted yet.")
        return self.root.dict(include_edges)
    
    def __eq__(self, value: object) -> bool:
        """Returns true if both stemmas are the same. !!! Only checks that both stemmas contain all the same texts !!!
        
        ### Args:
            - value (object): The object to be compared to the calling Stemma.

        ### Returns:
            - bool: Value indicating if the calling object and the value parameter are equal.
        """
        if isinstance(value, Stemma):
            # Check that both text_lookup exist and have same length.
            if self.text_lookup and value.text_lookup and len(self.text_lookup) == len(value.text_lookup):
                for lab in self.text_lookup:
                    if value.text_lookup.get(lab) == None or not self.text_lookup[lab].__eq__(value.text_lookup[lab]):
                        return False
                return True
        return False
    
    def __repr__(self) -> str:
        """String representation of the tree."""
        if self.fitted:
            return "Tree(" + json.dumps(self.dict(), indent=2) + ")"
        return "Empty"

    def dump(self, folder: Union[str, None] = None,
             edge_file: Union[str, None] = None,
             dump_edges: bool = True,
             dump_texts: bool = True) -> None:
        """Dump the generated stemma into a folder:
            - The texts in .txt file named after the manuscript label.
            - The corresponding tree structure in edge file.
            If folder is not specified will use the stemas path_to_folder attribute as path.

        ### Args:
            - folder (str, Optional): The folder where the text should be written.
            - edge_file (str, Optional): The name of the edge file in which the edges will be placed.
            - dump_edges (bool, Optional): Value indicating if the edges file should be dumped.
            - dump_texts (bool, Optional): Value indicating if the all the texts should be dumped.

        ### Raises:
            - ValueError: If folder is not specified and the folder_path variable is not set.
        """
        if not self.folder_path and not folder:
            raise ValueError("This stemmas path_to_folder varaibles is not set. Therefor folder must be specified.")
        if not folder and self.folder_path:
            folder = self.folder_path
        if not os.path.isdir(folder):
                Path(folder).mkdir(exist_ok=True)
        if not edge_file:
            edge_file = "edges.txt"
        if dump_edges:
            fedge = open(folder + "/" + edge_file, "w")
        for key in self.text_lookup:
            if dump_edges:
                for child in self.text_lookup[key].children:
                    fedge.write("('" + self.text_lookup[key].label + "','" + child.label + "')\n")
            if dump_texts and isinstance(self.text_lookup[key], Manuscript):
                ftext = open(folder + "/" + self.text_lookup[key].label + ".txt", "w")
                ftext.write(self.text_lookup[key].text)
                ftext.close()
        if dump_edges:
            fedge.close()

    def compute(self,
                algo: Union[StemmaAlgo, None] = None,
                edge_file: Union[str, None] = None,
                folder_path: Union[str, None] = None,
                generation_info: Union[Dict[str, Any], None] = None,
                *args,
                **kwargs) -> None:
        """Builds the stemma based on given algorithm or edge file. Builds the stemma in place. 
           Meaning it does not return anything.

        ### Args:
            - algo (StemmaAlgo, Optinal): indicating the function used to build the tree.
            - edge_file (str, Optional): Path to the edge file used to build the tree. If given will ignore all other parameters.
            - folder_path (str, Optional): The path to the folder containing all the stemma texts. 
            If specified with the algo perameter this path will overwrite all other
            - **kargs: The parameters to be passed to the algo parameter for the stemma generation.

        ### Raises:
            - ValueError: If edge_file is specified and path_to_folder is not specified.
            - RuntimeError: If folder_path is not specified and both the _folder_path attribute and the algo folder_path attribute are set to None.
            - RuntimeError: If both edge_file and algo pararmeters are unspecified.
        """
        self._generation_info = generation_info
        if edge_file:
            if not folder_path:
                raise ValueError("If edge_file is specified path_to_folder must be specified.")
            self._folder_path = folder_path
            text_list = Utils.get_text_list(self.folder_path)
            generation_dict = Utils.dict_from_edge(edge_path=edge_file)
            if list(generation_dict.keys())[0] in text_list:
                self._root = Manuscript(parent= None, recursive=Utils.dict_from_edge(edge_path=edge_file), text_list=text_list)
            else:
                self._root = ManuscriptEmpty(parent= None, recursive=Utils.dict_from_edge(edge_path=edge_file), text_list=text_list)
            self._text_lookup = self._root.build_text_lookup()
            for manuscript in self.text_lookup.values():
                if isinstance(manuscript, Manuscript):
                    manuscript._text = Utils.load_text(self.folder_path + "/" + manuscript.label + ".txt")
            self._fitted = True
            self._edge_file = edge_file
        elif algo:
            if folder_path:
                self._set_folder_path(folder_path=folder_path)
            elif self.folder_path:
                folder_path = self.folder_path
            elif algo.folder_path:
                folder_path = algo.folder_path
                self._set_folder_path(folder_path=algo.folder_path)
            else:
                raise RuntimeError("The folder_path is not specified as an attribute of this stemma instance or as an attribute of the algo parameter instance. Therefore the parameter folder_path must be specified.")  
            self._root = algo.compute(folder_path=folder_path,**kwargs)
            self._text_lookup = self._root.build_text_lookup()
            for manuscript in self.text_lookup.values():
                if isinstance(manuscript, Manuscript):
                    manuscript._text = Utils.load_text(folder_path + "/" + manuscript.label + ".txt")
            self._fitted = True
        else:
            raise RuntimeError("At least one of edge_file or algo parameters must be specified.")