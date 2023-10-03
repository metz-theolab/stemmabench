"""CLI commands for easy manipulation of library.
"""
import os
from pathlib import Path

import typer
import collatex
from stemmabench.stemma_generator import Stemma
from stemmabench.utils import (
    load_tradition,
    format_tradition,
    save_matrix_to_csv,
    save_analysis_summary_to_csv
)
from stemmabench.variant_analyzer import VariantAnalyzer


app = typer.Typer()


@app.command()
def generate_tradition(input_text: str,
                       output_folder: str,
                       configuration: str):
    """Generate a tradition of manuscripts.

    Args:
        input_text (str): The text to give as input for the tradition.
        output_folder (str): The output folder for the tradition.
        configuration (str): The configuration of the tradition.
    """
    stemma = Stemma(path_to_text=input_text,
                    config_path=configuration)
    stemma.generate()
    stemma.dump(folder=output_folder)

@app.command()
def analyze_tradition(input_folder: str,
                      output_folder: str,
                      sep: str=".",
                      # Initialize VariantAnalyzer
                      language: str = "en",
                      # Analysis summary
                      include = "all", # List[str] | str
                      decimals: int = 4,
                      normalize: bool = True,
                      ## omit
                      missing: str = "-",
                      ## mispell
                      distance: str = "DamerauLevenshtein",
                      mispell_cutoff: float = 0.4,
                      ## fragment
                      frag_strategy: str = "max",
                      ## complementary results
                      details: bool = False
                      ):
    """
    Analyze variant locations in a tradition.
    Estimate the occurence rates of different variant locations types in a  
    tradition.

    Args:
        input_folder (str): The text to give as input for the tradition.
        output_folder (str): The output folder for the results.
        sep (str, optional): The sentences delimiter in the text.
        language (str, optional): The language of the tradition. 
            Defaults to "en".
        disable_synonym (bool, optional): Do not return synonym rate. 
            Defaults to False.
        include (List[str]|str, optional): A list of variant type to consider in 
            the analysis. Defaults to "all". 
            Options: ["omit", "mispell", "synonym", "fragment", "undetermined"]
        decimals (int, optional): The number of decimal places to round the rate. 
            Defaults to 4.
        normalize (bool, optional): Return rates if True, or counts if False. 
            Defaults to True.
        missing (str, optional): The character representing missing readings. 
            Defaults to "-".
        distance (str, optional): The distance metric to use for mispelling
            detecttion. Defaults to "DamerauLevenshtein".
        mispell_cutoff (float, optional): The cutoff score for mispelling. 
            Maximum normalize (0,1) distance allowed for mispell. 
            Defaults to 0.4.
        frag_strategy (str, optional): The strategy for estimating the 
            fragment rate. Defaults to "max". Options: "max", "mean".
        details (bool, optional): Return supplementary details on the variant 
            analysis (dissimilarity matrices). Defaults to  False.

    Returns:
        Dict[str, float]: _description_
    """

    # Load tradition from the input file.
    ## tradition: Dict[str, str] LIKE {"witness_name": "witness_content"}
    ##      = {"text_file_name": capitalize_sentences("text_file_content")}
    tradition = load_tradition(input_folder=input_folder, sep=sep)

    # Format tradition as input for collatex collation and alignment table.
    tradition_formatted = format_tradition(tradition=tradition)

    # Create alignment table
    collation = collatex.Collation().create_from_dict(tradition_formatted)
    alignment_table = collatex.collate(
        collation, segmentation=False, near_match=True, layout="vertical"
    )

    # Perform analysis.
    variant_analyzer = VariantAnalyzer(
        alignment_table, language=language)
    # ---- Analysis summary.
    analysis_summary = variant_analyzer.analysis_summary(
        include=include,
        decimals=decimals,
        normalize=normalize,
        missing=missing,
        distance=distance,
        mispell_cutoff=mispell_cutoff,
        frag_strategy=frag_strategy
    )
    # Create output_folder if it does not exist.
    Path(output_folder).mkdir(exist_ok=True)
    # Save analysis summary to a CSV file.
    analysis_summary_path = os.path.join(output_folder, "analysis_summary.csv")
    save_analysis_summary_to_csv(analysis_summary, analysis_summary_path)

    # Details.
    if details:
        operations = include
        if operations == "all":
            operations = ["omit", "mispell", "synonym", "undetermined"]
        if "fragment" in operations:
            operations.remove("fragment")
        mapper = {"omit": "O", "mispell": "M", "synonym": "S", "undetermined": "U"}
        variant_types = [mapper.get(word, "U") for word in operations]

        # ---- Dissimilarity matrices
        dissimilarity_matrices = {
            variant_type: variant_analyzer.dissimilarity_matrix(
                variant_type=variant_type,
                normalize=normalize,
                missing=missing,
                distance=distance,
                mispell_cutoff=mispell_cutoff
            ) for variant_type in variant_types}
        reverse_mapper = {v: k for k, v in mapper.items()}
        # change keys name ("O" -> "omit")
        dissimilarity_matrices = {reverse_mapper.get(k, k): v
                                  for k, v in dissimilarity_matrices.items()}
        # Save dissimilarity matrices to CSV files
        for variant_type_name, dissimilarity_matrix in dissimilarity_matrices.items():
            dissimilarity_matrix_path = os.path.join(
                output_folder, f"{variant_type_name}_dissimilarity_matrix.csv"
            )
            save_matrix_to_csv(dissimilarity_matrix, dissimilarity_matrix_path)

    print(f"Analysis completed. Results saved to: {output_folder}")
    print(f"Summary: {analysis_summary}")


if __name__ == "__main__":
    app()
