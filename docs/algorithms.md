# How to use

In order to construct a stemma in the stemmabench package, a `Stemma` object must be created, which stores all relevant information about the stemma. A stemma can be constructed in one of two ways:

- From an edge file containing all the edges present in the stemma
- Using one of the implemented algorithms in the stemmabench package

For both methods, the stemma object must be initialized with the path to the folder containing all the stemma texts.
```python
stemma = Stemma(folder_path="path_to_the_folder")
```
The stemmas can then be built by calling the compute method on the stemma object.

## Build stemma from edge file

A stemma can be built from a txt file containing the list of all the edges contained in the stemma. This txt file must be present in the folder path specified in the stemma constructor.

The format of the edge file must be as follows:

```
(2, 5)
(2, 6)
(root, 2)
(root, 3)
(root, 4)
(3, 7)
(3, 8)
(3, 9)
(4, 10)
(4, 11)
(4, 12)
(4, 13)
```

> [Note]
> 
> For an edge file to be valid, it must possess only one root. The root is defined as the label that only appears on the left side of all the edges, as shown in the example above. The order of the labels in each edge is important and represents (parent, child).

The labels present in the edges must have matching txt files in the specified folder path containing the corresponding manuscript text.
If the txt file does not exist, the node will be considered as empty. That is to say, a node with no text.

To build a stemma from an edge file, simply instantiate the stemma, taking care to specify the folder containing the edge file. Then call the compute method, specifying the name of the edge file.

```python
stemma = Stemma(folder_path="path_to_the_folder")
stemma.compute(edge_file="edge_file.txt")
```
## Build stemma from using implemented algorithms

In the stemmabench package, algorithms are implemented in the form of objects that perform the stemma tree construction. The result of the compute method called on these algorithm objects is the root of the stemma that is passed to the stemma object.

All parameters specific to each algorithm are passed in the algorithm object constructor.

```python
stemma = Stemma(folder_path="path_to_the_folder")
stemma.compute(algo=StemmaDummy(width = 2))
```

The extra arguments to be passed to the algorithm's compute method can be passed in the `**kwargs` of the stemma compute method.

```python
stemma = Stemma(folder_path="path_to_the_folder")
stemma.compute(algo=StemmaDummy(), width = 2)
```

For further details on the algorithm objects and their parameters, check the Implemented algorithms section.

## Saving the results of a stemma

A stemma can be saved using the `dump` method. This method will create a txt file for each manuscript present in the stemma (manuscript_label.txt), as well as an edge file listing all the edges present in the tree. If the specified folder does not exist, it will be created.

The specific name of the edge file can be specified using the edge_file_name parameter.

If the parameter dump_texts is set to false, only the edge file will be created.

```python
stemma.dump(folder="path_to_the_folder", edge_file_name="my_edges.txt", dump_texts=False)
```

# Implemented algorithms

The following algorithms are currently implemented in the package:

- Dummy
- Neighbor-Joining
- RHM (Experimental)

## Dummy

This algorithm constructs random stemmas that respect certain constraints. The stemmas produced by this algorithm are meant to be used as a baseline to gauge the performance of various other stemmatological algorithms against random attribution. The algorithm will fill the tree structure from top to bottom and from left to right until all the manuscripts have been placed in the tree structure.

```python
stemma = Stemma(folder_path="path_to_the_folder")
stemma.compute(algo=StemmaDummy(width = 2, seed = 1))
```

### Parameters

- `width`: The number of children of each manuscript in the tree.
- `seed`: The seed that is passed to a random number generator in order to produce reproducible results.

## Neighbor-Joining

The Neighbor-Joining algorithm functions similarly to the agglomerative hierarchical clustering method, in that it requires a distance or similarity metric in order to progressively group individuals together.

Neighbor-Joining, being a distance or dissimilarity-based algorithm, therefore requires a choice of metric to calculate a distance matrix representing the distance between each pair of texts.

This method can only produce bifid trees with existing manuscripts only existing on leaf nodes.

```python
stemma = Stemma(folder_path="path_to_the_folder")
stemma.compute(algo=StemmaNJ(distance = levenshtein, rooting_method = "none"))
```
### Parameters

