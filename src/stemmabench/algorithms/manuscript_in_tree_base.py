from typing import Union, Dict, Any, List


class ManuscriptInTreeBase:
    """Base class for representing manuscripts in a stemma tree.

    ### Attributes:
        - label (str): The label that references the manuscript.
        - parent (ManuscriptBase): The parent of the manuscript. If it is none it is the root of the stemma tree.
        - children (list): The list of the manuscripts children. If it is empty the manuscript is a leaf node of the tree.
        - edges (list): The list of all the edges conected to the tree. Is in the same order as the children list.
    """

    def __init__(self,
                 label: str,
                 parent: Union["ManuscriptInTreeBase", None],
                 children: List["ManuscriptInTreeBase"] = [],
                 edges: List[float] = []
                 ) -> None:
        """Base class for representing manuscripts.

        ### Args:
            - label (str): The label denoting the text.
            - parent (text): The parent text of the curent text. If set to None is the root manuscript of the tree.
            - children (list, Optional): A list of this Manuscripts children.
            - edges (list, Optional): A list representing the distance between the edges. In the same order as the children list.
            If different than None will ignore all other parameters except parent
            and will build all the children of the manuscript from the given list.

        ### Raises:
            - ValueError: If parent different than None or not of type ManuscriptBase.
            - ValueError: If children not of type list.
            - RuntimeError: If edges specified and len(edges) > len(children)
        """
        if not isinstance(label, str):
            raise ValueError("Parameter label must be a string.")
        self._label: str = label
        self._edges: List[float] = edges
        if not parent or isinstance(parent, ManuscriptInTreeBase):
            self._parent: Union[ManuscriptInTreeBase, None] = parent
        else:
            raise ValueError(
                "Parent must be None or of type ManuscriptInTreeBase.")
        if isinstance(children, list):
            self._children: List["ManuscriptInTreeBase"] = children
        else:
            raise ValueError("The children must be of type list.")

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
        """String representation of the Manuscript.

        ### Returns:
            - str: String representation of the manuscript.
        """
        return self.label

    def dict(self, include_edges: bool = False) -> Dict[str, Any]:
        """ Constructs dictionary representaion of tree from the Manuscript it is called from.

        ### Args:
            - include_edges (bool, Optional): Indicates if the tree should contain the edges. Default to false.

        ### Resturns:
            - dict: Dictionary representation of Manuscript and all of its children.
        """
        if include_edges:
            if len(self.children) == 0:
                return {self.label: {}}
            else:
                return {"label": self.label,
                        "edges": {child.label: edge for edge, child in zip(self.edges, self.children)},
                        "children": {child.label: child.dict() for child in self.children}}
        else:
            if not self.children or len(self.children) == 0:
                return {self.label: {}}
            else:
                out = {}
                for child in self.children:
                    out.update(child.dict())
                return {self.label: out}

    def build_text_lookup(self) -> Dict[str, "ManuscriptInTreeBase"]:
        """Used to instantiate the stemmas lookup attribute.

        ### Returns:
            dict: Dictionary of its self and all its decendents. With its label as key and its self as value.
        """
        out = {self.label: self}
        if self.children:
            for c in self.children:
                out.update(c.build_text_lookup())
        return out

    def set_edges(self, edge_dict: Dict[str, Union[float, int]]) -> None:
        """Sets the edges of the current manuscript and propagates the edge setting to all its children.

        ### Args:
            - edge_dict (dict): The dictionary used to set the edges with the edges as keys and the edge distances as values.
            The format of the keys is: "node_label1,node_label2".
        """
        if len(self.edges) > 0:
            self._edges = []
        for child in self.children:
            if edge_dict.get(f"{self.label},{child.label}") != None:
                self._edges.append(edge_dict[f"{self.label},{child.label}"])
            else:
                self._edges.append(edge_dict[f"{child.label},{self.label}"])
            child.set_edges(edge_dict=edge_dict)
