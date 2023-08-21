import sys
import random
from loguru import logger
from stemmabench.textual_units.text import Text
from stemmabench.stemma_generator import Stemma
from stemmabench.config_parser import StemmaBenchConfig

# Set logging level to info
logger.remove()
logger.add(sys.stderr, level="INFO")

config = StemmaBenchConfig(**{
    "meta": {
      "language": "en"  
    },

    "stemma": {
        "depth": 2,
        "width": {
            "law": "Uniform",
            "min": 2,
            "max": 4
        },
        "fragmentation_proba": 1
    },

    "variants": {
        "sentences": {
            "duplicate": {
                "args": {
                    "nbr_words": 2
                },
                "law": "Bernouilli",
                "rate": 0.1
            }
        },
        "words": {
            "synonym": {
                "law": "Bernouilli",
                "rate": 0.1,
                "args": {}
            },
            "mispell": {
                "law": "Bernouilli",
                "rate": 0.05,
                "args": {}
            },
            "omit": {
                "law": "Bernouilli",
                "rate": 0.05,
                "args": {}
            }
        },
        "texts": {
            "fragmentation": {
                "max_rate": 1,
                "distribution": {
                    "law": "Poisson",
                    "rate": 0.9
                }
            }
        }
    }
})


def repeat_character(n_rep:int=10, char:str="word", sep:str=" "):
    """
    Generate a fake text.
    """
    return sep.join([f"{char}{i}"  for i in range(1, n_rep + 1)])

DEMO_TEXT = repeat_character(25)
DEMO_TEXT2 = "love bade  welcome yet my soul hrew back guilty of dust ajd sin."

# Instantiate a Stemma object.
stemma = Stemma(original_text=DEMO_TEXT2, config=config, random_state=123)

# Generate a tradition.
# random.seed(10)
# print(stemma._apply_level(DEMO_TEXT2))
# print(stemma.generate())
# print(stemma.texts_lookup)
random.seed(10)
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

print(stemma._apply_level(stemma.original_text))
