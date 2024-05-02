from pathlib import Path

class Utils:

    @staticmethod
    def load_text(path_to_text: str) -> str:
        """Load a text given a path to this text.

        Args:
            path_to_text (str): The path to the text to be loaded.

        Returns:
            str: The loaded text.
        """
        with open(Path(path_to_text), encoding="utf-8") as file:
            return file.read()

    pass