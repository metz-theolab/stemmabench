"""Utility Functions
"""
import os
import csv
from typing import Dict, List
from pathlib import Path

import numpy as np
from stemmabench.config_parser import StemmaBenchConfig


def make_stemmabench_config(
    depth: int=1,
    width_min: int=2,
    width_max: int=2,
    frag_proba: float=0,
    frag_max_rate: float=0,
    frag_dist_law: str="Discrete Uniform",
    frag_dist_rate: str=0.5,
    missing_manuscripts_rate: float = 0,
    duplicate_nbr_words: int=1,
    duplicate_rate: float=0.01,
    synonym_rate: float=0.05,
    mispell_rate: float=0.05,
    omit_rate: float=0.01,
    language: str="en"
):
    """Shortcurt function to build a configuration file for stemma generation.
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
            "missing_manuscripts": {
                "law": "Bernouilli",
                "rate": missing_manuscripts_rate
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
                        "n": 1000 # just for consistency (not used)
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


def load_tradition(input_folder: str, sep: str = ".") -> Dict[str, str]:
    """
    Load tradition from input folder and format it.

    Args:
        input_folder (str): The input folder containing witness text files.
        sep (str, optional): Sentence separator. Defaults to ".".

    Returns:
        Dict[str, str]: A dictionary with witness names as keys and 
            formatted witness content as values.
    """
    tradition = {}
    # List directory files/
    for filename in os.listdir(input_folder):
        # Select .txt files.
        if filename.endswith(".txt"):
            # Get file name (remove .txt extension).
            witness_name = os.path.splitext(filename)[0]
            # Add file content to the dictionary.
            with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as file:
                witness_content = file.read()
                formatted_content = capitalize_sentences(witness_content, sep=sep)
                tradition[witness_name] = formatted_content
    return tradition


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


def save_analysis_summary_to_csv(analysis_summary: Dict[str, float],
                                 output_path: str):
    """Save an analysis summary result to a csv file.
    The input is a dictionary that look like the ouput of the method 
    `VariantAnalyzer.analysis_summary()`.

    Args:
        analysis_summary (Dict[str, float]): The dictionary to save.
        output_path (str): The filepath where to save the dictionary.
    """
    if not output_path.endswith(".csv"):
        output_path = Path(output_path + ".csv")
    output_path = Path(output_path)
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Variant Type", "Rate"])
        for variant_type, rate in analysis_summary.items():
            writer.writerow([variant_type, rate])


def save_matrix_to_csv(matrix: np.ndarray,
                       output_path: str):
    """Save a matrix to csv.

    Args:
        matrix (np.ndarray): _description_
        output_path (str): _description_

    Raises:
        AttributeError: _description_
    """
    if not output_path.endswith(".csv"):
        output_path = Path(output_path + ".csv")
    output_path = Path(output_path)
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for row in matrix:
            writer.writerow(row)
