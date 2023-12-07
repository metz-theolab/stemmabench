"""This module define the `Word` class whose methods apply transformations at 
the word level.
"""
import re
import string

import numpy as np
from loguru import logger
from stemmabench.data import SUPPORTED_LANGUAGES, SYNONYM_DICT, LETTERS


class Word:
    """The Word class defines several methods for variants at
    the word level.
    """

    def __init__(self,
                 word: str,
                 language: str = "en") -> None:
        """Initialize a class of type Word.

        Args:
            word (str): The word to wrap the class around.
            language (str, optional): The language to perform the variant in.
                Defaults to "en".
        """
        self.word = self.clean(word)
        if language not in SUPPORTED_LANGUAGES:
            logger.critical(f"Unknown language {language}.")
            raise ValueError(f"Unknown language {language}.")
        self.language = language
        self.synonyms = SYNONYM_DICT[language]

    @staticmethod
    def clean(word: str) -> str:
        """Clean up the word by removing punctuations and lowering the letters.

        Args:
            str: The word to clean.

        Returns:
            str: The cleaned out word.
        """
        return re.sub('[%s]' % re.escape(string.punctuation), '', word).lower()

    def synonym(self) -> str:
        """Return a synonym of the word, by picking randomly in the available dictionary.

        Returns:
            str: The selected synonym.
        """
        try:
            synonyms = self.synonyms[self.word]
            if len(synonyms):
                return synonyms[np.random.randint(0, len(synonyms))]
            logger.debug(f"Could not find synonym for word {self.word}")
        except KeyError:
            logger.debug(f"Could not find synonym for word {self.word}")
        return self.word

    def mispell(self) -> str:
        """Mispell the word by replacing a letter with another one.

        Returns:
            str: The mispelled word.
        """
        if self.word:
            random_location = np.random.randint(0, len(self.word))
            return self.word[:random_location] + \
                np.random.choice(list(LETTERS[self.language])) + \
                self.word[random_location + 1:]
        return self.word

    def omit(self) -> str:
        """Omit a word (ie: return an empty string).

        Returns:
            str: An empty string.
        """
        return ""
