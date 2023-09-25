"""Utility Functions
"""
from typing import Dict, List
from stemmabench.config_parser import StemmaBenchConfig


# Define the configuration of the stemma.
def make_stemmabench_config(
    depth: int=1,
    width_min: int=2,
    width_max: int=2,
    frag_proba: float=0,
    frag_max_rate: float=0,
    frag_dist_law: str="Discrete Uniform",
    frag_dist_rate: str=0.5,
    duplicate_nbr_words: int=1,
    duplicate_rate: float=0.01,
    synonym_rate: float=0.05,
    mispell_rate: float=0.05,
    omit_rate: float=0.01,
    language: str="en"
):
    """Shortcut function to specify a configuration for generating a stemma. 
    """
    config = StemmaBenchConfig(**{
        "meta": {
          "language": language
        },
        "stemma": {
            "depth": depth,
            "width": {
                "law": "Uniform",
                "min": width_min,
                "max": width_max
            },
            "fragmentation_proba": frag_proba
        },
        "variants": {
            "sentences": {
                "duplicate": {
                    "args": {
                        "nbr_words": duplicate_nbr_words
                    },
                    "law": "Bernouilli",
                    "rate": duplicate_rate
                }
            },
            "words": {
                "synonym": {
                    "law": "Bernouilli",
                    "rate": synonym_rate,
                    "args": {}
                },
                "mispell": {
                    "law": "Bernouilli",
                    "rate": mispell_rate,
                    "args": {}
                },
                "omit": {
                    "law": "Bernouilli",
                    "rate": omit_rate,
                    "args": {}
                }
            },
            "texts": {
                "fragmentation": {
                    "max_rate": frag_max_rate,
                    "distribution": {
                        "law": frag_dist_law,
                        "rate": frag_dist_rate,
                        "n": 1000 # just for conformity (not used)
                    }
                }
            }
        }
    })
    return config


def capitalize_sentences(text: str, sep=".") -> str:
    """Capitalize each sentence in a text. A sentence is a group of words 
    delimited by a comma.

    Args:
        text (str): The text given as input
        sep (str, optional): Sentence separator. Defaults to ".".

    Returns:
        str: The input text where sentences has been capitalized. 
    """
    return (f"{sep} ".join([
        sentence.strip().capitalize() for sentence in text.split(sep)
    ])).strip()


def format_tradition(tradition: Dict[str, str]) -> Dict[str, List[Dict[str, str]]]:
    """Format tradition to meet the input requirements for collatex collation.

    Args:
        tradition (Dict[str, str]): A dictionary formatted tradition with 
            witness names as keys and witness content texts as values. 

    Returns:
        JSON(Dict[str, List[Dict[str, str]]]): A json formatted tradition that 
            can be passed to collatex.
    """
    return {"witnesses": [{"id": witness_id, "content": content}
                            for witness_id, content in tradition.items()]
            }
