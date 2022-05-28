import random
import re
import string
from typing import List, Union
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError, Synset
from loguru import logger

POS = {
    "NOUN": wn.NOUN,
    "VERB": wn.VERB,
    "ADJ": wn.ADJ,
    "NA": None
}


class Word:
    """Class for single word variants and manipulation.
    """

    def __init__(self, word: str, language: str = "eng", pos: str = "NOUN") -> None:
        """Initialize a class of type Word.
        """
        self.word = self.clean(word.lower())
        if pos not in POS:
            logger.critical(f"Uknown POS {POS}")
            raise ValueError(f"Uknown POS {POS}")
        else:
            self.pos = POS[pos]
        if language not in wn.langs():
            logger.critical(f"Unknown language {language}.")
            raise ValueError(f"Unknown language {language}.")
        else:
            self.language = language
        self.synset = self.get_synsets()

    @staticmethod
    def clean(word: str) -> str:
        """Clean up the word by removing punctuations and lowering the letters.

        Returns:
            str: The cleaned out word.
        """
        return re.sub('[%s]' % re.escape(string.punctuation), '', word)

    def get_synsets(self) -> List[Union[None, Synset]]:
        """Get the NLTK synsets associated with the word, as well as the associated
        pos.
        """
        try:
            synsets = wn.synsets(self.word, lang=self.language, pos=self.pos)
            if not synsets:
                logger.warning(
                    f"Could not return any WordNet data for word {self.word}")
            return synsets
        except WordNetError:
            nltk.download('wordnet')
            nltk.download('omw-1.4')

    def check_synset(self, error_msg: str = "Returning word value") -> Union[str, None]:
        """Check if synset is empty. If it is, return the word.
        """
        if not self.synset:
            logger.warning(error_msg)
            return self.word

    def synonym(self) -> str:
        """Return a synonym of the word.
        Iterates several times in case the value returned is the same
        as the original word.
        """
        self.check_synset(error_msg=f"No synonym for word {self.word}")
        synonym = self.word
        counter = 0
        while synonym == self.word:
            synonym = self.synset[random.randrange(len(self.synset))].lemmas()[
                0].name()
            if counter <= len(self.synset):
                counter += 1
            else:
                logger.warning(f"Could not find synonym for word {self.word}")
                break
        return synonym

    def hypernym(self) -> str:
        """Get a hypernym for the word using nltk.
        Pick at random among the values returned by NLTK.
        """
        self.check_synset(error_msg=f"No hypernym for word {self.word}")

        hypernyms = self.synset[0].hypernyms()
        if hypernyms:
            return hypernyms[random.randrange(len(hypernyms))].lemmas()[0].name()
        else:
            logger.warning(
                f"No hypernym for word {self.word}, returning word.")
            return self.word

    def hyponym(self) -> str:
        """Get a hyponym for the word using Spacy most similar.
        """
        self.check_synset(error_msg=f"No hyponym for word {self.word}")

        hyponyms = self.synset[0].hyponyms()
        if hyponyms:
            return hyponyms[random.randrange(len(hyponyms))].lemmas()[0].name()
        else:
            logger.warning(f"No hyponym for word {self.word}, returning word.")
            return self.word

    def mispell(self) -> str:
        """Mispell a word by replacing a letter with another one.

        Returns:
            str: A mispelled word.
        """
        random_location = random.randrange(len(self.word))
        return self.word[:random_location] + \
            random.choice(string.ascii_lowercase) + \
            self.word[random_location + 1:]

    def omit(self) -> str:
        """Omit a word (ie: return an empty string).

        Returns:
            str: An empty string.
        """
        return ""
