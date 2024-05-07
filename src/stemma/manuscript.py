from pathlib import Path ######################## Remove
from stemma.manuscript_base import ManuscriptBase
from src.utils import load_text


class Manuscript(ManuscriptBase):
    """Class for the representation of an existing manuscript in a stemma tree.
    """

    def __init__(self,
                 label: str,
                 text_path: str,
                 text: str,
                 parent: "Manuscript",
                 children: list["ManuscriptBase"] = None,
                 edges: list[float] = None,
                 recursive: list[list[str, str],list[str, str]] = None) -> None:
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
            recursive (list[str], Optional): If different than None will buil all the children of the manuscript
            from the given list. 

        Raises:
            Exception: If no input text is specified.
        """
        if recursive:
            super().__init__(self, parent, recursive)
            return

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

    def dump(self, 
             folder_path: str,  
             recurcive: bool = False) -> None:
        """Writes the manuscripts contents to a txt file in the given folder.
            If file already exists will overwrite file.
            If the folder does not exist it will be created.
            If the edge file does not existe it will be created.
            Will look through edge file if it exists to check that edge is alredy present in edge file. 
            If True will not wirte individual edge to file.
        
        Args:
            folder_path (str, Required): The path the folder where the text file will be writen.
            recurcive (bool, Otional): Indicates if the dump should be propagated to all children recursively.
        """

        Path(folder_path).mkdir(exist_ok=True)
        file_path = Path(folder_path) / f"{self.label.replace(':', '_')}.txt"
        file_path.open("r+", encoding="utf-8").write(self.text)
        super().dump(folder_path, recurcive=recurcive) # Edge files are dumped here
        