- `distance`: The distance metric to be used to calculate the distance between texts. This can be any function that takes at least 2 strings as arguments and returns a float. For the distance function to be valid, it must respect the following 2 constraints:
    +  The distance of 2 identical strings must be equal to 0 `distance("test", "test") == 0`.
    +  No matter the order the strings are placed in as parameters, the result must be identical `distance("test1", "test2") == distance("test2", "test1")`.
- `rooting_method`: As the Neighbor-Joining algorithm produces unrooted trees, this parameter specifies the rooting method to be used on the resulting tree. The currently supported rooting methods are:
    + **none**: This will return the last agglomerated node as the root of the tree.
    + **midpoint-dist**: This is an implementation of the midpoint rooting method, and will return the tree with the root being the midpoint of the longest distance between all leaf nodes in the tree. This method takes into account the length of the tree edges. This is the default method used by the algorithm.
    + **midpoint-edge**: Similar to the previous method, although all edge lengths are considered to be equal to 1.

> Reference
> 
>Saitou N, Nei M (July 1987). “The neighbor-joining method: a new method for reconstructing phylogenetic trees”. In: Mol. Biol. Evol.

## RHM

RHM is a stochastic algorithm which functions by randomly rearranging a given tree and only keeping the changes that reduce a certain cost function. This means that the heart of RHM algorithm is the various cost functions of which it is comprised. 

This method can only produce bifid trees with existing manuscripts only existing on leaf nodes.

Currently, this algorithm can only build the stemma by reading the outputted dot file produced by the compute method.

In the case that multiple iterations of the algorithm are run (strap>1) then the stemma that is returned by the compute method is the last one calculated.

```python
stemma = Stemma(folder_path="path_to_the_folder")
stemma.compute(algo=StemmaRHM(nb_opti = 1, strap = 1, segment_size = 10, keep_dot = True))
```

### Parameters

- `nb_opti`: The number of optimisation iterations to run through for each run of the algorithm.
- `strap`: The number of times the algorithm will be run and the results outputted. Due to the stochastic nature of the algorithm, this parameter is used to enable the calculation of an average performance.
- `segment_size`: The size of the segments that the texts will be divided up into. The number represents the number of words per segment.
- `keep_dot`: Boolean indicating if the dot files should be removed once the edge.txt files have been produced.

> Reference
>
>Roos, Teemu, Tuomas Heikkilä, and Petri Myllymäki (Jan. 2006). “A Compression-Based Method for Stemmatic Analysis.” In: Frontiers in Artificial Intelligence and Applications 141, pp. 805–806.

# How to implement a custom algorithm

All algorithms inherit from the class StemmaAlgo. Therefore, any custom algorithm must inherit from this class. 

The algorithm object must also possess a compute method which must take the path to the folder containing the stemma txt file as first parameter. This compute method must return the root of the stemma tree which will be passed to the _root attribute of the stemma as shown below. This root must be an object that inherits from the ManuscriptInTreeBase object.

The code section bellow shows the section of the stemma compute method that is executed when building as stemma using an algorithm.

```python
elif algo:
    self._root = algo.compute(folder_path=self.folder_path, **kargs)
    self._text_lookup = self._root.build_text_lookup()
    for text in self.text_lookup.values():
        if isinstance(text, ManuscriptInTree):
            text._text = Utils.load_text(f"{self.folder_path}/{text.label}.txt")
    self._fitted = True
```

Then following example shows the implementation of the compute method for the dummy algorithm.

```python
def compute(self, folder_path: str, width: Union[int, None] = None) -> ManuscriptInTree:
        if width:
            self._width = width
        if not isinstance(width, int):
            raise ValueError("Parameter width must be of type int.")
        super().compute(folder_path)
        return ManuscriptInTree(parent=None, recursive=Utils.dict_from_edge(edge_list=self._build_edges(self._build_random_levels())), 
                                                                            text_list=Utils.get_text_list(folder_path))
```

As it can be seen in the above example in order to instantiate a tree the algorithm need only produce a dictionary representation of the stemma tree and passe it as an argument to the `recursive` parameter of a manuscript object.

In order to facilitate the production of this dictionary, a list of edges can be passed to the `dict_from_edge` method from the Utils class that will construct the dictionary. This list of edges must be specified in the following format:

```python
[["1", "2"], ["1", "3"], ["2", "4"], ["2", "5"], ["3", "6"], ["3", "7"]]
```

The labels on the left are considered parens and the labels on the right children. For an edge list to be valid, it must possess a single root. Therefore, only a single label can only be present on the left of all the edges.