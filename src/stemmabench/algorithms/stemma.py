import json
from pathlib import Path
from typing import Dict, Union, Any
import os
from stemmabench.algorithms.manuscript_in_tree import ManuscriptInTree
from stemmabench.algorithms.manuscript_in_tree_empty import ManuscriptInTreeEmpty
from stemmabench.algorithms.manuscript_in_tree_base import ManuscriptInTreeBase
from stemmabench.algorithms.utils import Utils


class Stemma:
    """Class that represents a stemma tree.

    ### Attributes:
        - root (ManuscriptInTree): The root of the stemma tree.
        - folder_path (str): The path to the folder containing the texts for the stemma.
        - edge_file (str): The path to the .txt file that contains the edges for the stemma.
        - text_lookup (dict): Dictionary containing all the manuscripts contained in the stemma tree.
          With manuscript as labels as keys and reference of manuscripte as value.
        - fitted (bool): Indicates if the stemma has been built.
        - generation_info (dict): Dictionary containing info about how the tree was generated.
    """

    def __init__(self,
                 folder_path: str,
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
        self._root: Union[ManuscriptInTreeBase, None] = None
        self._text_lookup: Dict[str, ManuscriptInTreeBase] = {}
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

    def _set_folder_path(self, folder_path: str) -> None:
        """Checks that the folder path is an existing directory and sets the folder_path attribute.

        ### Args:
            - folder_path (str): The path to the folder containing all the texts.

        ### Raises:
            - ValueError: If the specified folder_path is not an existing directory.
        """
        if not os.path.isdir(folder_path):
            raise ValueError(f"{folder_path} is not an existing folder path.")
        self._folder_path = folder_path

    def get_edges(self) -> None:
        """Return array of all the edge values.

        ### Raises:
            - NotImplementedError: Not implemented yet.
        """
        raise NotImplementedError

    def dict(self, include_edges: bool = False) -> Dict[str, Any]:
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
        # TODO: This method is a placeholder until a better definition of equality can be found.

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

    def dump(self, folder: str) -> None:
        """Dump the generated stemma into a folder:
            - The texts in .txt file named after the manuscript label.
            - The corresponding tree structure in edge file.
            If folder is not specified will use the stemas path_to_folder attribute as path.

        ### Args:
            - folder (str): The folder where the text should be written.

        ### Raises:
            - RuntimeError: If was unable to create directory.
        """
        if not os.path.isdir(folder):
            try:
                Path(folder).mkdir(exist_ok=True)
            except:
                raise RuntimeError(
                    f"Was unable to create the directory {folder}.")
        fedge = open("edges.txt", "w")
        for key in self.text_lookup:
            for child in self.text_lookup[key].children:
                fedge.write(f"({self.text_lookup[key].label},{child.label})\n")
            if isinstance(self.text_lookup[key], ManuscriptInTree):
                ftext = open(f"{self.text_lookup[key].label}.txt", "w")
                ftext.write(self.text_lookup[key].text)
                ftext.close()

    def compute(self,
                algo: Any = None,
                edge_file: Union[str, None] = None,
                generation_info: Dict[str, Any] = {},
                *args,
                **kargs) -> None:
        """Builds the stemma based on given algorithm or edge file. Builds the stemma in place. 
           Meaning it does not return anything.

        ### Args:
            - algo (StemmaAlgo, Optional): indicating the function used to build the tree.
            - edge_file (str, Optional): Path to the edge file used to build the tree. If given will ignore all other parameters.
            If specified with the algo perameter this path will overwrite all other
            - **kargs: The parameters to be passed to the algo parameter for the stemma generation.

        ### Raises:
            - RuntimeError: If both edge_file and algo pararmeters are unspecified.
        """
        self._generation_info = generation_info
        if edge_file:
            text_list = Utils.get_text_list(self.folder_path)
            generation_dict = Utils.dict_from_edge(edge_path=edge_file)
            if list(generation_dict.keys())[0] in text_list:
                self._root = ManuscriptInTree(
                    parent=None, recursive=generation_dict, text_list=text_list)
            else:
                self._root = ManuscriptInTreeEmpty(
                    parent=None, recursive=generation_dict, text_list=text_list)
            self._text_lookup = self._root.build_text_lookup()
            for text in self.text_lookup.values():
                if isinstance(text, ManuscriptInTree):
                    text._text = Utils.load_text(
                        self.folder_path + "/" + text.label + ".txt")
            self._fitted = True
            self._edge_file = edge_file
        elif algo:
            self._root = algo.compute(
                folder_path=self.folder_path, *args, **kargs)
            self._text_lookup = self._root.build_text_lookup()
            for text in self.text_lookup.values():
                if isinstance(text, ManuscriptInTree):
                    text._text = Utils.load_text(
                        self.folder_path + "/" + text.label + ".txt")
            self._fitted = True
        else:
            raise RuntimeError(
                "At least one of edge_file or algo parameters must be specified.")
