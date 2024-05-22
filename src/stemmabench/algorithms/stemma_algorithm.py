import os
from typing import Union, Dict
from stemmabench.algorithms.manuscript import Manuscript


class StemmaAlgo:
    """Base class for all th stemma algorithmes.

    ### Attributes:
        - folder_path (str): The path to the folder containing all the texts.
        - manuscripts (dict): The dictionay of all the texts with text labels as keys and texts as values.
        This is what is ued to build the stemmas.
    """

    def __init__(self, 
                 folder_path: Union[str, None] = None) -> None:
        """StemmaAlgo constructor.

        ### Args:
            - folder_path (str, Optional): The path to the folder containing the texts. 
            !!! All .txt files in this folder must be files containing Manuscript texts unless the file name contains the substring "edge" !!!
        """
        if folder_path:
            self._set_from_folder_path(folder_path)
        else:
            self._folder_path: Union[str, None] = None
            self._manuscripts: Dict[str, str] = {}

    @property
    def folder_path(self):
        return self._folder_path
    
    @property
    def manuscripts(self):
        return self._manuscripts
    
    def _set_from_folder_path(self, folder_path: Union[str, None] = None) -> None:
        """Setter for all attributs that rely on the folder path.
        
        ### Args:
            - folder_path (str): The path to the folder containing all the texts.

        ### Raises:
            - ValueError: If folder_path not specified.
            - RuntimeError: If the given folder_path is not an existing directory.
        """
        if not folder_path:
            raise ValueError("No folder_path specified.")
        if not os.path.isdir(folder_path):
            raise RuntimeError("The given path is not an existing directory.")
        self._folder_path = folder_path
        self._manuscripts = {}
        files: list[str] = list(filter(lambda x: "edge" not in x and os.path.isfile(folder_path + "/" + x) and ".txt" in x, 
                                       os.listdir(folder_path)))
        for text in files:
            self._manuscripts.update({text.replace(".txt", ""): open(folder_path + "/" + text, "r").read()})

    def compute(self, folder_path: Union[str, None] = None, *arg, **kwarg) -> Manuscript:
        """Builds the stemma tree. The implementation at this level only checks the inputs and sets the attributes.

        ### Args:
            - folder_path (str, Optional): The path to the folder containing the texts. The path specified here will surplant the previous path defined in constructor and will be set as new path_folder attribute.
            !!! All .txt files in this folder must be files containing Manuscript texts unless the file name contains the substring "edge" !!!
        
        ### Returns:
            - Manuscript: The root of the stemma with the rest of its tree as its children.

        ### Raises:
            - ValueError: If both the folder_path parameter and the object _folder_path attribute have not been specified.
        """
        if folder_path == None and self.folder_path == None:
            raise ValueError("The attribute folder_path has not been initialized for this instance. Therefore folder_path must be specified.")
        self._set_from_folder_path(folder_path)
    
    def _build_edges(self) -> list[list[str]]:
        """Builds a list representation of stemma tree edges.
        This is where the algorythmes are implemented.

        ### Returns:
            - list: List of all the edges from the stemma tree constructed by the algorythm.

        ### Raises:
            - NotImplementedError: Method not implemented for this class.
        """
        raise NotImplementedError()

    def __eq__(self, value: object) -> bool:
        """Tests equality with an other object.

        ### Args:
            - value (object): The object to be compared to the calling object.

        ### Returns:
            - bool: Value indicating if the calling object and the value parameter are equal.

        ### Raises:
            NotImplementedError: Method not implemented for this class.
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """Returns a string representation of this object.

        ### Returns:
            str: String representation of the object.

        ### Raises:
            - NotImplementedError: Method not implemented for this class.
        """
        raise NotImplementedError()
