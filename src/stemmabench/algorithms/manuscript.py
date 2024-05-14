from pathlib import Path ######################## Remove
from stemmabench.algorithms.manuscript_base import ManuscriptBase
from typing import Union


class Manuscript(ManuscriptBase):
    """Class for the representation of an existing manuscript in a stemma tree.
    """

    def __init__(self,
                 parent: "ManuscriptBase",
                 label: str = None,
                 children: Union[list["ManuscriptBase"], None] = None,
                 edges: Union[list[float], None] = None,
                 recursive: Union[dict[str:dict], None] = None,
                 text: Union[str, None] = None) -> None:
        """A class representing the Manuscripts that make up the nodes of a stemma.

        Args:
            label (str, Reqired): The label denoting the text.
            parent (text, Optional): The parent Manuscript of the curent Manuscript. If set to None is the root of the tree.
            children (list, optional): A list of this Manuscripts children.
            edges (list, Optional): A list representing the distance between the edges. 
            In the same order as the children array.
            recursive (dict[str], Optional): If different than None will buil all the children of the manuscript
            from the given list. 
            text (str, Required): The contense of the text. If set to None this represents a missing text.

        Raises:
            ValueError: If no label or.
        """
        if text:
            self._text = text
        if recursive:
            self._parent = None
            self._children = []
            self._label = list(recursive.keys())[0]
            # End recursion if list of keys is empty
            if list(recursive[self.label]) == []:
                return None
            # Else for each key value add a new Manuscript with dict contense
            for lab in recursive[self.label].keys():
                self._children.append(Manuscript(parent=self, recursive={lab:recursive[self._label][lab]}))  
        else:
            super().__init__(label, parent, children, edges)
    
    @property
    def text(self):
        return self._text
        
    def __eq__(self, value: object) -> bool:
        """Returns True if both texts have the same content and the same label.

        Args:
            value (object, requiered): The object to compare to.
        """
        if isinstance(value, Manuscript):
            return value.text == self.text and value.label == self.label
        return False

    def dump(self, folder_path: str, edge_path: str = None):
        """Writes all texts int the stemma to txt files placed in the specified folder.
        If the folder does not exist it will be created. Will also write all edges present in the stemma to 
        the specified edge file. If none is specified a file named edges.txt will be created in the given folder
        and the adges will be writen to that file.
        
        Args:
            folder_path (str, Required): The path the folder where the text file will be writen.
            edge_path (str, Optional): The path to the edge file.
        """
        if not Path(folder_path).exists():
            Path(folder_path).mkdir(exist_ok=True)
        f = (Path(folder_path) / (self.label + ".txt")).open("w")
        f.write(self.text)
        f.close()
        super().dump(folder_path, edge_path)

    def build_text_lookup(self) -> dict:
        """Used to instantiate the stemmas lookup attribute.

        Returns:
            dict: Dictionary of its self and all its decendents. With its label as key and its self as value.
        """
        out = {self.label: self}
        if self.children:
             for c in self.children:
                  out.update(c.build_lookup())
        return out