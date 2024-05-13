from pathlib import Path ######################## Remove
from stemmabench.algorithms.manuscript_base import ManuscriptBase

class Manuscript(ManuscriptBase):
    """Class for the representation of an existing manuscript in a stemma tree.
    """

    def __init__(self,
                 label: str,
                 parent: "ManuscriptBase",
                 children: list["ManuscriptBase"] = None,
                 edges: list[float] = None,
                 recursive: dict[str:dict] = None,
                 text: str = None) -> None:
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
            # End recursion if list of keys is empty
            if list(recursive[self.label]) == []:
                return None
            super().__init__(list(recursive.keys())[0], parent, [], edges)
            # Initialize children list
            #children = []
            # Else for each key value add a new Manuscript with dict contense
            for lab in recursive[self.label].keys():
                super()._children.append(Manuscript(parent=self, recursive={lab:recursive[self._label][lab]}))
            
        else:
            super().__init__(label, parent, children, edges)


            

    # Getters
    #@property
    #def text_path(self):
    #    return self._text_path
    
    @property
    def text(self):
        return self._text
        
    def __eq__(self, value: object) -> bool:
        """Returns True if both texts have the same content and the same label.
        !!! Returns True if both texts are missing !!!

        Args:
            value (object, requiered): The object to compare to.
        """
        if isinstance(value, Manuscript):
            return value.text == self.text and value.label == self.label
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
        
    def cast_to_Manuscript(manuscriptBase: "ManuscriptBase",
                           text_path: str,
                           text: str):
        """Casts a ManuscriptBase to a Manuscript.
        
        Args:
            manuscriptBase (ManuscriptBase, Required): The ManuscriptBase object to be cast to a Manuscript.
            text_path (str, Required): The path the the txt file containing the text.
            text (str, Required): The manuscript text.

        Returns:
            Manuscript: The manuscriptBase object cast to a Manuscript class.

        Raises:
            ValueError: If manuscriptBase is not of class ManuscriptBase.
        """
        if not isinstance(manuscriptBase, ManuscriptBase):
            raise ValueError("manuscriptBase is not of class ManuscriptBase.")
        return Manuscript(manuscriptBase.label,text_path, text, manuscriptBase.parent, manuscriptBase.children)