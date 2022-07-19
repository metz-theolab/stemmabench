"""Module to analyze the characteristics of a tree from its variations.

Goal of the module:
    - Get as input a tree (tree object needs to be defined)
    - Compute its variations across collations to learn the statistical repartition
    - Provide statistical insights in terms of behavior.

TODO:
    - MSS names should be taken into account somehow
    - Figure out interesting measures on the collation
"""


class CollationAnalysis:
    """Provide the analysis of a collation.
    """

    def __init__(self, collation) -> None:
        """Get as input a collation (as defined by collatex) for analysis.

        Args:
            collation (TODO: get collation type from collatex): The collation to analyze.
        """
        self.collation = collation

    def change_rate(self):
        """Compute the change rate across the collation.
        """

    def global_distance_matrix(self):
        """Compute the distance matrix between each collation.
        """

    def word_distance_matrix(self):
        """Compute distance matrix on a word to word basis.
        """

    def mispell_rate(self):
        """Compute the mispell rate across the collation.
        """


class ModelFitter:
    """Given a stemmatology tree, computes the variations across it.
    """

    def __init__(self, stemma_tree) -> None:
        """
        TODO: define some kind of standard format for a stemmatology tree.
        """

    def build_collation(self):
        """Build the collations across each level of the tree.
        """

    def analyze_collations(self):
        """Analyze the collations at each level of the tree.
        """
