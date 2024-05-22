from pathlib import Path


class Utils:
    """Class containing utility function to be used throughout the program."""

    @staticmethod
    def load_text(path_to_text: str) -> str:
        """Load a text given a path to this text.

        Args:
            path_to_text (str): The path to the text to be loaded.

        Returns:
            str: The loaded text.
        """
        with open(path_to_text, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod   
    def dict_of_children(edges: list[list[str,str]]) -> dict[str: dict]:
        """Builds a dictionary with node label as key and dictionary of children as value.

        Args:
            edges (list, Requiered): A list representation of edges in list format.
            Format: [['a','b'], ['a','c'],...] 

        Returns:
            dict: A dictionary containing with a node as key and a dictionary children.
            Format: {a: {b: {}, c: {}}, ...}
        """
        tree_data = {}
        for edge in edges:
            if edge[0] not in tree_data:
                tree_data[edge[0]] = {}
            tree_data[edge[0]][edge[1]] = {}
        return tree_data

    @staticmethod
    def find_root(dict_of_children: dict[str: dict]) -> list[str]:
        """Finds the root of the stemma from a dictionary of children.
        
        Args:
            dict_of_children (dict, Required): Dictionary containing the labels of all manuscripts that have children as keys
            and dictionary of whith all children of key manuscript as keys as values.
            Format: {'1':{'2':{}, '3': {}},
                     '2': {'4': {}, '5': {}},
                     '3': {'6': {}, '7': {}}, ...}
        """
        not_root = []
        for i in dict_of_children:
            for j in dict_of_children:
                if str(i) in list(dict_of_children[j].keys()):
                    not_root.append(i)
        root = list(set(dict_of_children.keys()) - set(not_root))
        return root

    @staticmethod
    def dict_from_edge(*,edge_path: str = None, edge_list: list = None) -> dict:
        """Converts edge file to dictionary representation.

        Args:
            edge_path (str, Optional): The path to the edge file used to construct dictionary.
            edge_list (str, Optional): The list of all the edges in a stemma tree.

        Returns:
            dict: Dictionary representation of the tree in edge file.

        Raises:
            ValueError: If edge file or list is not a valid edge (see method validate_edge for more info).
                        If no parameter is specified.
                        If both parameters are specified.
        """
        if edge_path != None and edge_list != None:
            raise ValueError("Only one of the parameters edge_path and edge_list can be specified.")
        if edge_path == None and edge_list == None:
            raise ValueError("At least one of the parameters edge_path or edge_list must be specified.")
        if edge_path != None:
            edge_list = Utils.edge_to_list(edge_path)
        tree_data = Utils.dict_of_children(edge_list)
        root = Utils.find_root(tree_data)
        if not Utils.validate_edge(tree_data):
            raise ValueError("The edge file given is not valid. Look at validate_edge function for more details.")
        while len(tree_data) > 1:
            # TODO: Optimize this mess
            if root[0] == list(tree_data.keys())[len(tree_data.keys())-1]:
                lab = list(tree_data.keys())[len(tree_data.keys())-2]
            else:
                lab = list(tree_data.keys())[len(tree_data.keys())-1]
            moving = tree_data.pop(lab)
            for i in tree_data:
                if tree_data[i].get(lab) != None:
                    tree_data[i][lab] = moving
        return tree_data

    @staticmethod
    def validate_edge(dict_of_children: dict[str: dict]) -> bool:
        """Cheks to see if edge file is valid.
            - Checks to see if there is only one root.
        Args:
            dict_of_children (dict, Requiered): A dictionary of nodes with node labels as keys and
            dictionary of children as value.
            Format: {'a': {'b': {}, 'c': {}}, 'b': {'d': {'e': {}}}, ...}

        Returns:
            bool: Indicates if the edge file is valid.
        """
        nb_root_cond = len(Utils.find_root(dict_of_children)) == 1
        # TODO: add other conditions.
        return nb_root_cond

    @staticmethod
    def edge_to_list(edge_path: str) -> list[list[str,str]]:
        """Builds an list representation of the edge file.
        Args:
            edge_path (str, Requiered): The path to the edge file.

        Returns:
            list: List of edges in edge format.
        """
        input_lines = Path(edge_path).read_text().strip().replace("(", "").replace(")","").replace("'","").replace(" ","").split(sep="\n")
        return list(e.split(sep=",") for e in input_lines)