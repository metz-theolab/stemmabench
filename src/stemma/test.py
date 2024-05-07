import pickle
import json
from stemma.stemma import Stemma
from ..utils import dict_from_edge


#dic = dict_from_edge("../tests/test_data/test_egde.txt")

out = Stemma()

out.compute(edge_file="../tests/test_data/new_egde.txt")

print(json.dump(out))
