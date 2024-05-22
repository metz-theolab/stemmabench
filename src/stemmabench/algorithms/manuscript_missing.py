from stemmabench.algorithms.manuscript_base import ManuscriptBase


class ManuscriptMissing(ManuscriptBase):
    """Class for the representation of a missing manuscript in a stemma tree.
    """

    def __init__(self, 
                 label: str, 
                 parent: ManuscriptBase, 
                 children: list[ManuscriptBase] = None, 
                 edges: list[float] = None) -> None:
        """Class for the representation of a missing manuscript in a stemma tree.

        Args:
            label (str, Required): The label denoting the text.
            parent (ManuscriptBase, Required): The parent text of the curent text. If set to None is the root manuscript of the tree.
            children (list, optional): A list of this Manuscripts children.
            edges (list, Optional): A list representing the distance between the edges. 
            In the same order as the children array.
        """
        raise NotImplementedError()
