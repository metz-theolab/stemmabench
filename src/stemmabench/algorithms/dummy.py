
import os
from stemmabench.algorithms.stemma_algorithm import Stemma_algo


class Dummy(Stemma_algo):
    
    def compute(input_path, output_path):

        files = list(filter(lambda x: "0" in x, os.listdir(input_path)))



        

        return