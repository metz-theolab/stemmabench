import sys
import os
from textdistance import levenshtein, jaccard
from typing import List, Callable
from stemmabench.algorithms.stemma_dummy import StemmaDummy
from stemmabench.algorithms.stemma_NJ import StemmaNJ
from stemmabench.algorithms.stemma import Stemma
from fast_edit_distance import edit_distance
from stemmabench.algorithms.stemma import Stemma
from stemmabench.algorithms.stemma_RHM import StemmaRHM
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def inverse_jaccard(str1: str, str2: str):
    return 1 - jaccard(str1, str2)
NJ_distances: List[Callable] = [edit_distance, inverse_jaccard]
NJ_dist_names: List[str] = ["Fast_Levenshtein", "inverse_jaccard"]
Dummy_children: List[int] = [2,4,6,8,10]
tradition_dir_list = [sys.argv[1]]
# For each tradition
for trad in tradition_dir_list:
    print(f"Tradition: {trad}")
    # Dummy loop
    for dummy_param in Dummy_children:
        stemma = Stemma(trad)
        print(f"Dummy_param: {dummy_param}")
        stemma.compute(algo=StemmaDummy(),width=dummy_param)
        output_edge_name = f"edges_Dummy_NbChild_{dummy_param}.txt"
        stemma.dump(trad,output_edge_name,dump_texts=False)
    # NJ loop
    for i in range(len(NJ_distances)):
        stemma = Stemma(trad)
        print(f"NJ_param: {NJ_dist_names[i]}")
        stemma.compute(algo=StemmaNJ(distance=NJ_distances[i]))
        output_edge_name = f"edges_NJ_Dist_{NJ_dist_names[i]}.txt"
        stemma.dump(trad,output_edge_name, dump_texts=False)
    #RHM
    RHM = StemmaRHM(100000,1,10,False)
    RHM.compute(trad)
logger.info("Algo done.")