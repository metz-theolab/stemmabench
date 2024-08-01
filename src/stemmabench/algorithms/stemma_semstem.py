from typing import Callable, Dict, Union, Tuple, List, Any
from numpy import array, log, ones, identity, zeros, dot, abs
from copy import deepcopy
from math import inf
from random import gauss
import os
import time
import shutil
import math
import numpy as np
from concurrent.futures import ThreadPoolExecutor
# from networkx import minimum_spanning_tree, Graph
# from pgmpy.estimators import TreeSearch #Chow-Liu algorithm [4]
from stemmabench.algorithms.stemma_algorithm import StemmaAlgo
from stemmabench.algorithms.manuscript_in_tree_base import ManuscriptInTreeBase
from stemmabench.algorithms.manuscript_in_tree import ManuscriptInTree
from stemmabench.algorithms.utils import Utils
from stemmabench.algorithms.manuscript_in_tree_empty import ManuscriptInTreeEmpty


class StemmaSemstem(StemmaAlgo):
    """Class that constructs a stemma using the Semstem algorithm.

    ### Attributes:
        - folder_path (str): The path to the folder containing all the texts.
        - manuscripts (dict): The dictionay of all the texts with text labels as keys and texts as values.
        - distance (Callable): The function to be used as a distance metric.
        - _dist_matrix (numpy.ndarray): The distance matrix
        - _rooting_method (str): The rooting method used on the tree resulting from Neighbor-Joining algorithm.
    """

    def __init__(self,
                 iterationmax: int,
                 distance: Union[Callable, None] = None,
                 nj_edge_list: Union[str, None] = None,
                 keep_dot_files: bool = False) -> None:
        """
        Constructor for the StemmaSemstem class.

        ### Args:
            - iterrationmax (str): The maximum number of optimisation iterations that will be performed. 
            - distance (Callable, Optional): A function that takes 2 strings as parameters and returns a numeric value which is
            the distance between the 2 strings. Is passed to the Neighbor-Joining algorithm to initialise the first tree.
            - nj_edge_list (str, Optional): The edge list of a previously constructed Neighbor-Joining tree.
            - keep_dot_files (bool): Indicates if the dot files should be outputted.

        Raises:
            - ValueError: If the distance parameter does not respect d(x,x) = 0 or d(x,y) = d(y,x).
        """
        super().__init__()
        if distance and nj_edge_list:
            raise RuntimeError(
                "Only one of distance or nj_edge_list parameters must be specified.")
        elif not distance and not nj_edge_list:
            raise RuntimeError(
                "At least one of distance or nj_edge_list parameters must be specified.")
        self._distance: Union[Callable, None] = distance
        self._nj_edge_list: Union[str, None] = nj_edge_list
        self._iterationmax: str = iterationmax
        self._keep_dot_files: bool = keep_dot_files
        self.log_string: str = None
        self._dist_matrix: np.ndarray

    def compute(self, folder_path: str) -> ManuscriptInTreeBase:
        """Builds the stemma tree. If the distance is specified in function call it will surplant the existing distance if it exists.

        ### Args:
            - folder_path (str): The path to the folder containing the texts. The path specified here will surplant the previous path defined in constructor.
            !!! All .txt files in this folder must be files containing Manuscript texts unless the file name contains the substring "edge" !!!

        Returns:
            - Manuscript: The root of the stemma with the rest of its tree as its children.
        """
        super().compute(folder_path)
        # If no valid NJ edges available calculate the NJ edges
        if not self._nj_edge_list:
            self.dist(self._distance)
        edges = self.semuniform2(
            folder_path, self._iterationmax)[2]#, folder_path)[2]
        print(f"StemmaSemstem.compute(): {edges}")
        print(f"StemmaSemstem.compute(): man list: {list(self.manuscripts.keys())}")
        root = Utils.find_root(edges)
        print(f"StemmaSemstem.compute():root: {root[0][0]}")
        if root[0][0] == "N":
            return ManuscriptInTreeEmpty(parent=None, recursive=Utils.dict_from_edge(
                edge_list=edges), text_list=list(self.manuscripts.keys()))
        else:
            return ManuscriptInTree(parent=None, recursive=Utils.dict_from_edge(
                edge_list=edges), text_list=list(self.manuscripts.keys()))

    def readfiles(self, input_folder: str) -> Tuple[Dict[str, int], Dict[Any, Any], Dict[str, str]]:
        """Reads all txt files present in the provided folder that do not containe the substring edge in their name, 
        and builds the outputs requered to start the semstem  algorithm.

        ### Args:
            - input_folder (str): The folder in which can be found the texts.

        ### Returns:
            - tuple: A tuple containing: (a dictionary with the name of eache manuscitp as key and their order as value,
                                          a dictionary representation of the tree in semstem format,
                                          a dictionary with manuscript labels as keys and texts as values)
        """
        manuscripts = {}

        files: List[str] = list(filter(lambda x: "edge" not in x and os.path.isfile(input_folder + "/" + x) and ".txt" in x,
                                       os.listdir(input_folder)))
        for text in files:
            manuscripts.update(
                {text.replace(".txt", ""): open(input_folder + "/" + text, "r").read()})
        namelist = {}
        datadic = {}
        for label in enumerate(list(manuscripts.keys())):
            namelist.update({label[1]: label[0]})
        return (namelist, datadic, manuscripts)

    def dist(self, distance: Callable) -> None:
        """Builds the distance matix based on the provided distance function and sets the attribute _dist_matrix.

        ### Args:
            - distance (Callable): A function that takes as parameters 2 strings and that returns the distance between them.
        """
        self._dist_matrix = np.zeros(
            (len(self._manuscripts), len(self._manuscripts)), dtype=float)
        keys = list(self._manuscripts.keys())
        keys.sort()
        labels = {}
        man_range = range(len(self._manuscripts))
        with ThreadPoolExecutor(max_workers=len(self._manuscripts)*len(self._manuscripts)) as executor:
            for row in man_range:
                for col in man_range:
                    if col >= row:
                        labels.update({f"{keys[row]},{keys[col]}": executor.submit(
                            distance, self._manuscripts[keys[row]], self._manuscripts[keys[col]])})
        for row in enumerate(keys, start=0):
            for col in enumerate(keys, start=0):
                if col[0] >= row[0]:
                    self._dist_matrix[row[0]][col[0]
                                              ] = labels[f"{row[1]},{col[1]}"].result()
        self._dist_matrix = self._dist_matrix + self._dist_matrix.transpose()

    def convert_edges_to_semtree(self, edges: List[str]) -> Dict[str, List[str]]:
        """Converts an edge list to a tree structure.

        ### Args:
            - edges (list): Edge list to be converted to a tree structure.

        ### Returns:
            - dict: A dict representing the stemma tree in StemWeb format.
        """
        out = {}
        for edge in edges:
            if not out.get(edge[0]):
                self.createnode(out, edge[0])
            if not out.get(edge[1]):
                self.createnode(out, edge[1])
            self.addedge(out, edge[0], edge[1])
            # print(f"edge: {edge}, node0: {out[edge[0]]}, node1: {out[edge[1]]}")
        return out

    def instanciate_nj_tree_output_from_edge(self, edge_list: List[List[str]]) -> Dict[str, Dict[str, str]]:
        """Function used to skip JN if edges have already been calculated.
        !!!! The edge list must have been outputed from stemmabench.algorithms.stemma_NJ and not have been modified in any way.  
         This includes rooting the tree. (generated with rooting_method = "none") !!!!

         !!!!!!!!!! Not tested yet !!!!!!!!!!!!!!!
        """
        # treeroot: The root of the tree
        # nodeorder: list of all nodes added to the tree in order from bottom to top
        # nodehidden: List of all the hidden/empty nodes
        # nodeleaf: List of leaf nodes
        nodeorder = []
        temp = ""
        nodehidden = []
        nodeleaf = []
        for edge in edge_list:
            if edge[0][0] == "N":
                if edge[0] not in nodehidden:
                    nodehidden.append(edge[0])
            elif edge[0] not in nodeleaf:
                nodeleaf.append(edge[0])
            if edge[1][0] == "N":
                if edge[1] not in nodehidden:
                    nodehidden.append(edge[1])
            elif edge[1] not in nodeleaf:
                nodeleaf.append(edge[1])
            if edge[1] not in nodeorder:
                nodeorder.append[edge[1]]
            if edge[0] == temp:
                if edge[0] not in nodeorder:
                    nodeorder.append[edge[0]]
            else:
                if temp not in nodeorder:
                    nodeorder.append[temp]
                if edge[0] not in nodeorder:
                    nodeorder.append[edge[0]]
            temp = edge[0]
        return (Utils.find_root(edge_list), nodeorder, nodehidden, nodeleaf, self.convert_edges_to_semtree(edge_list))

    def createnode(self, treedic, node):
        treedic[node] = {}
        treedic[node]['parent'] = []
        treedic[node]['child'] = []
        treedic[node]['neighbor'] = []

    def addedge(self, treedic, parent, child):
        treedic[child]['parent'].append(parent)
        treedic[child]['neighbor'].append(parent)

        treedic[parent]['child'].append(child)
        treedic[parent]['neighbor'].append(child)

    def removeedge(self, treedic, parent, child):
        treedic[child]['parent'].remove(parent)
        treedic[child]['neighbor'].remove(parent)
        treedic[parent]['child'].remove(child)
        treedic[parent]['neighbor'].remove(child)

    def njtree(self, textdata):

        def _build_edges(self) -> Tuple[Dict[str, float], List[List[str]]]:
            """Builds list of edges as well as the associated dictionayr containing the edge distances.

            ### Returns:
                - dict: The dictionary with edges as keys and distences as values.
                - list: List of edges.
            """
            temp_dist_matrix = self._dist_matrix.copy()
            labels = sorted(list(self.manuscripts.keys()))
            edges_labels = []
            edges_distance = []
            while temp_dist_matrix.shape[0] > 2:
                temp_dist_matrix, labels, df, f_lab, dg, g_lab = _agglo(self,
                                                                        temp_dist_matrix, labels)
                edges_labels.append([labels[len(labels)-1], f_lab])
                edges_distance.append(df)
                edges_labels.append([labels[len(labels)-1], g_lab])
                edges_distance.append(dg)
            edges_distance.append(temp_dist_matrix[0, 1])
            edges_labels.append([labels[0], labels[1]])
            edges_dict_labels = [l[0] + "," + l[1] for l in edges_labels]
            return {edges_dict_labels[i]: edges_distance[i] for i in range(len(edges_dict_labels))}, edges_labels

        def _agglo(self, dist_mat: np.ndarray, labels: List[str]) -> Tuple[np.ndarray, List[str], float, str, float, str]:
            """Performs one step in the distance matrix agglomeration process and returns all information needed for Neighbour Joining.
               Does not work for matrix 2*2. 

            ### Args:
                - dist_mat (np.ndarray): A !!!insert name here!!! distance matrix to be agglomerated by one step.
                - labels (list): The list of labels that corespond to the distance matrix labels. Can be found in manuscrips.keys().

            ### Returns:
                - np.ndarray: The distance matrix agglomerated by one step.
                - list: The list of labels for the new agglomerated matrix.
                - float: Distance between the the agglomerrated manuscript f and the new node u.
                - str: The label of the manuscript f.
                - float: Distance between the the agglomerrated manuscript g and the new node u.
                - str: The label of the manuscript g.
            """
            # Calculate divergence matrix
            Q = (dist_mat.shape[0] - 2) * dist_mat - (dist_mat.sum(
                axis=0).reshape((dist_mat.shape[0], 1)) + dist_mat.sum(axis=1))
            Q = Q.round(7)
            np.fill_diagonal(Q, 0)
            # Find min of divergence matrix
            coord = np.argwhere(Q == Q.min())[0]
            # The distances d(f,u) and d(g,u)
            df = round(0.5*dist_mat[coord[0], coord[1]] + (dist_mat[coord[0],
                                                                    ].sum() - dist_mat[coord[1],].sum())/(2*(dist_mat.shape[0] - 2)), 7)
            dg = round(dist_mat[coord[0], coord[1]] - df, 7)
            # Removed agglomerated rows and columns
            out = np.delete(np.delete(dist_mat, obj=coord, axis=0),
                            obj=coord, axis=1).round(7)
            # Vector to be appended to side of reduced matrix
            vect = 0.5*(np.delete(dist_mat[coord[0],], [coord[0], coord[1]]) + np.delete(
                dist_mat[coord[1],], [coord[0], coord[1]]) - dist_mat[coord[0], coord[1]])
            vect = vect.round(7)
            # Stick new U distance vectors on the right and bottom of the original distance matrix
            out = np.row_stack((np.column_stack((out, vect)),
                               np.append(vect, 0))).round(7)
            # Extracting labels and creating new node label
            f_label = labels[coord[0]]
            g_label = labels[coord[1]]
            new_label = "N_" + \
                str(self._dist_matrix.shape[0] - len(labels) + 1)
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
            # Creates the output requred by the semstem algo
            if f_label not in nodeorder:
                nodeorder.append(f_label)
            if g_label not in nodeorder:
                nodeorder.append(g_label)
            if new_label not in nodeorder:
                nodeorder.append(new_label)
            if new_label not in nodehidden:
                nodehidden.append(new_label)
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
            labels = list(np.delete(labels, coord))
            labels.append(new_label)
            return out, labels, df, f_label, dg, g_label

        nodeorder = []
        nodehidden = []
        nodeleaf = []
        for m in self.manuscripts:
            nodeleaf.append(m)

        edge_dict, edge_list = _build_edges(self)
        treeroot = Utils.find_root(edge_list)
        treedic = self.convert_edges_to_semtree(edge_list)
        # treeroot: The root of the tree
        # nodeorder: list of all nodes added to the tree in order from bottom to top
        # nodehidden: List of all the hidden/empty nodes
        # nodeleaf: List of leaf nodes
        return (treeroot, nodeorder, nodehidden, nodeleaf, treedic)

    def removehidden(self, nodehiddenori, treedicori):
        treedic = deepcopy(treedicori)
        nodehidden = list(nodehiddenori)
        finnish = 0
        while (finnish == 0):
            finnish = 1
            for nodei in nodehidden:
                if len(treedic[nodei]['neighbor']) == 2:
                    finnish = 0
                    nodehidden.remove(nodei)
                    if len(treedic[nodei]['child']) == 2:  # root
                        childi = treedic[nodei]['child'][0]
                        childj = treedic[nodei]['child'][1]
                        self.addedge(treedic, childi, childj)
                        self.removeedge(treedic, nodei, childi)
                        self.removeedge(treedic, nodei, childj)
                        del treedic[nodei]

                    if len(treedic[nodei]['child']) == 1:  # not root
                        childi = treedic[nodei]['child'][0]
                        parenti = treedic[nodei]['parent'][0]
                        self.addedge(treedic, parenti, childi)
                        self.removeedge(treedic, nodei, childi)
                        self.removeedge(treedic, parenti, nodei)
                        del treedic[nodei]
                else:
                    if len(treedic[nodei]['neighbor']) == 1:
                        finnish = 0
                        nodehidden.remove(nodei)
                        if len(treedic[nodei]['parent']) == 1:
                            parenti = treedic[nodei]['parent'][0]
                            self.removeedge(treedic, parenti, nodei)
                            del treedic[nodei]
                        else:
                            childi = treedic[nodei]['child'][0]
                            self.removeedge(treedic, nodei, childi)
                            del treedic[nodei]
        return treedic, nodehidden

    def readfile(self, inputfile):
        import re
        # readfile('heinrichi.nex')
        import math
        file = open(inputfile, 'r')
        nexdata = file.read()
        nexdata = nexdata.replace('-', '?')
        nexdata = nexdata.replace(' ', '\t')
        file.close()

        nexdata = nexdata.split('\n')
        for i in range(len(nexdata)):
            if len(re.findall(r'matrix', nexdata[i].lower())) > 0:
                startline = i+1
        for i in range(len(nexdata)-1, -1, -1):
            if len(re.findall(r'end', nexdata[i].lower())) > 0:
                endline = i
        nexdata = nexdata[startline:endline]

        namelist = {}
        datalist = []
        textdata = {}
        nodenumber = len(nexdata)

        index = 0
        for nexdatai in nexdata:
            nexdatai = nexdatai.strip()
            nexdatai = nexdatai.strip(';')
            nexdatai = nexdatai.split('\t', 1)
            namelist[nexdatai[0].strip()] = index
            index = index+1
            textdatai = nexdatai[1].strip()
            textdata[nexdatai[0].strip()] = textdatai
            textlen = len(textdatai)
            if len(datalist) == textlen:
                for i in range(textlen):
                    datalist[i].append(textdatai[i])
            else:
                for i in range(textlen):
                    datalist.append([textdatai[i]])

        datadic = {}
        dataori = []
        for datalisti in datalist:
            if '?' in datalisti:
                temp = list(set(datalisti))
                temp.remove('?')
                uniquenumber = len(temp)
            else:
                uniquenumber = len(list(set(datalisti)))

            if len(list(set(datalisti))) == 1:
                datalist.remove(datalisti)
            else:
                chardic = {'?': '?'}
                j = 0
                letters = 'abcdefghijklmnopqrstuvwxyz'
                datalistrefinei = []
                for i in datalisti:
                    if i in chardic.keys():
                        datalistrefinei.append(chardic[i])
                    else:
                        datalistrefinei.append(
                            letters[j-int(26*(math.floor(j/26)))])
                        chardic[i] = letters[j-int(26*(math.floor(j/26)))]
                        j = j+1
                dataori.append(datalistrefinei)
                if uniquenumber in datadic.keys():
                    datadic[uniquenumber].append(datalistrefinei)
                else:
                    datadic[uniquenumber] = [datalistrefinei]
        return (namelist, datadic, textdata)

    def nohiddeninitial(self, textdata):
        namelist = list(textdata.keys())
        treeroot = namelist[0]
        nodeleaf = [namelist[-1]]
        nodehidden = []
        nodeorder = [treeroot]
        treedic = {}
        self.createnode(treedic, treeroot)
        for i in range(len(namelist)-1):
            self.createnode(treedic, namelist[i+1])
            self.addedge(treedic, namelist[i], namelist[i+1])
            nodeorder[0:0] = [namelist[i+1]]
        return (treeroot, nodeorder, nodehidden, nodeleaf, treedic)

    def mst(self, weightmatrix, weightmatrixindex):

        treedic = {}
        nodelist = list(weightmatrixindex)
        nodelisttemp = array(list(nodelist))
        # nodenumber = len(list(weightmatrixindex))
        treeroot = nodelist[0]
        nodelist.remove(treeroot)

        nodeaddedindex = (nodelisttemp == treeroot)
        nodeadded = list(array(nodelisttemp)[nodeaddedindex])
        noderemainindex = (nodelisttemp != treeroot)
        noderemain = list(array(nodelisttemp)[noderemainindex])

        nodeorder = [treeroot]
        self.createnode(treedic, treeroot)
        nodeleaf = list(weightmatrixindex)
        while len(nodelist) > 0:

            weightmatrixtemp1 = weightmatrix[nodeaddedindex, :]
            weightmatrixtemp = weightmatrixtemp1[:, noderemainindex]

            maxindex = weightmatrixtemp.argmax()

            maxrowindex = int(math.floor(maxindex / len(noderemain)))
            maxcolindex = int(maxindex % len(noderemain))
            edgefromadded = nodeadded[maxrowindex]
            edgefromremain = noderemain[maxcolindex]
            self.createnode(treedic, edgefromremain)
            self.addedge(treedic, edgefromadded, edgefromremain)

            nodeaddedindex[nodelisttemp == edgefromremain] = True
            nodeadded = list(array(nodelisttemp)[nodeaddedindex])
            noderemainindex[nodelisttemp == edgefromremain] = False
            noderemain = list(array(nodelisttemp)[noderemainindex])
            nodeorder[0:0] = [edgefromremain]
            nodelist.remove(edgefromremain)
            if edgefromadded in nodeleaf:
                nodeleaf.remove(edgefromadded)
        return treeroot, nodeorder, nodeleaf, treedic

    def messagepassingu(self, treeroot, nodeorder, nodehidden, nodeleaf, treedic, textbyline, linerepeat, namelist):
        # import operator
        # reduce(operator.mul, (3, 4, 5))
        probsame = 0.95

        textbylinearray = array(list(textbyline))
        linenumber = len(textbyline)
        textdiffer = list(set(textbyline[0]))
        if '?' in textdiffer:
            textdiffer.remove('?')
        textdiffer.sort()
        textdiffernumber = len(textdiffer)
        probelement = 1.0/float(textdiffernumber)  # prob of a
        probchangearray = identity(textdiffernumber, float)*probsame
        probchangearray[probchangearray == 0] = (
            1-probsame)/textdiffernumber  # prob a->b [aa ab] [ba bb]
        probchangearrayT = probchangearray.T
        # log matrix: log P(a->b(t)) - log P(b)
        logarray = log(probchangearray) - \
            log(ones((textdiffernumber, textdiffernumber))*probelement)

        smalludic = {}
        bigudic = {}
        probnodedic = {}
        probedgedic = {}
        countdic = {}
        weightdic = {}

        # ++++++++++++++++++++++++++++++++++++++#
        # big u, small u message

        for nodei in nodeorder:  # from leaf to root
            if nodei in nodeleaf:  # big u for leaf nodes
                for parenti in treedic[nodei]['parent']:
                    bigudic[(nodei, parenti)] = zeros(
                        (linenumber, textdiffernumber))
                    if namelist.has_key(nodei):  # known nodes
                        texti = textbylinearray[:, namelist[nodei]]
                        # assign for know character
                        for textdifferi in range(textdiffernumber):
                            bigudic[(nodei, parenti)][texti ==
                                                      textdiffer[textdifferi], textdifferi] = 1
                        bigudic[(nodei, parenti)][texti == '?', :] = 1
                    else:  # unknown nodes
                        bigudic[(nodei, parenti)] = ones(
                            (linenumber, textdiffernumber))
            else:  # big u for internal nodes
                for parenti in treedic[nodei]['parent']:
                    if namelist.has_key(nodei):  # known nodes
                        bigudic[(nodei, parenti)] = zeros(
                            (linenumber, textdiffernumber))
                        texti = textbylinearray[:, namelist[nodei]]
                        # assign for know character
                        for textdifferi in range(textdiffernumber):
                            bigudic[(nodei, parenti)][texti ==
                                                      textdiffer[textdifferi], textdifferi] = 1
                        unknownpositioni = (texti == '?')
                        bigudic[(nodei, parenti)][unknownpositioni, :] = 1
                        for childi in treedic[nodei]['child']:
                            bigudic[(nodei, parenti)][unknownpositioni, :] = bigudic[(nodei, parenti)
                                                                                     ][unknownpositioni, :]*smalludic[(childi, nodei)][unknownpositioni, :]
                    else:  # unkonwn nodes
                        bigudic[(nodei, parenti)] = ones(
                            (linenumber, textdiffernumber))
                        for childi in treedic[nodei]['child']:
                            bigudic[(nodei, parenti)] = bigudic[(nodei, parenti)] * \
                                smalludic[(childi, nodei)]

            # small u
            for parenti in treedic[nodei]['parent']:
                smalludic[(nodei, parenti)] = dot(
                    bigudic[(nodei, parenti)], probchangearrayT)

        nodeorderreverse = list(nodeorder)
        nodeorderreverse.reverse()

        for nodei in nodeorderreverse:  # from root to leaf
            if nodei not in nodeleaf:  # big u
                if namelist.has_key(nodei):
                    texti = textbylinearray[:, namelist[nodei]]
                    unknownpositioni = (texti == '?')
                    # pass message to all children
                    for childi in treedic[nodei]['child']:
                        bigudic[(nodei, childi)] = zeros(
                            (linenumber, textdiffernumber))
                        # assign for known character
                        for textdifferi in range(textdiffernumber):
                            bigudic[(nodei, childi)][texti ==
                                                     textdiffer[textdifferi], textdifferi] = 1

                        neighbori = list(treedic[nodei]['neighbor'])
                        neighbori.remove(childi)
                        bigudic[(nodei, childi)][unknownpositioni, :] = 1
                        for neighborii in neighbori:
                            bigudic[(nodei, childi)][unknownpositioni, :] = bigudic[(nodei, childi)
                                                                                    ][unknownpositioni, :]*smalludic[(neighborii, nodei)][unknownpositioni, :]
                else:  # unknown nodes
                    for childi in treedic[nodei]['child']:
                        neighbori = list(treedic[nodei]['neighbor'])
                        neighbori.remove(childi)
                        bigudic[(nodei, childi)] = ones(
                            (linenumber, textdiffernumber))
                        for neighborii in neighbori:
                            bigudic[(nodei, childi)] = bigudic[(nodei, childi)] * \
                                smalludic[(neighborii, nodei)]
            # small u
            for childi in treedic[nodei]['child']:
                smalludic[(nodei, childi)] = dot(
                    bigudic[(nodei, childi)], probchangearrayT)

        # ++++++++++++++++++++++++++++++++++++++#
        # prob of characters
        for nodei in nodeorder[0:(-1)]:  # from leaf to root
            probnodedic[nodei] = probelement * \
                bigudic[(nodei, treedic[nodei]['parent'][0])] * \
                smalludic[(treedic[nodei]['parent'][0], nodei)]
            normalizingvector = array([probnodedic[nodei] .sum(1)])
            normalizingmat = normalizingvector .repeat(
                [textdiffernumber], axis=0)
            probnodedic[nodei] = probnodedic[nodei] / (normalizingmat.T)

        probnodedic[treeroot] = probelement * \
            bigudic[(treeroot, treedic[treeroot]['child'][0])] * \
            smalludic[(treedic[treeroot]['child'][0], treeroot)]
        normalizingvector = array([probnodedic[treeroot] .sum(1)])
        normalizingmat = normalizingvector .repeat([textdiffernumber], axis=0)
        probnodedic[treeroot] = probnodedic[treeroot] / (normalizingmat.T)

        # ++++++++++++++++++++++++++++++++++++++#
        # prob of edge of linked nodes
        for nodei in nodeorder[0:(-1)]:  # from leaf to root
            for parenti in treedic[nodei]['parent']:
                probedgedic[(nodei, parenti)] = []
                probedgedic[(parenti, nodei)] = []
                for linei in range(linenumber):
                    proba = probelement
                    biguij = bigudic[(nodei, parenti)][linei, :]
                    biguji = bigudic[(parenti, nodei)][linei, :]
                    probab = probchangearray  # [[a->a  a->b][b->a  b->b]]

                    # s1 =[[a a] [b b]] = p(a) * Uij(a)
                    s1 = array([proba * biguij]
                               ).T.repeat([textdiffernumber], axis=1)

                    # s2 = s1 * p(a->b)
                    s2 = s1 * probab
                    # s3 = s2 * Uji(b)  [[a b][a b]]
                    s3 = s2 * \
                        (array([biguji]).repeat([textdiffernumber], axis=0))
                    s4 = s3/sum(s3)
                    probedgedic[(nodei, parenti)].append(s4)
                    probedgedic[(parenti, nodei)].append(s4.T)

        # ++++++++++++++++++++++++++++++++++++++#
        # prob count
        nodepooled = [treeroot]
        for nodei in nodeorderreverse[1:]:
            for nodej in nodepooled:
                if nodej in treedic[nodei]['parent']:
                    # first repeat array, then sum
                    countdic[(nodei, nodej)] = (
                        array(probedgedic[(nodei, nodej)]).repeat(linerepeat, axis=0)).sum(0)
                    # weight = sum (S(a->b) * log array)
                    weightdic[(nodei, nodej)] = sum(
                        countdic[(nodei, nodej)] * logarray)
                    weightdic[(nodej, nodei)] = weightdic[(nodei, nodej)]
                else:
                    parenti = treedic[nodei]['parent'][0]
                    probedgedic[(nodei, nodej)] = []
                    probedgedic[(nodej, nodei)] = []
                    weightdic[(nodei, nodej)] = 0
                    # sum(Pij(a->b)*Pji(b->c)/P(j=b)) by b
                    for linei in range(linenumber):
                        probmiddle = array([probnodedic[parenti][linei]]
                                           ).T.repeat(textdiffernumber, axis=1)
                        probmiddle[probmiddle == 0] = 1
                        probunlinkedi = dot(probedgedic[(nodei, parenti)][linei], probedgedic[(
                            parenti, nodej)][linei]/probmiddle)

                        probedgedic[(nodei, nodej)].append(probunlinkedi)
                        probedgedic[(nodej, nodei)].append(probunlinkedi.T)

                        weightdic[(nodei, nodej)] = weightdic[(nodei, nodej)] + \
                            sum(probunlinkedi*logarray*linerepeat[linei])
                    weightdic[(nodej, nodei)] = weightdic[(nodei, nodej)]
            # print "%s" % (weightdic[(nodej,nodei)])
            nodepooled.append(nodei)

        return (weightdic)

    def treetodot(self, treedic, nodeorder, nodehidden, resultfolder, resultfile):
        # how to print dot file 'neato -Tpdf -Gstart=rand x.dot > x.pdf'
        edges = []  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
        import os
        outstr = 'graph clustering {\n\tsize=\"5,5\"\n\n'
        for node in nodeorder:
            if node in nodehidden:
                outstr = outstr + '\t' + node + ' [shape=point];\n'
            else:
                outstr = outstr + '\t' + node + \
                    ' [label=\"' + node + '\" shape=plaintext fontsize=24];\n'
        outstr = outstr + '\n'
        for nodei in nodeorder:
            if len(treedic[nodei]['parent']) > 0:
                for nodej in treedic[nodei]['parent']:
                    outstr = outstr + '\t' + nodei + ' -- ' + nodej + ';\n'
                    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
                    edges.append([str(nodej), str(nodei)])
                    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
        outstr = outstr + '}'
        # filename = os.path.splitext(resultfile)[0]
        dot_file = os.path.join(resultfolder, resultfile) + '.dot'
        # svg_file = os.path.join(resultfolder, resultfile) + '.svg'
        file = open(dot_file, 'w')
        file.write(outstr)
        file.close()
        # os.system('neato -Tsvg -Gstart=rand ' + dot_file + ' > ' + svg_file)
        return edges

    def semuniform(self, input_folder, iterationmax, folder_path):
        # This section of the code initializes the variables used by the semstem algorithm.
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
        # If we don't have the pre calculated AND VALID (see instanciate_nj_tree_output_from_edge comments for details)
        # then calculate njtree
        if not self._nj_edge_list:
            # step 1 read file
            # namelist, datadic, textdata = readfile(inputfile)
            namelist, datadic, textdata = self.readfiles(input_folder)
            # step 2 initiation by nj tree
            treeroot, nodeorder, nodehidden, nodeleaf, treedic = self.njtree(
                textdata)
        # treeroot, nodeorder, nodehidden, nodeleaf, treedic = self.nohiddeninitial(textdata) # This line is used for a different version of the algorythm.
        else:
            treeroot, nodeorder, nodehidden, nodeleaf, treedic = self.instanciate_nj_tree_output_from_edge(
                self._nj_edge_list)
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
        # step 3 calculate weight matrix
        logstr = 'Start at' + str(time.gmtime()) + '\n'
        sigma = 0
        qscoreold = float("-inf")  # Inf)
        bestiteration = -1
        # treedicold = treedic
        # nodeorderold = nodeorder
        logvector = [['iteration'], ['sigma'], ['qscore']]
        # Simply modified output path
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
        # resfolder = "test_output_folder"
        resfoldertree = os.path.join(folder_path, 'tree')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
        if not os.path.exists(resfoldertree):
            os.makedirs(resfoldertree)

        for iteration in range(iterationmax):
            print(iteration)
            # print (time.gmtime())
    # if (iteration % 100) ==0:
    # print (iteration)
            weightmatrix = zeros((len(nodeorder), len(nodeorder)))
            weightmatrixwithnoise = zeros((len(nodeorder), len(nodeorder)))
            weightmatrixindex = list(nodeorder)
            for datadickey in datadic.keys():

                textbylinewithrepeat = datadic[datadickey]
                linerepeat = []
                textbyline = []
                for textbylinewithrepeati in textbylinewithrepeat:
                    if textbylinewithrepeati not in textbyline:
                        textbyline.append(textbylinewithrepeati)
                        linerepeat.append(1.0)
                    else:
                        lineindex = textbyline.index(textbylinewithrepeati)
                        linerepeat[lineindex] = linerepeat[lineindex]+1.0

                weightdic = self.messagepassingu(
                    treeroot, nodeorder, nodehidden, nodeleaf, treedic, textbyline, linerepeat, namelist)
                for ni in range(0, (len(nodeorder)-1)):
                    for nj in range((ni+1), len(nodeorder)):
                        weightmatrix[ni, nj] = weightmatrix[ni, nj] + \
                            weightdic[(nodeorder[ni], nodeorder[nj])]
                        weightmatrix[nj, ni] = weightmatrix[ni, nj]

            for ni in range(len(nodeorder)):
                for nj in range(len(nodeorder)):
                    if ni != nj:
                        weightmatrixwithnoise[ni,
                                              nj] = weightmatrix[ni, nj] + gauss(0, sigma)
                        weightmatrixwithnoise[nj,
                                              ni] = weightmatrixwithnoise[ni, nj]
                    else:
                        weightmatrixwithnoise[ni, ni] = float('inf')
            treeroot, nodeorder, nodeleaf, treedic = self.mst(
                weightmatrixwithnoise, weightmatrixindex)

            qscore = 0.0
            for nodei in nodeorder[0:(-1)]:
                qscore = qscore + weightmatrix[weightmatrixindex.index(
                    nodei), weightmatrixindex.index(treedic[nodei]['parent'][0])]

            logvector[0].append(iteration)
            logvector[1].append(sigma)
            logvector[2].append(qscore)

            if iteration > 10:
                if (abs(logvector[2][-2] - logvector[2][-3]) < 0.001) and (abs(logvector[2][-1] - logvector[2][-2]) < 0.001):
                    # print ('stop at' + str(iteration) + '\n')
                    break

            print(f"Scores current: {qscore} old: {qscoreold}")
            if qscore > qscoreold:
                # treedicold = treedic
                # nodeorderold = nodeorder
                qscoreold = qscore
                bestiteration = iteration

            treedicremoved, nodehiddenremoved = self.removehidden(
                nodehidden, treedic)
            out = self.treetodot(treedicremoved, treedicremoved.keys(),
                                 nodehiddenremoved, resfoldertree, str(iteration).zfill(4))

            if iteration >= 2:
                sigma = float(sigma0) * \
                    ((1.0-float(iteration)/float(iterationmax))**2.0)
            elif iteration == 1:
                sigma0 = 1.0 * max(abs(weightmatrix.min()),  # float(0.2)),  #
                                   abs(weightmatrix.max()))  # float(0.2)))  #
                sigma = sigma0
        # To my knoledge this section of code only creates a visual part to the output
        # treediclast, nodehiddenlast = removehidden(nodehidden, treedic)
        # tree2newick(treediclast ,treediclast.keys(),nodehiddenlast, resfoldertree,'treelast')

        # treedicbest, nodehiddenbest = removehidden(nodehidden, treedicold)
        # tree2newick(treedicbest ,treedicbest.keys(),nodehiddenbest, resfoldertree,'treebest')
        # utils.tree2img(self.newick_path, self.image_path, self.run_args['learnlength'], radial = False)

        logstr = logstr + 'End at' + str(time.gmtime()) + '\n' + 'best iteration is ' + str(
            bestiteration) + '\n' + 'best qscore is ' + str(qscoreold) + '\n\n\n'
        inumber = len(logvector)
        jnumber = len(logvector[0])
        for j in range(jnumber):
            for i in range(inumber):
                logstr = logstr + str(logvector[i][j]) + '\t'
            logstr = logstr.strip() + '\n'
        # logstr = logstr.strip()
        self.log_string = logstr.strip()
        print(self.log_string)
        # file = open("test_output", 'w')
        # file.write(logstr)
        # file.close()
        return (qscoreold, bestiteration, out)

    def semuniform2(self, folder_path, iterationmax):
        probsame = 0.9
        printtime = False
        #resfolder = inputfile
        # step 1 read file
        namelist, datadic, textdata = self.readfiles(folder_path)
        # step 2 initiation by nj tree
        # |<
        # (1)
        treeroot, nodeorder, nodehidden, nodeleaf, treedic = self.njtree(
            textdata)  # with hidden nodes
        # (2)
        # treeroot, nodeorder, nodehidden, nodeleaf, treedic = nohiddeninitial(textdata) #without hidden nodes
        # >|
        # resfolder = inputfile + '_res' #debug
        # define folder for resulting trees
        resfoldertree = os.path.join(folder_path, 'tree')
        # define result folder
        # create result folder and tree folder
        #if not os.path.exists(resfolder):
        #    os.makedirs(resfolder)
        #else:
        #    shutil.rmtree(resfolder)
        #    os.makedirs(resfolder)
        if not os.path.exists(resfoldertree):
            os.makedirs(resfoldertree)
        else:
            shutil.rmtree(resfoldertree)
            os.makedirs(resfoldertree)
        # print initial tree
        # |<
        # (1)
        # plot tree with removed hiddden nodes
        treedicremoved, nodehiddenremoved = self.removehidden(nodehidden, treedic)
        # treetodot(treedicremoved,treedicremoved.keys(),nodehiddenremoved, resfoldertree, str(0).zfill(4))
        # (2)
        # plot tree with NO removed hiddden nodes
        # treetodot(treedic,treedic.keys(),nodehidden, resfoldertree, str(0).zfill(4)+'_withhidden')
        # >|
        # step 3 calculate weight matrix
        logstr = 'The resulting folder is ' + folder_path + \
            '\n' + 'Start at ' + str(time.gmtime()) + '\n'
        sigma = 0  # <parameter>
        # initial sigma, will be calculated according to score matrix later
        rho = 0.001**(1/float(iterationmax-5))  # <parameter>
        # give initial value to [bestiteration treedicbest nodeorderbest probtreeallbest]
        probtreeallbest = float("-inf")
        bestiteration = 0
        treedicbest = deepcopy(treedic)
        nodeorderbest = deepcopy(nodeorder)
        # logvector store results in each iteration
        logvector = [['iteration'], ['sigma'], [
            'qscore'], ['probability']]  # <log>
        logvector[0].append(0)
        logvector[1].append(0)
        logvector[2].append(0)
        # <important
        stopsign = 0
        for iteration in range(1, iterationmax+1):
            # print time
            treedicprevious = deepcopy(treedic)
            nodeorderprevious = deepcopy(nodeorder)
            if printtime and (iteration < 4):
                timestart = time.time()
            if iterationmax > 100 and (iteration % 100) == 0:
                print('Now is iteration ' + str(iteration))
            if iterationmax <= 100 and (iteration % 10) == 0:
                print('Now is iteration ' + str(iteration))
            weightmatrix = zeros((len(nodeorder), len(nodeorder)))
            weightmatrixwithnoise = zeros((len(nodeorder), len(nodeorder)))
            weightmatrixindex = list(nodeorder)
            # calculate weight matrix
            # arrange the same columes together
            probtreeall = 0
            for datadickey in datadic.keys():
                if datadickey > 1:
                    textbylinewithrepeat = datadic[datadickey]
                    linerepeat = []
                    textbyline = []
                    for textbylinewithrepeati in textbylinewithrepeat:
                        if textbylinewithrepeati not in textbyline:
                            textbyline.append(textbylinewithrepeati)
                            linerepeat.append(1.0)
                        else:
                            lineindex = textbyline.index(textbylinewithrepeati)
                            linerepeat[lineindex] = linerepeat[lineindex]+1.0
                    weightdic, probtree = self.messagepassingu(
                        treeroot, nodeorder, nodehidden, nodeleaf, treedic, textbyline, linerepeat, namelist, probsame)
                    probtreeall = probtreeall + probtree
                    for ni in range(0, (len(nodeorder)-1)):
                        for nj in range((ni+1), len(nodeorder)):
                            weightmatrix[ni, nj] = weightmatrix[ni, nj] + \
                                weightdic[(nodeorder[ni], nodeorder[nj])]
                            weightmatrix[nj, ni] = weightmatrix[ni, nj]
            # add noise to weight matrix
            for ni in range(len(nodeorder)):
                for nj in range(len(nodeorder)):
                    if ni != nj:
                        # add noise or not
                        # |<
                        # (1)with noise
                        weightmatrixwithnoise[ni, nj] = weightmatrix[ni,
                                                                     nj] + gauss(0, sigma)
                        # (2)without noise
                        # weightmatrixwithnoise[ni,nj] = weightmatrix[ni,nj]
                        # >|
                        weightmatrixwithnoise[nj,
                                              ni] = weightmatrixwithnoise[ni, nj]
                    else:
                        weightmatrixwithnoise[ni, ni] = float('Inf')
            # update tree by mst
            treeroot, nodeorder, nodeleaf, treedic = self.mst(
                weightmatrixwithnoise, weightmatrixindex)
            # calculate qscore
            qscore = 0.0
            for nodei in nodeorder[0:(-1)]:
                qscore = qscore + weightmatrix[weightmatrixindex.index(
                    nodei), weightmatrixindex.index(treedic[nodei]['parent'][0])]
            # save results in logvector
            logvector[0].append(iteration)
            logvector[1].append(sigma)
            logvector[2].append(qscore)
            logvector[3].append(probtreeall)
            # print time
            if printtime and (iteration < 4):
                timeend = time.time()
                print('The time for iteration ' + str(iteration) +
                      ' is '+str(timeend-timestart))
            # if stopsign == 0:
                # |<
                # (1)
                # plot tree with removed hiddden nodes
                # treedicremoved,nodehiddenremoved = removehidden(nodehidden,treedic)
                # treetodot(treedicremoved,treedicremoved.keys(),nodehiddenremoved, resfoldertree, str(iteration).zfill(4))
                # (2)
                # plot tree with NO removed hiddden nodes
                # treetodot(treedic,treedic.keys(),nodehidden, resfoldertree, str(iteration).zfill(4)+'_withhidden')
                # >|
            # test converge
            if (iteration > 10) and (iteration < iterationmax):
                if stopsign == 1:
                    print('stop at ' + str(iteration-1) + '\n')
                    break
                if (abs(logvector[2][-2] - logvector[2][-3]) < 0.001) and (abs(logvector[2][-1] - logvector[2][-2]) < 0.001):
                    stopsign = 1
                    treediclastbackup = deepcopy(treedic)
            if (iteration == iterationmax) and (stopsign == 0):
                print('stop at ' + str(iteration-1) + '\n')
                treediclastbackup = deepcopy(treedicprevious)

            # find the iteration with best probtreeall
            if probtreeall > probtreeallbest:
                treedicbest = deepcopy(treedicprevious)
                nodeorderold = nodeorder
                probtreeallbest = probtreeall
                bestiteration = iteration - 1
                treedicremoved, nodehiddenremoved = self.removehidden(
                    nodehidden, treedicbest)
                # treetodot(treedicremoved,treedicremoved.keys(),nodehiddenremoved, resfoldertree, str(iteration-1).zfill(4))
        # important>
            # update sigma
            if iteration >= 2:
                # <parameter>
                sigma = sigma0 * \
                    ((1.0-float(iteration)/float(iterationmax))**2.0)
            elif iteration == 1:
                sigma0 = 0.1 * max(abs(weightmatrix.min()),
                                   abs(weightmatrix.max()))
                sigma = sigma0
        # save last and best tree
        # |<
        # (1)
        # without hidden nodes
        treediclast, nodehiddenlast = self.removehidden(
            nodehidden, treediclastbackup)
        out = self.treetodot(treediclast ,treediclast.keys(),nodehiddenlast, resfoldertree,'treelast') # !!!!!!!!! I uncomented this !!!!!!!!!!!!!!!!!! #
        #tree2newick(treediclast, treediclast.keys(),
        #            nodehiddenlast, resfoldertree, 'treelast')
        treedicbestrh, nodehiddenbest = self.removehidden(nodehidden, treedicbest)
        # treetodot(treedicbestrh ,treedicbestrh.keys(),nodehiddenbest, resfoldertree,'treebest')
        #tree2newick(treedicbestrh, treedicbestrh.keys(),
        #            nodehiddenbest, resfoldertree, 'treebest')
        #newick2img(self.newick_path, self.image_path, False, radial=False)
        # (2)
        # with hidden nodes
        # treetodot(treediclastbackup, treediclastbackup.keys(), nodehidden, resfoldertree,'treelast_withhidden')
        # treetodot(treedicbestrh, treedicbestrh.keys(), nodehidden, resfoldertree,'treebest_withhidden')
        # >|
        # save log
        logstr = logstr + 'End at ' + str(time.gmtime()) + '\n' + 'best iteration is ' + str(
            bestiteration) + '\n' + 'best probability is ' + str(probtreeallbest) + '\n\n\n'
        # print (resfolder)
        # print (logstr)
        # print ('_________________________')
        inumber = len(logvector)
        jnumber = iteration + 1
        for j in range(jnumber):
            for i in range(inumber):
                logstr = logstr + str(logvector[i][j]) + '\t'
            logstr = logstr.strip() + '\n'
        logstr = logstr.strip()
        self.log_string = logstr
        #file = open(os.path.join(resfolder, 'log'), 'w')
        #file.write(logstr)
        #file.close()
        return (qscore, bestiteration, out)

    # qscore, bestiteration = semuniform("test_stemma", 1)
    # print(f"best iteration was: {bestiteration}")
