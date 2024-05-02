class ManuscriptBase:
    """Base class for representing manuscripts in a stemma tree.
    """

    def __init__(self,
                 label: str,
                 parent: "ManuscriptBase",
                 children: list["ManuscriptBase"] = None,
                 edges: list[float] = None) -> None:
        """Base class for representing manuscripts.

        Args:
            label (str, reqired): The label denoting the text.
            parent (text, requiered): The parent text of the curent text. If set to None is the root manuscript of the tree.
            children (list, optional): A list of this Manuscripts children.
            edges (list, Optional): A list representing the distance between the edges. 
            In the same order as the children array.
        """

        if label:
            self._label = label
        else:
            raise TypeError("No Manuscript label specified.")
        
        self._parent = parent

        if children:
            self._children = children

        if edges:
            if not children:
                raise RuntimeError("The children array must be specified in order to have edges.")
            elif len(children) != len(edges):
                raise RuntimeError("The edges array must be of same length as the children array.")
            else:
                self._edges = edges

    @property
    def parent(self):
        return self._parent
    
    @property
    def children(self):
        return self._children
    
    @property
    def label(self):
        return self._label
    
    @property
    def edges(self):
        return self._edges
    
    def __repr__(self) -> str:
        """String representation of the Manuscript"""
        return self.label

    def dict(self, include_edges = False) -> dict:
        """ Constructs dictionary representaion of tree from the Manuscript it is called from.

        Args:
            include_edges (bool, optional): Indicates if the tree should contain the edges. Default to false.

        Resturns:
            Dictionary representation of Manuscript and all of its children.
        """
        if include_edges:
            if len(self.children) == 0:
                return self.label
            else:
                return {self.label: {child.dict() for child in self.children}}
        # TODO: Check this works.
        else:
            if len(self.children) == 0:
                return self.label
            else:
                return {"label": self.label, 
                        "children": {child.dict() for child in self.children}, 
                        "edges": {edge for edge in self.edges}}
    


                
