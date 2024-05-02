from pathlib import Path ######################## Remove
from stemma.manuscript_base import ManuscriptBase
from utils import load_text


class Manuscript(ManuscriptBase):
    """Class for the representation of an existing manuscript in a stemma tree.
    """

    def __init__(self,
                 label: str,
                 text_path: str,
                 text: str,
                 parent: "Manuscript",
                 children: list["ManuscriptBase"] = None,
                 edges: list[float] = None) -> None:
        """A class representing the Manuscripts that make up the nodes of a stemma.

        Args:
            label (str, reqired): The label denoting the text.
            text_path (str, reqired): The name of the txt file containing the text. 
            (The name of the folder containing the txt files will be taken from the stemma class.)
            text (str, required): The contense of the text. If set to None this represents a missing text.
            parent (text, optional): The parent text of the curent text.
            children (list, optional): A list of this Manuscripts children.
            edges (list, Optional): A list representing the distance between the edges. 
            In the same order as the children array.

        Raises:
            Exception: If no input text is specified.
        """
        super().__init__(self, label, parent, children, edges)
        
        if text_path:
            self._text_path = text_path
        else:
            raise TypeError("No text path specified.")
        
        if text:
            self._text = load_text(text_path)
        else:
            raise TypeError("No input text specified.")

    # Getters
    @property
    def text_path(self):
        return self._text_path
    
    @property
    def text(self):
        return self._text
        
    def __eq__(self, value: object) -> bool:
        """Returns True if both texts have the same contents.
        !!! Returns True if both texts are missing !!!

        Args:
            value (object, requiered): The object to compare to.
        """
        if isinstance(value, Manuscript):
            return value.text == self.text
        return False
