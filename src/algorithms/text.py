from pathlib import Path ######################## Remove
import algorithms.utils as util

class Text:
    """Class for the representation of a text in a stemma tree.
    """

    def __init__(self,
                 label: str,
                 text_path: str,
                 text: str,
                 parent,
                 children: list = None,
                 edges: list = None): # Potentially use 2nd array to store edge distances.
        if label:
            self._label = label
        else:
            raise TypeError("No node label specified.")
        
        if text_path:
            self._text_path = text_path
        else:
            raise TypeError("No text path specified.")
        
        if text:
            self._text = util.load_text(text_path)
        else:
            raise TypeError("No input text specified.")
        
        if parent:
            self._parent = parent

        if children:
            self._children = children

        if edges:
            self._edges = edges


    """A class representing the texts that make up the nodes of a stemma.
        

        Args:
            label (str, reqired): The label denoting the text.
            text_path (str, reqired): The name of the txt file containing the text. 
            (The name of the folder containing the txt files will be taken from the stemma class.)
            text (str, required): The contense of the text. If set to None this represents a missing text.
            parent (text, optional): The parent text of the curent text.
            children (list, optional): A list of this nodes children. 

        Raises:
            Exception: If no input text is specified.
        """
    
    # Getters
    @property
    def label(self):
        return self._label
    
    @property
    def text_path(self):
        return self._text_path
    
    @property
    def text(self):
        return self._text
    
    @property
    def parent(self):
        return self._parent
    
    @property
    def children(self):
        return self._children

    # Setters
    @label.setter
    def label(self, label):
        # TODO: add checks
        self._label = label

    @text_path.setter
    def text_path(self, text_path):
        # TODO: add checks
        self._text_path = text_path

    @text.setter
    def text(self, text):
        # TODO: add checks
        self._text = text

    @parent.setter
    def parent(self, parent):
        # TODO: add checks
        self._parent = parent

    @children.setter
    def children(self, children):
        # TODO: add checks
        self._children = children

    def to_dict(self):
        """ Constructs dictionary representaion of tree from the text it is called from.
        """
        if len(self.children) == 0:
            return self.label
        else:
            return {self.label: {child.to_dict() for child in self.children}}
        
    
    def __eq__(self, value: object) -> bool:
        """Returns True if both texts have the same contents.
        !!! Returns True if both texts are missing !!!
        """
        if isinstance(value, Text):
            return value.text == self.text
        return False
