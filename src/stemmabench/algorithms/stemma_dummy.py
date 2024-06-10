import numpy as np
from typing import Union, List
from numpy.random import default_rng
from numpy.random._generator import Generator
from stemmabench.algorithms.stemma_algorithm import StemmaAlgo
from stemmabench.algorithms.manuscript_in_tree import ManuscriptInTree
from stemmabench.algorithms.utils import Utils


class StemmaDummy(StemmaAlgo):
    """Class that constructs a "random" stemma for use as a basis for comparison.

    ### Attributes:
        - manuscripts (dict): The dictionay of all the texts with text labels as keys and texts as values.
        - width (int): The number of children generated for each manuscript. May be overriten by more complex generation parameters in future implementations.
        - seed (int): The seed used to produce reproducible pseudorandom results.
        - generator (numpy.random._generator.Generator): The generator used to generate random numbers.
    """

    def __init__(self,
                 width: int = 2,
                 seed: Union[int, None] = None) -> None:
        """Object used for the construction of a dummy stemma tree.

        ### Args:
            - width (int, Optional): The number of children to be built for each manuscript. Tree is filed from top to bottom and from left to right.
            - seed (int, Optional): The seed used to produce reproducible pseudorandom results.
            Uses Generators for random number generation.

        ### Raises:
            - ValueError: If width parameter is not an int.
        """
        if not isinstance(width, int):
            raise ValueError("Parameter width must be of type int.")
        super().__init__()
        self._width: int = width
        self._generator: Generator = default_rng(seed=seed)

    @property
    def width(self):
        return self._width

    @property
    def generator(self):
        return self._generator

    def compute(self, folder_path: str, width: Union[int, None] = None) -> ManuscriptInTree:
        """Builds the stemma tree.

        ### Args:
            - folder_path (str): The path to the folder containing the texts. The path specified here will surplant the previous path defined in constructor.
            !!! All .txt files in this folder must be files containing Manuscript texts unless the file name contains the substring "edge" !!!
            - width (int, Optional): The number of children to be generated for each manuscript. 
            If specified will reset the instance attribute to _width to width parameter value.

        ### Returns:
            - Manuscript: The root of the stemma with the rest of its tree as its children.
        """
        if not isinstance(width, int):
            raise ValueError("Parameter width must be of type int.")
        if width:
            self._width = width
        super().compute(folder_path)
        return ManuscriptInTree(parent=None, recursive=Utils.dict_from_edge(edge_list=self._build_edges(self._build_random_levels())))

    def _build_random_levels(self) -> List[List[str]]:
        """Builds a list of labels at each level of the stemma tree.
        Uses the keys of the manuscripts attribute from the super class as input.

        ### Returns:
            - list: List of lists of lebels present at each level.

        Example:
            >>> StemmaDummy(folder_path="../../../tests/test_data", width = 2)._build_random_levels()
            [['2'], 
            ['5', '1'], 
            ['9', '6', '8', '12'], 
            ['10', '11', '13', '3', '4', '7']]
        """
        labels = list(self.manuscripts.keys())
        depth = 1
        next_man = labels.pop(self.generator.integers(0, len(labels)))
        out = [[next_man]]
        while len(labels) >= np.power(self.width, depth):
            level = []
            for i in range(np.power(self.width, depth)):
                next_man = labels.pop(self.generator.integers(0, len(labels)))
                level.append(next_man)
            out.append(level)
            depth += 1
        if len(labels) > 0:
            out.append(labels)
        return out

    def _build_edges(self, levels: List[List[str]]) -> List[List[str]]:
        """Builds an edge list from the classes manuscript attribute using the _build_random_levels method.

        ### Args:
            - levels (list): The list containing the levels of the stemma tree.

        ### Returns:
            - list: List of edges of the stemma.

        ### Example:
            >>> _build_edges(levels = [["1"], ["2", "3"], ["4", "5", "6", "7"]])
            [['1','2'], ['1','3'], ['2','4'], ['2','5'], ['3','6'],['3','7']]
        """
        edges = []
        for idx in range(len(levels)-1):
            parents = levels[idx]
            children = levels[idx + 1]
            children_sublist = [children[i:i + self.width]
                                for i in range(0, len(children), self.width)]
            for parent, child_list in zip(parents, children_sublist):
                for child in child_list:
                    edges.append([parent, child])
        return edges
