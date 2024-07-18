import sys
import os
from textdistance import levenshtein, jaccard
from typing import List, Callable
from stemmabench.algorithms.stemma_dummy import StemmaDummy
from stemmabench.algorithms.stemma_NJ import StemmaNJ
from stemmabench.algorithms.stemma import Stemma


def inverse_jaccard(str1: str, str2: str):
    return 1 - jaccard(str1, str2)
NJ_distances: List[Callable] = [levenshtein, inverse_jaccard]
NJ_dist_names: List[str] = ["levenshtein", "inverse_jaccard"]
Dummy_children: List[int] = [2,4,6,8,10]
# Check that the right number of arguments have been passed
if len(sys.argv) < 2:
    raise RuntimeError("The folder path argument is missing.")
tradition_dir_list = [f"{sys.argv[1]}/{f}" for f in os.listdir(sys.argv[1]) if os.path.isdir(f"{sys.argv[1]}/{f}")]
# For each tradition
for trad in tradition_dir_list:
    print(f"Tradition: {trad}")
    # Dummy loop
    for dummy_param in Dummy_children:
        stemma = Stemma(trad)
        print(f"Dummy_param: {dummy_param}")
        stemma.compute(algo=StemmaDummy(),width=dummy_param)
        output_edge_name = f"edges_Dummy_NbChild_{dummy_param}.txt"
        stemma.dump(trad,output_edge_name, dump_texts=False)
    # NJ loop
    for i in range(len(NJ_distances)):
        stemma = Stemma(trad)
        print(f"NJ_param: {NJ_dist_names[i]}")
        stemma.compute(algo=StemmaNJ(distance=NJ_distances[i]))
        output_edge_name = f"edges_NJ_Dist_{NJ_dist_names[i]}.txt"
        stemma.dump(trad,output_edge_name, dump_texts=False)