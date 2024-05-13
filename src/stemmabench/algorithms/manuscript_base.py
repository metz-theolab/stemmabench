from pathlib import Path
import re

class ManuscriptBase:
    """Base class for representing manuscripts in a stemma tree.
    """

    def __init__(self,
                 label: str,
                 parent: "ManuscriptBase",
                 children: list["ManuscriptBase"] = None,
                 edges: list[float] = None
                 ) -> None:
        """Base class for representing manuscripts.

        Args:
            label (str, reqired): The label denoting the text.
            parent (text, requiered): The parent text of the curent text. If set to None is the root manuscript of the tree.
            children (list, optional): A list of this Manuscripts children.
            edges (list, Optional): A list representing the distance between the edges. 
            In the same order as the children array.
            recursive (dict, Optional): If different than None will ignore all other parameters except parent
            and will build all the children of the manuscript from the given list.

        Raises:
            TypeError: If no Manuscript label specified.
        """
        if label:
                self._label = label
        else:
            raise ValueError("No Manuscript label specified.")
        if parent:
                self._parent = parent
        else:
            raise ValueError("No Manuscript parent specified.")
        if children:
                self._children = children
        else:
            raise ValueError("No Manuscript children specified.")
        if edges:
                if not children:
                    raise ValueError("The children array must be specified in order to have edges.")
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
                        "edges": {edge for edge in self.edges},
                        "children": {child.dict() for child in self.children}}

    def dump(self, 
             folder_path: str,  
             recurcive: bool = False) -> None:
        """Adds the edge to the edge file present in given folder.
            If the folder does not exist it will be created.
            If the edge file does not existe it will be created.
            Will look through edge file if it exists to check that edge is alredy present in edge file. 
            If True will not wirte individual edge to file.
        
        Args:
            folder_path (str, required): The path the folder where the text file will be writen.
            recurcive (bool, otional): Indicates if the dump should be propagated to all children recursively.
        """
        edge_path = Path(folder_path) / "edges.txt"
        if not Path.exists(edge_path): # If not exists read file check if edge already present
            Path.mkdir(exist_ok=True)
        text = edge_path.read_text()
        with edge_path.open("a") as f:
            for child in self.children:
                edge = "('" + self.label + "','" + child.label + "')"
                if not re.search(edge, text):
                    f.write(edge + "\n")
            f.close()
        if recurcive: # Propagate dump recursively to children
            for child in self.children:
                child.dump(folder_path, recurcive = True)

    def build_lookup(self, lookup: dict) -> None:
        """Used to instantiate the stemmas lookup attribute.

        Args:
            lookup (dict, Requiered): The dictionary that the current manuscript will be added to.
        """
        # TODO: Check to see if passed by reference or by value -> need return.
        lookup.update({self.label: self})
        if self.children:
            (c.build_lookup(lookup) for c in self.children)