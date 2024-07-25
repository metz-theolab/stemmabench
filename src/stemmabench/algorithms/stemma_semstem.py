from typing import Callable, Dict, Union, Tuple, List, Any
from numpy import array, log, ones, identity, zeros, dot, abs
from copy import deepcopy
from math import inf
from random import gauss
import os
import time
# from networkx import minimum_spanning_tree, Graph
# from pgmpy.estimators import TreeSearch #Chow-Liu algorithm [4]
from stemmabench.algorithms.stemma_algorithm import StemmaAlgo
from stemmabench.algorithms.stemma_NJ import StemmaNJ
from stemmabench.algorithms.stemma import Stemma
from stemmabench.algorithms.manuscript_in_tree_base import ManuscriptInTreeBase
from stemmabench.algorithms.manuscript_in_tree import ManuscriptInTree
from stemmabench.algorithms.utils import Utils
# from stemmabench.algorithms.manuscript_in_tree_empty import ManuscriptInTreeEmpty


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

    def compute(self, folder_path: str) -> ManuscriptInTreeBase:
        """Builds the stemma tree. If the distance is specified in function call it will surplant the existing distance if it exists.

        ### Args:
            - folder_path (str): The path to the folder containing the texts. The path specified here will surplant the previous path defined in constructor.
            !!! All .txt files in this folder must be files containing Manuscript texts unless the file name contains the substring "edge" !!!

        Returns:
            - Manuscript: The root of the stemma with the rest of its tree as its children.
        """
        super().compute(folder_path)
        if self._distance:
           nj_stemma = Stemma(folder_path=folder_path)
           nj_stemma.compute(algo=StemmaNJ(
               distance=self._distance, rooting_method="none"))
           self._nj_edge_list = nj_stemma.to_edge_list()
        edges = self.semuniform(
            folder_path, self._iterationmax, folder_path)[2]
        print(edges)
        return ManuscriptInTree(parent=None, recursive=Utils.dict_from_edge(
            edge_list=edges), text_list=list(self.manuscripts.keys()))

    def readfiles(self, input_folder: str) -> Tuple[Dict[str, int], Dict[Any, Any], Dict[str, str]]:
        """"""
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

        def countdiff(text1, text2):
            return self._distance(text1, text2)

        def ajustmatrix(distmatrix):
            distmatrix1 = deepcopy(distmatrix)
            namelist = list(distmatrix1.keys())
            netdivergence = {}
            namenumber = len(namelist)
            for namei in namelist:
                disti = list(distmatrix1[namei].values())
                netdivergence[namei] = sum(disti)

            for namei in range(namenumber):
                for namej in range(namei+1, namenumber):
                    distmatrix1[namelist[namei]][namelist[namej]] = distmatrix1[namelist[namei]][namelist[namej]]-(
                        (netdivergence[namelist[namei]]+netdivergence[namelist[namei]])/(namenumber-2))
                    distmatrix1[namelist[namej]][namelist[namei]
                                                 ] = distmatrix1[namelist[namei]][namelist[namej]]
            return (distmatrix1)

        def updatematrix(distmatrix, edgelengthdic, linkednodes, newnode):
            namelist = list(distmatrix.keys())
            distmatrix[newnode] = {}
            edgelengthdic[(linkednodes[0], newnode)] = (distmatrix[linkednodes[0]][linkednodes[1]]/2)+(
                (sum(distmatrix[linkednodes[0]].values())-sum(distmatrix[linkednodes[1]].values()))/(2*(len(namelist)-2)))
            edgelengthdic[(newnode, linkednodes[0])
                          ] = edgelengthdic[(linkednodes[0], newnode)]
            edgelengthdic[(linkednodes[1], newnode)] = distmatrix[linkednodes[0]
                                                                  ][linkednodes[1]]-edgelengthdic[(linkednodes[0], newnode)]
            edgelengthdic[(newnode, linkednodes[1])
                          ] = edgelengthdic[(linkednodes[1], newnode)]

            distmatrix[newnode] = {}
            for nodei in namelist:
                if nodei not in linkednodes:
                    distmatrix[nodei][newnode] = (
                        distmatrix[nodei][linkednodes[0]]+distmatrix[nodei][linkednodes[1]]-distmatrix[linkednodes[0]][linkednodes[1]])/2
                    distmatrix[newnode][nodei] = distmatrix[nodei][newnode]
                    del distmatrix[nodei][linkednodes[0]]
                    del distmatrix[nodei][linkednodes[1]]

            for nodei in linkednodes:
                del distmatrix[nodei]

        def findnearestnode(distmatrix):
            namelist = list(distmatrix.keys())
            mindist = float('Inf')
            for namei in namelist:
                for namej in namelist:
                    if namei != namej:
                        if mindist > distmatrix[namei][namej]:
                            mindist = distmatrix[namei][namej]
                            nearestnode = [namei, namej]
            return (nearestnode, mindist)

        distmatrix = {}
        namelist = list(textdata.keys())

        for namei in namelist:
            distmatrix[namei] = {}
        for namei in range(len(namelist)):
            for namej in range((namei+1), len(namelist)):
                distmatrix[namelist[namei]][namelist[namej]] = countdiff(
                    textdata[namelist[namei]], textdata[namelist[namej]])
                distmatrix[namelist[namej]][namelist[namei]
                                            ] = distmatrix[namelist[namei]][namelist[namej]]

        hiddennodecount = 1
        treedic = {}
        edgelengthdic = {}
        nodeorder = []
        nodehidden = []
        nodeleaf = list(distmatrix.keys())

        while len(distmatrix.keys()) > 2:
            distmatrixnormalized = ajustmatrix(distmatrix)
            nearestnode, mindist = findnearestnode(distmatrixnormalized)
            if nearestnode[0] not in treedic:
                self.createnode(treedic, nearestnode[0])
                nodeorder.append(nearestnode[0])
            if nearestnode[1] not in treedic:
                self.createnode(treedic, nearestnode[1])
                nodeorder.append(nearestnode[1])
            if str(hiddennodecount) not in treedic:
                self.createnode(treedic, str(hiddennodecount))
                nodeorder.append(str(hiddennodecount))
                nodehidden.append(str(hiddennodecount))

            self.addedge(treedic, str(hiddennodecount), nearestnode[0])
            self.addedge(treedic, str(hiddennodecount), nearestnode[1])
            updatematrix(distmatrix, edgelengthdic,
                         nearestnode, str(hiddennodecount))
            hiddennodecount = hiddennodecount+1
        noderemain = list(distmatrix.keys())
        if str(hiddennodecount) not in treedic:
            self.createnode(treedic, str(hiddennodecount))
            nodehidden.append(str(hiddennodecount))

        print(f"noderemain: {noderemain}")
        
        if noderemain[0] not in treedic:
            self.createnode(treedic, noderemain[0])
            nodeorder.append(noderemain[0])
        if noderemain[1] not in treedic:
            self.createnode(treedic, noderemain[1])
            nodeorder.append(noderemain[1])
        self.addedge(treedic, str(hiddennodecount), noderemain[0])
        self.addedge(treedic, str(hiddennodecount), noderemain[1])
        #edgelengthdic[(noderemain[0], str(hiddennodecount))
        #              ] = distmatrix[noderemain[0]][noderemain[1]]/2
        #edgelengthdic[(str(hiddennodecount), noderemain[0])
        #              ] = edgelengthdic[(noderemain[0], str(hiddennodecount))]
        #edgelengthdic[(noderemain[1], str(hiddennodecount))
        #              ] = edgelengthdic[(noderemain[0], str(hiddennodecount))]
        #edgelengthdic[(str(hiddennodecount), noderemain[1])
        #              ] = edgelengthdic[(noderemain[0], str(hiddennodecount))]
        treeroot = str(hiddennodecount)
        nodeorder.append(treeroot)
    # treeroot: Number of the hiden root
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
        import math

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
        # step 1 read file
        # namelist, datadic, textdata = readfile(inputfile)
        namelist, datadic, textdata = self.readfiles(input_folder)
        # step 2 initiation by nj tree
        treeroot, nodeorder, nodehidden, nodeleaf, treedic = self.njtree(textdata)
        treeroot, nodeorder, nodehidden, nodeleaf, treedic = self.nohiddeninitial(
            textdata)
        # step 3 calculate weight matrix
        logstr = 'Start at' + str(time.gmtime()) + '\n'
        sigma = 0
        qscoreold = float("-inf")  # Inf)
        bestiteration = -1
        # treedicold = treedic
        # nodeorderold = nodeorder
        logvector = [['iteration'], ['sigma'], ['qscore']]
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
        # resfolder = "test_output_folder"
        resfoldertree = os.path.join(folder_path, 'tree')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
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
                        weightmatrixwithnoise[ni, nj] = weightmatrix[ni,
                                                                     # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
                                                                     nj] + gauss(0, sigma)
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

    # qscore, bestiteration = semuniform("test_stemma", 1)
    # print(f"best iteration was: {bestiteration}")
