import os
from typing import Dict, List
from stemmabench.algorithms.manuscript_in_tree import ManuscriptInTree


class StemmaAlgo:
    """Base class for all th stemma algorithmes.

    ### Attributes:
        - folder_path (str): The path to the folder containing all the texts.
        - manuscripts (dict): The dictionay of all the texts with text labels as keys and texts as values.
        This is what is ued to build the stemmas.
    """

    def __init__(self) -> None:
        """StemmaAlgo constructor.
        """
        self._manuscripts: Dict[str, str] = {}

    @property
    def manuscripts(self):
        return self._manuscripts

    def compute(self, folder_path: str, *arg, **kwarg) -> ManuscriptInTree:
        """Builds the stemma tree. The implementation at this level only checks the inputs and sets the attributes.

        ### Args:
            - folder_path (str): The path to the folder containing the texts. The path specified here will surplant the previous path defined in constructor and will be set as new path_folder attribute.
            !!! All .txt files in this folder must be files containing Manuscript texts unless the file name contains the substring "edge" !!!

        ### Returns:
            - Manuscript: The root of the stemma with the rest of its tree as its children.

        ### Raises:
            - RuntimeError: If folder_path is not an existing directory.
        """
        if not os.path.isdir(folder_path):
            raise RuntimeError(f"{folder_path} is not an existing directory.")
        files: List[str] = list(filter(lambda x: "edge" not in x and os.path.isfile(folder_path + "/" + x) and ".txt" in x,
                                       os.listdir(folder_path)))
        for text in files:
            self._manuscripts.update(
                {text.replace(".txt", ""): open(folder_path + "/" + text, "r").read()})

    def _build_edges(self) -> List[List[str]]:
        """Builds a list representation of stemma tree edges.
        This is where the algorythmes are implemented.

        ### Returns:
            - list: List of all the edges from the stemma tree constructed by the algorythm.

        ### Raises:
            - NotImplementedError: Method not implemented for this class.
        """
        raise NotImplementedError

    def __eq__(self, value: object) -> bool:
        """Tests equality with an other object.

        ### Args:
            - value (object): The object to be compared to the calling object.

        ### Returns:
            - bool: Value indicating if the calling object and the value parameter are equal.

        ### Raises:
            NotImplementedError: Method not implemented for this class.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """Returns a string representation of this object.

        ### Returns:
            str: String representation of the object.

        ### Raises:
            - NotImplementedError: Method not implemented for this class.
        """
        raise NotImplementedError
