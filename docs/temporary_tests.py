import sys
# import random
import pickle
from loguru import logger
# from stemmabench.textual_units.text import Text
# from stemmabench.stemma_generator import Stemma
# from stemmabench.config_parser import StemmaBenchConfig
from stemmabench.variant_analyzer import VariantAnalyzer

# Set logging level to info
logger.remove()
logger.add(sys.stderr, level="INFO")

# config = StemmaBenchConfig(**{
#     "meta": {
#       "language": "en"  
#     },

#     "stemma": {
#         "depth": 2,
#         "width": {
#             "law": "Uniform",
#             "min": 2,
#             "max": 4
#         },
#         "fragmentation_proba": 1
#     },

#     "variants": {
#         "sentences": {
#             "duplicate": {
#                 "args": {
#                     "nbr_words": 2
#                 },
#                 "law": "Bernouilli",
#                 "rate": 0.1
#             }
#         },
#         "words": {
#             "synonym": {
#                 "law": "Bernouilli",
#                 "rate": 0.1,
#                 "args": {}
#             },
#             "mispell": {
#                 "law": "Bernouilli",
#                 "rate": 0.05,
#                 "args": {}
#             },
#             "omit": {
#                 "law": "Bernouilli",
#                 "rate": 0.05,
#                 "args": {}
#             }
#         },
#         "texts": {
#             "fragmentation": {
#                 "max_rate": 1,
#                 "distribution": {
#                     "law": "Poisson",
#                     "rate": 0.9
#                 }
#             }
#         }
#     }
# })


# def repeat_character(n_rep:int=10, char:str="word", sep:str=" "):
#     """
#     Generate a fake text.
#     """
#     return sep.join([f"{char}{i}"  for i in range(1, n_rep + 1)])

# DEMO_TEXT = repeat_character(25)
# DEMO_TEXT2 = "love bade  welcome yet my soul hrew back guilty of dust ajd sin."

# # Instantiate a Stemma object.
# stemma = Stemma(original_text=DEMO_TEXT2, config=config, random_state=123)

# # Generate a tradition.
# # random.seed(10)
# # print(stemma._apply_level(DEMO_TEXT2))
# # print(stemma.generate())
# # print(stemma.texts_lookup)
# random.seed(10)
# print(
#     [Text(DEMO_TEXT2).transform(stemma.config.variants)
#     for _ in range(stemma.width)]
# # )
# manu1 = 'Love bade welcome  my soul hrew back huilty of dust ajd sin.'
# manu2 = 'Lie with bade welcome yet my soul hrew back guilty  dust ajd sin.'
# manu3 = 'Love bade welcome yet my ooul hrew back guilty of dust ajd sin.'
# results = [manu1, manu2, manu3]
# manu1f = stemma._apply_fragmentation(manu1)
# manu2f = stemma._apply_fragmentation(manu2)
# manu3f = stemma._apply_fragmentation(manu3)
# print([manu1f, manu2f, manu3f])
# res = ['huilty of dust ajd sin.', 
#        'guilty  dust ajd sin.', 
#        'guilty of dust ajd sin.']

# print(stemma._apply_level(stemma.original_text))


#------------ VARIANT ANALYZER -----------------
filepath = r"d:\Yedidia\Programming\src-variant-analysis\tests\test_data\test_alignment_table.pickle"
with open(filepath, "rb") as file:
    table = pickle.load(file)
# print(table)

variant_analyzer = VariantAnalyzer(table)

# ----- PROPERTIES
print(variant_analyzer.table)
# print(variant_analyzer.array)
# print(variant_analyzer.language)
# print(variant_analyzer.witness_names)
# print(variant_analyzer.variant_locations)

# ----- VARIANT LOCATIONS
# print(variant_analyzer.variant_locations_pairwise_matrix())
w1, w2, w3 = variant_analyzer.array
# print(variant_analyzer.is_omit(w1[1], w1[1]), # "-" and "-" => False
#       variant_analyzer.is_omit(w1[1], w2[1]), # "-" and "quick" => True
#       variant_analyzer.is_omit(w3[1], w2[1])) # "fast" and "quick" => False

# print(variant_analyzer.is_mispell(w1[2], w2[2]), # "brown" and "brewn" => True
#       variant_analyzer.is_mispell(w1[2], w3[2]), # "brown" and "brown" => False
#       variant_analyzer.is_mispell(w1[0], w3[0])) # "The" and "A" => False 

# print(variant_analyzer.is_synonym(w1[0], w3[0]), # "The" and "A" => False
#       variant_analyzer.is_synonym(w2[1], w3[1])) # "quick" and "fast" => True 

# print([variant_analyzer.which_variant_type(s1, s2) for s1, s2 in zip(w2, w3)])
# print(variant_analyzer.which_variant_type_vectorize(w1, w2),
#       variant_analyzer.which_variant_type_vectorize(w2, w3))
# print(variant_analyzer.variant_type_matrix())

# print(variant_analyzer.dissimilarity_matrix(), "\n\n",
#       variant_analyzer.dissimilarity_matrix(normalize=True), "\n\n",
#       variant_analyzer.dissimilarity_matrix(variant_type="O"), "\n\n",
#       variant_analyzer.dissimilarity_matrix(variant_type="M"), "\n\n",
#       variant_analyzer.dissimilarity_matrix(variant_type="S"), "\n\n",
#       variant_analyzer.dissimilarity_matrix(variant_type="U"))

# print(variant_analyzer.operation_rate(), variant_analyzer.operation_rate(normalize=False), "\n\n",
#       variant_analyzer.operation_rate(variant_type="O"), variant_analyzer.omit_rate(), "\n\n",
#       variant_analyzer.operation_rate("S"), variant_analyzer.synonym_rate(), "\n\n",
#       variant_analyzer.operation_rate("M"), variant_analyzer.mispell_rate(), "\n\n",
#       variant_analyzer.operation_rate("U"), variant_analyzer.undetermined_operation_rate(),
#       )

# print(variant_analyzer.fragment_locations(w1))
# print(variant_analyzer.fragment_locations_matrix())
# print(variant_analyzer.fragment_locations_count(),
#       variant_analyzer.fragment_locations_count(normalize=True))
# print(variant_analyzer.fragment_rate(), 
#       variant_analyzer.fragment_rate(strategy="mean"), 
#       variant_analyzer.fragment_rate(normalize=False), )