from pathlib import Path
from typing import Dict, Union
from os import listdir


class Utils:
    """Class containing utility function to be used throughout the program."""

    @staticmethod
    def load_text(path_to_text: str) -> str:
        """Load a text given a path to this text.

        ### Args:
            - path_to_text (str): The path to the text to be loaded.

        ### Returns:
            - str: The loaded text.
        """
        with open(path_to_text, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def get_text_list(folder_path: str) -> list[str]:
        """For a given folder path returns a list of all the text names in that folder.
        Will remove all names that contain the subsring "edge" from the list.
        
        ### Args:
            - folder_path (str): The path to the folder that containing stemma texts.

        ### Returns:
            - list: List of manuscript names.
        """
        return [l.replace(".txt","") for l in listdir(folder_path) if l.find("edge") == -1]

    @staticmethod   
    def dict_of_children(edges: list[list[str]]) -> Dict[str, dict]:
        """Builds a dictionary with node label as key and dictionary of children as value.

        ### Args:
            - edges (list): A list representation of edges in list format.

        ### Returns:
            - dict: A dictionary containing with a node as key and a dictionary children.

        ### Example:
            >>> Utils.dict_of_children([['a','b'], 
                                        ['a','c'], 
                                        ['b', 'd'], 
                                        ['b','e'], 
                                        ['c','f'], 
                                        ['c', 'g']])
            {'a': {'b': {}, 'c': {}}, 
            'b': {'d': {}, 'e': {}}, 
            'c': {'f': {}, 'g': {}}}
        """
        tree_data: dict = {}
        for edge in edges:
            if edge[0] not in tree_data:
                tree_data[edge[0]] = {}
            tree_data[edge[0]][edge[1]] = {}
        return tree_data

    @staticmethod
    def find_root(dict_of_children: Dict[str, dict]) -> list[str]:
        """Finds the root of the stemma from a dictionary of children.
        
        ### Args:
            - dict_of_children (dict): Dictionary containing the labels of all manuscripts that have children as keys
            and dictionary of whith all children of key manuscript as keys as values.
        
        ### Example:
            >>> Utils.find_root({'a': {'b': {}, 'c': {}}, 
                                 'b': {'d': {}, 'e': {}}, 
                                 'c': {'f': {}, 'g': {}}})
            ['a']
        """
        not_root = []
        for i in dict_of_children:
            for j in dict_of_children:
                if str(i) in list(dict_of_children[j].keys()):
                    not_root.append(i)
        root = list(set(dict_of_children.keys()) - set(not_root))
        return root

    @staticmethod
    def recursive_fit(input_dict: Dict[str, dict], 
                      to_be_fited_label: str, 
                      to_be_fited_dict: Dict[str, dict]) -> Dict[str, dict]:
        """Takes nested dictionaries and places the to_be_fited_dict in the corresponding place. If to_be_fited_label is not a key in any of the input_dict
        nested dictionaries it will return input_dict unchanged.
        
        ### Args:
            - input_dict (dict): The nested dictionary in which the to_be_fited_dict will be placed.
            - to_be_fited_label (str): The label of the to_be_fited_dict. Used to find its corresponding places in the input_dict.
            - to_be_fited_dict (dict): The dictionary to fitted into the input_dict at the position identified by to_be_fited_label.

        ### Returns:
            - dict: The input_dict with the to_be_fited_dict dictionary placed at the position identified by the key to_be_fited_label.
            If to_be_fited_label is not a key in input_dict will return input_dict.

        ### Example:
            >>> test_dict = {'1':{'A':{'e':{}, 'f':{}}, 'B':{}}, '2':{}}
            >>> to_be_fited = {'i':{}, 'j':{}}
            >>> to_be_fited_lab = 'e'
            >>> recursive_fit(test_dict, to_be_fited_lab, to_be_fited)
            {'1': {'A': {'e': {'i': {}, 'j': {}}, 'f': {}}, 'B': {}}, '2': {}}

            >>> test_dict = {'1':{'A':{'e':{}, 'f':{}}, 'B':{}}, '2':{}}
            >>> to_be_fited = {'i':{}, 'j':{}}
            >>> to_be_fited_lab = 'w'
            >>> recursive_fit(test_dict, to_be_fited_lab, to_be_fited)
            {'1': {'A': {'e': {}, 'f': {}}, 'B': {}}, '2': {}}
        """
        if to_be_fited_label in list(input_dict.keys()):
            input_dict[to_be_fited_label] = to_be_fited_dict    
        else:
            for key in input_dict:
                input_dict[key] = Utils.recursive_fit(input_dict = input_dict[key], to_be_fited_label = to_be_fited_label, to_be_fited_dict = to_be_fited_dict)
        return input_dict

    @staticmethod
    def dict_from_edge(*,edge_path: Union[str, None] = None, edge_list: Union[list[list[str]], None] = None) -> Dict[str, dict]:
        """Converts edge file to dictionary representation.

        ### Args:
            - edge_path (str, Optional): The path to the edge file used to construct dictionary.
            - edge_list (str, Optional): The list of all the edges in a stemma tree.

        ### Returns:
            - dict: Dictionary representation of the tree in edge file.

        ### Raises:
            - ValueError: If edge file or list is not a valid edge (see method validate_edge for more info).
            - ValueError: If no parameter is specified.
            - ValueError: If both parameters are specified.
        """
        if edge_path and edge_list:
            raise ValueError("Only one of the parameters edge_path and edge_list can be specified.")
        if not edge_path and not edge_list:
            raise ValueError("At least one of the parameters edge_path or edge_list must be specified.")
        if edge_path:
            edge_list = Utils.edge_to_list(edge_path)
        tree_data = Utils.dict_of_children(edge_list)
        root = Utils.find_root(tree_data)
        if not Utils.validate_edge(tree_data):
            raise ValueError("The edge file given is not valid. Look at validate_edge function for more details.")
        while len(tree_data) > 1:
            # If root is the last one take next as root should be fitted last
            if root[0] == list(tree_data.keys())[len(tree_data.keys())-1]:
                lab = list(tree_data.keys())[len(tree_data.keys())-2]
            else:
                lab = list(tree_data.keys())[len(tree_data.keys())-1]
            moving = tree_data.pop(lab)
            tree_data = Utils.recursive_fit(tree_data, lab, moving)
        return tree_data

    @staticmethod
    def validate_edge(dict_of_children: Dict[str, dict]) -> bool:
        """Cheks to see if edge file is valid.
            - Checks to see if there is only one root.
        ### Args:
            - dict_of_children (dict): A dictionary of nodes with node labels as keys and
            dictionary of children as value.

        ### Returns:
            - bool: Indicates if the edge file is valid.

        ### Example:    
            >>> Utils.validate_edge({'a': {'b': {}, 'c': {}}, 
                                     'b': {'d': {}, 'e': {}}, 
                                     'c': {'f': {}, 'g': {}}})
            True
        """
        nb_root_cond = len(Utils.find_root(dict_of_children)) == 1
        # TODO: add other conditions.
        return nb_root_cond

    @staticmethod
    def edge_to_list(edge_path: str) -> list[list[str]]:
        """Builds an list representation of the edge file.
        ### Args:
            - edge_path (str): The path to the edge file.

        ### Returns:
            - list: List of edges in edge format.
        """
        input_lines = Path(edge_path).read_text().strip().replace("(", "").replace(")","").replace("'","").replace(" ","").split(sep="\n")
        return list(e.split(sep=",") for e in input_lines)