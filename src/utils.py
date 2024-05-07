from pathlib import Path
from itertools import groupby

@staticmethod
def load_text(path_to_text: str) -> str:
    """Load a text given a path to this text.
    Args:
        path_to_text (str): The path to the text to be loaded.
    Returns:
        str: The loaded text.
    """
    with open(Path(path_to_text), encoding="utf-8") as file:
        return file.read()

@staticmethod
def dict_from_edge(edge_path) -> dict:
    """Converts edge file to dictionary representation.
    
    Args:
        edge_path (str, Requiered): The path to the edge file used to construct dictionary.

    Returns:
        dict: Dictionary representation of the tree in edge file.
    """
    input_lines = Path(edge_path).read_text().strip().replace("(", "").replace(")","").replace("'","").split(sep="\n")
    tree_data = {}
    for line in input_lines:
        parent, child = map(int,line.split(', '))
        if parent not in tree_data:
            tree_data[parent] = {}
        tree_data[parent][child] = {}
    while len(tree_data) > 1:
        lab = max(tree_data)
        moving = tree_data.pop(lab)
        for i in tree_data:
            if tree_data[i].get(lab) != None:
                tree_data[i][lab] = moving
    return tree_data