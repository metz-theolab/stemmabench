from pathlib import Path
import numpy as np
from typing import Dict, Union, List, Any, Tuple


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
    def get_text_list(folder_path: str) -> List[str]:
        """For a given folder path returns a list of all the text names in that folder.
        Will remove all names that contain the subsring "edge" from the list.

        ### Args:
            - folder_path (str): The path to the folder that contains stemma texts.

        ### Returns:
            - list: List of manuscript names.
        """
        return [l.stem for l in Path(folder_path).glob("*.txt") if not "edge" in l.stem]

    @staticmethod
    def dict_of_children(edges: List[List[str]]) -> Dict[str, Any]:
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
    def find_root(tree: Union[Dict[str, Any], List[List[str]], np.ndarray]) -> List[str]:
        """Finds the root of the stemma from a dictionary of children or a list of edges.

        ### Args:
            - tree (dict, list, nd.array): Dictionary containing the labels of all manuscripts that have children as keys
            and dictionary of whith all children of key manuscript as keys as values. Or list of all edges found in the tree.

        ### Returns:
            - list: List containing all the roots found in the tree.

        ### Example:
            >>> Utils.find_root({'a': {'b': {}, 'c': {}},
                                 'b': {'d': {}, 'e': {}},
                                 'c': {'f': {}, 'g': {}}})
            ['a']
            >>> Utils.find_root(["A","1"],
                                ["1","2"],
                                ["1","3"],
                                ["2","4"],
                                ["2","5"],
                                ["3","6"],
                                ["3","7"])
            ['A']
        """
        if isinstance(tree, (list, np.ndarray)):
            out = []
            if not isinstance(tree, np.ndarray):
                tree = np.array(tree)
            for node in tree[:, 0]:
                if node not in tree[:, 1] and node not in out:
                    out.append(node)
            return out
        else:
            not_root = []
            for i in tree:
                for j in tree:
                    if str(i) in list(tree[j].keys()):
                        not_root.append(i)
            root = list(set(tree.keys()) - set(not_root))
            return root

    @staticmethod
    def recursive_fit(input_dict: Dict[str, Any],
                      to_be_fitted_label: str,
                      to_be_fitted_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Takes nested dictionaries and places the to_be_fitted_dict in the corresponding place. If to_be_fitted_label is not a key in any of the input_dict
        nested dictionaries it will return input_dict unchanged.

        ### Args:
            - input_dict (dict): The nested dictionary in which the to_be_fitted_dict will be placed.
            - to_be_fitted_label (str): The label of the to_be_fitted_dict. Used to find its corresponding places in the input_dict.
            - to_be_fitted_dict (dict): The dictionary to fitted into the input_dict at the position identified by to_be_fitted_label.

        ### Returns:
            - dict: The input_dict with the to_be_fitted_dict dictionary placed at the position identified by the key to_be_fitted_label.
            If to_be_fitted_label is not a key in input_dict will return input_dict.

        ### Example:
            >>> test_dict = {'1':{'A':{'e':{}, 'f':{}}, 'B':{}}, '2':{}}
            >>> to_be_fitted = {'i':{}, 'j':{}}
            >>> to_be_fitted_lab = 'e'
            >>> recursive_fit(test_dict, to_be_fitted_lab, to_be_fitted)
            {'1': {'A': {'e': {'i': {}, 'j': {}}, 'f': {}}, 'B': {}}, '2': {}}

            >>> test_dict = {'1':{'A':{'e':{}, 'f':{}}, 'B':{}}, '2':{}}
            >>> to_be_fitted = {'i':{}, 'j':{}}
            >>> to_be_fitted_lab = 'w'
            >>> recursive_fit(test_dict, to_be_fitted_lab, to_be_fitted)
            {'1': {'A': {'e': {}, 'f': {}}, 'B': {}}, '2': {}}
        """
        if to_be_fitted_label in list(input_dict.keys()):
            input_dict[to_be_fitted_label] = to_be_fitted_dict
        else:
            for key in input_dict:
                input_dict[key] = Utils.recursive_fit(
                    input_dict=input_dict[key], to_be_fitted_label=to_be_fitted_label, to_be_fitted_dict=to_be_fitted_dict)
        return input_dict

    @staticmethod
    def dict_from_edge(*, edge_path: Union[str, None] = None, edge_list: Union[List[List[str]], None] = None) -> Dict[str, dict]:
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
            raise ValueError(
                "Only one of the parameters edge_path and edge_list can be specified.")
        if not edge_path and not edge_list:
            raise ValueError(
                "At least one of the parameters edge_path or edge_list must be specified.")
        if edge_path:
            edge_list = Utils.edge_to_list(edge_path)
        if not Utils.validate_edge(edge_list):
            raise ValueError(
                "The edge file or edge list given is not valid. Look at validate_edge function for more details.")
        tree_data = Utils.dict_of_children(edge_list)
        root = Utils.find_root(tree_data)
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
    def validate_edge(tree: Union[Dict[str, Any], List[List[str]], np.ndarray]) -> bool:
        """Checks to see if edge file is valid.
            - Checks to see if there is only one root.
        ### Args:
            - dict_of_children (dict, list, numpy.ndarray): A dictionary of nodes with node labels as keys and
            dictionary of children as value. Or a list of all edges present in a tree.

        ### Returns:
            - bool: Indicates if the edge file is valid.

        ### Example:
            >>> Utils.validate_edge({'a': {'b': {}, 'c': {}},
                                     'b': {'d': {}, 'e': {}},
                                     'c': {'f': {}, 'g': {}}})
            True
            >>> Utils.validate_edge(["A","1"],
                                    ["1","2"],
                                    ["1","3"],
                                    ["2","4"],
                                    ["2","5"],
                                    ["3","6"],
                                    ["3","7"])
            True
        """
        nb_root_cond = len(Utils.find_root(tree)) == 1
        # TODO: add other conditions.
        return nb_root_cond

    @staticmethod
    def edge_to_list(edge_path: str) -> List[List[str]]:
        """Builds an list representation of the edge file.
        ### Args:
            - edge_path (str): The path to the edge file.

        ### Returns:
            - list: List of edges in edge format.
        """
        input_lines = Path(edge_path).read_text().strip().replace(
            "(", "").replace(")", "").replace("'", "").replace(" ", "").split(sep="\n")
        return [e.split(sep=",") for e in input_lines]

    @staticmethod
    def set_new_root(edge_list: Union[List[List[str]], np.ndarray],
                     new_root: str) -> List[List[str]]:
        """Reroots the given tree to the given root.

        ### Args:
            - edge_list (list, numpy.ndarray): A list of edges that represents a tree.
            - new_root (srt): The label the tree is to be rerooted to.

        ### Returns:
            - list: The edge list of the rerooted tree.

        ### Raises:
            - ValueError: If new_root is not present in edge_list.
        """
        if new_root not in np.array(edge_list).flatten():
            raise ValueError(f"Parameter new_root: {new_root} is not present in edge_list.")
        out = []
        leaves = Utils.find_leaf_nodes(edge_list)
        curent_level = [new_root]
        next_level = []
        already_done = []
        while curent_level != []:
            for edge in edge_list:
                if edge[0] in curent_level and edge[0] not in already_done and edge[1] not in already_done:
                    out.append([edge[0], edge[1]])
                    if edge[1] not in next_level and edge[1] not in leaves:
                        next_level.append(edge[1])
                elif edge[1] in curent_level:
                    if edge[1] not in next_level and edge[1] not in already_done and edge[0] not in already_done:
                        out.append([edge[1], edge[0]])
                        if edge[1] not in leaves:
                            next_level.append(edge[0])
            already_done.extend(curent_level)
            curent_level = next_level.copy()
            next_level = []
        return out

    @staticmethod
    def find_leaf_nodes(edge_list: Union[List[List[str]], np.ndarray]) -> List[str]:
        """For a given list of edges will return a list of all leaf nodes.

        ### Args:
            - edge_list (list): A list of edges that represents a stemma tree.

        ### Returns:
            - list: The list of all leaf nodes in the tree.
        """
        out = []
        if not isinstance(edge_list, np.ndarray):
            edges = np.array(edge_list)
        unique_elements, counts = np.unique(edges[:, 0], return_counts=True)
        out.extend(np.setdiff1d(unique_elements[counts == 1], edges[:, 1]).tolist())
        unique_elements, counts = np.unique(edges[:, 1], return_counts=True)
        out.extend(np.setdiff1d(unique_elements[counts == 1], edges[:, 0]).tolist())
        return out

    @staticmethod
    def find_midpoint_root(edge_list: List[List[str]],
                           dist_dict: Union[Dict[str, Union[float, int]], None] = None) -> str:
        """For a given edge list will return the node label that is the midpoint between the 2 leaf nodes that are the furthest apart.

        ### Args:
            - edge_list (list): A list of edges that represents a stemma tree.
            - dist_dict (dict, Optional): A dictionary with all the edges of the tree as key in format "parent,child".
            If it is not specified thie distance beween each node will be assumed to be 1.
            And the distance between the nodes as value.

        Returns:
            - str: The label of the node that is the midpoint between the 2 leaf nodes that are the furthest apart.
        """
        leaves = Utils.find_leaf_nodes(edge_list)
        dict_connect = Utils.dict_of_connections(edge_list)
        longest = 0.0
        # Find longest path
        while len(leaves) > 1:
            current_node = leaves.pop(0)
            for leaf in leaves:
                length, path = Utils.find_path_length(
                    dict_connect, current_node, leaf, dist_dict, get_path=True)
                if length > longest:
                    longest = length
                    longest_path = path
        # Finding the middle of the path
        if dist_dict:
            distance = 0.0
            middistance = longest/2
            for idx in range(len(longest_path)-1):
                if dist_dict.get(f"{longest_path[idx]},{longest_path[idx+1]}") != None:
                    dist_dict_key = f"{longest_path[idx]},{longest_path[idx+1]}"
                else:
                    dist_dict_key = f"{longest_path[idx+1]},{longest_path[idx]}"
                distance += dist_dict[dist_dict_key]
                if distance > middistance:
                    if abs(distance - middistance) < abs(distance - dist_dict[dist_dict_key] - middistance):
                        return longest_path[idx+1]
                    else:
                        return longest_path[idx]
        return longest_path[int(len(longest_path)/2)]

    @staticmethod
    def find_path_length(connections: Union[Dict[str, List[str]], List[List[str]], np.ndarray],
                         start: str,
                         target: str,
                         dist_dict: Union[Dict[str, Union[float, int]], None] = None,
                         get_path: bool = False) -> Union[Union[float, int], Tuple[Union[float, int], List[str]]]:
        """For a given list of edges and a starting node and ending node will return the lenght between both nodes.

        ### Args:
            - connections (dict, list): Ether a list of edges between all nodes in the tree.
            Or a dictionary with node labels as keys and a list of connected node labels as values.
            - start (str): The node the search will start from.
            - end (str): The node that the search will end at.
            - dist_dict (dict, Optional): Dictionary with the edge label as key in format "parent,child" and length of the edge as value.
            If not specified the lenght of each edge will be assumed to be 1.
            - get_path (bool, Optional): If true then function will return a both the distance and the list containing all nodes in the path.

        ### Returns:
            - float: The total distance between the start node and the end node.
            - tuple: If get_path is true will returns total distance between the start node in first position of a tuple,
            and the list containing the path between both nodes in second position.

        ### Raises:
            - RuntimeError: If path between 2 successive nodes is not referenced in dist_dict.
        """
        if isinstance(connections, (list, np.ndarray)):
            connections = Utils.dict_of_connections(connections)
        path = Utils.find_path(connections, start, target)
        if not dist_dict:
            out = len(path) - 1
        else:
            out = 0
            for idx in range(len(path)-1):
                edge_dist = dist_dict.get(f"{path[idx]},{path[idx+1]}")
                if edge_dist == None:  # Yes it has to be "edge_dist == None" as edge_dist can be 0.0
                    edge_dist = dist_dict.get(f"{path[idx+1]},{path[idx]}")
                if edge_dist != None:
                    out += edge_dist
                else:
                    raise RuntimeError(f"Nor \"{path[idx]}, {path[idx+1]}\" or \"{path[idx+1]},{path[idx]}\" in not a key in dict_of_connections.")
        if get_path:
            return out, path
        return out

    @staticmethod
    def find_path(tree: Union[Dict[str, List[str]], List[List[str]]],
                  start: str,
                  target: str) -> List[str]:
        # TODO: Check that this works for cyclic graphs for future contamination implementation
        """For a given list of edges and a starting node and ending node will return the lenght between both nodes.

        ### Args:
            - dict_of_connections (dict): A dictionary representation of a tree. With the node label as key and a list of all its connecting nodes as value.
            - start (str): The node the search will start from.
            - target (str): The node that the search will end at.

        ### Returns:
            - list: The list of all the nodes between the 2 points. Will return an empty list if ether the start or target are not in dict_of_connections.
        """
        if isinstance(tree, (list, np.ndarray)):
            tree = Utils.dict_of_connections(tree)
        path: List[str] = []
        if not tree.get(start) or not tree.get(target):
            return path
        def dfs(current: str,
                current_path: List[str]) -> bool:
            """Runs recursivly through dict_of_connections and adds or removes nodes to path.

            ### Args:
                - current (str): The current node in the search.
                - current_path (list): The list of the path up to this point.

            ### Returns:
                - bool: Indicates if should proceed to next step.
            """
            current_path.append(current)
            if current == target:
                path.extend(current_path)
                return True
            for child in tree[current]:
                if child not in current_path and dfs(child, current_path):
                    return True
            current_path.pop()
            return False
        dfs(start, [])
        return path

    @staticmethod
    def dict_of_connections(tree: Union[List[List[str]], np.ndarray]) -> Dict[str, List[str]]:
        """For a given edge list or Stemma will return a dictionary with all the nodes labels as keys and the list of all the node labels each node is connected to.

        ### Args:
            - tree (list, numpy.ndarray): The Stemma or edge list for which the dictionary of connections will be built (Will be converted to np.array).

        ### Returns:
            - dict: A dictionary of connections for each node present in the tree.

        ### Raises:
            - ValueError: If tree parameter is not of type list.
            - ValueError: If tree of type list and numpy.array(tree).shape[1] != 2 and numpy.array(tree).shape[1] != 2.
        """
        if isinstance(tree, (list, np.ndarray)):
            if not isinstance(tree, np.ndarray):
                tree = np.array(tree)
            if len(tree.shape) != 2 or tree.shape[1] != 2:
                raise ValueError(f"The list specified as tree parameter has shape {tree.shape}. It must be of shape (n,2).")
            out: Dict[str, List[str]] = {}
            for edge in tree:
                if not out.get(edge[0]):
                    out.update({edge[0]: [edge[1]]})
                else:
                    out[edge[0]].append(edge[1])
                if not out.get(edge[1]):
                    out.update({edge[1]: [edge[0]]})
                else:
                    out[edge[1]].append(edge[0])
        else:
            raise ValueError(
                "tree parameter must be of type list or numpy.ndarray.")
        return out
