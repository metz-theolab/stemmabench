import random


class Sentence:
    """Class for a sentence representation and variation.

    Returns:
        _type_: _description_
    """

    def __init__(self, sentence: str) -> None:
        """Class allowing for the manipulation of sentences.

        Args:
            sentence (str): _description_
        """
        self.sentence = sentence
        self.words = sentence.split(" ")
        self.nbr_words = len(self.words)

    def duplicate(self, nbr_words: int = 2) -> str:
        """Duplicate a subset of nbr_words words in the sentence.
        """
        if self.nbr_words > nbr_words + 1:
            random_location = random.randrange(self.nbr_words - nbr_words)
            return " ".join(self.words[:random_location]
                            + self.words[random_location:nbr_words] * 2
                            + self.words[random_location + nbr_words:])
        else:
            return self.sentence
