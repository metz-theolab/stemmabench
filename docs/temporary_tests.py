import sys
from stemmabench.stemma_generator import Stemma
from stemmabench.config_parser import StemmaBenchConfig
from loguru import logger
# Set logging level to info
logger.remove()
logger.add(sys.stderr, level="INFO")

config = StemmaBenchConfig(**{
    "meta": {
      "language": "eng"  
    },

    "stemma": {
        "depth": 3,
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
                    "nbr_words": 1
                },
                "law": "Bernouilli",
                "rate": 0.5
            }
        },
        "words": {
            "synonym": {
                "law": "Bernouilli",
                "rate": 0.05,
                "args": {}
            },
            "mispell": {
                "law": "Bernouilli",
                "rate": 0.001,
                "args": {}
            },
            "omit": {
                "law": "Bernouilli",
                "rate": 0.001,
                "args": {}
            }
        },
        "text": {
            "fragmentation": {
                "max_rate": 1,
                "distribution": {
                    "law": "Bernouilli",
                    "rate": 0.5
                }
            }
        }
    }
})

def repeat_character(n:int=10, char:str="word", sep:str=" "):
    """
    Generate a fake text.
    """
    return sep.join([f"{char}{i}"  for i in range(1, n + 1)])

DEMO_TEXT = repeat_character(25)

# Instantiate a Stemma object.
stemma = Stemma(original_text=DEMO_TEXT, config=config)

# Generate a tradition.
print(stemma.generate())