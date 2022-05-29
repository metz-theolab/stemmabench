"""CLI commands for easy manipulation of library.
"""
import typer

from stemmabench.stemma_generator import Stemma


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


if __name__ == "__main__":
    app()
