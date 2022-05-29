import random
import re
import string


class Sentence:
    """Class for a sentence representation and variation.
    """

    def __init__(self, sentence: str) -> None:
        """Class allowing for the manipulation of sentences.

        Args:
            sentence (str): The sentence to wrap in the class.
        """
        self.sentence = sentence
        self.words = self.clean(sentence).split(" ")
        self.nbr_words = len(self.words)

    @staticmethod
    def clean(sentence: str) -> str:
        """Clean up the sentence by removing punctuations and lowering the letters.

        Args:
            str: The sentence to clean.

        Returns:
            str: The cleaned out sentence.
        """
        return re.sub('[%s]' % re.escape(string.punctuation),
                      '',
                      sentence).lower()

    def duplicate(self, nbr_words: int = 2) -> str:
        """Duplicate a subset of nbr_words words in the sentence,
        and returns the duplicate.

        Args:
            nbr_words (int, optional): The length of the group of words
            to switch in the sentence. Defaults to 2.

        Returns:
            str: The newly generated sentence.
        """
        if self.nbr_words > nbr_words + 1:
            random_location = random.randrange(self.nbr_words - nbr_words)
            generated_sentence = " ".\
                join(
                    self.words[:random_location]
                    + self.words[random_location:random_location
                                 + nbr_words]
                    * 2
                    + self.words[random_location + nbr_words:]
                )
            return f"{generated_sentence.strip().capitalize()}."
        else:
            return self.sentence
