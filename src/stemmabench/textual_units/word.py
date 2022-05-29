import random
import re
import string
from typing import List
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
    """The Word class defines several methods for variants at
    the word level.
    """

    def __init__(self,
                 word: str,
                 language: str = "eng",
                 pos: str = "NA") -> None:
        """Initialize a class of type Word.

        Args:
            word (str): The word to wrap the class around.
            language (str, optional): The language to perform the variant in.
                Defaults to "eng".
            pos (str, optional): The POS of the considered word.
                Defaults to "NOUN".
        """
        self.word = self.clean(word)
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
        self.has_synset = True if self.synset else False

    @staticmethod
    def clean(word: str) -> str:
        """Clean up the word by removing punctuations and lowering the letters.

        Args:
            str: The word to clean.

        Returns:
            str: The cleaned out word.
        """
        return re.sub('[%s]' % re.escape(string.punctuation), '', word).lower()

    def synsets(self) -> List[Synset]:
        """Get the synsets associated with the word.
        """
        synsets = wn.synsets(self.word, lang=self.language, pos=self.pos)
        if not synsets:
            logger.warning(
                f"Could not return any WordNet data for word {self.word}")
        return synsets

    def get_synsets(self) -> List[Synset]:
        """Get the NLTK synsets associated with the word, as well as the associated
        pos.
        """
        try:
            return self.synsets()
        except WordNetError:
            try:
                logger.warning("Ooops, something went wrong, trying to download the\
                    right packages...")
                nltk.download('wordnet')
                nltk.download('omw-1.4')
                return self.synsets()
            except Exception:
                logger.critical(
                    f"Could not get synsets for word {self.word}, aborting...")
                raise Exception("Could not get synsets.")

    def synonym(self) -> str:
        """Return a synonym of the word, by picking randomly into the Synset
        data.
        Iterates several times in case the value returned is the same
        as the original word.

        Returns:
            str: The selected synonym.
        """
        if not self.has_synset:
            return self.word
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

        Returns:
            str: The selected hypernym
        """
        if not self.has_synset:
            return self.word
        hypernyms = self.synset[0].hypernyms()
        if hypernyms:
            return hypernyms[random.randrange(len(hypernyms))]\
                .lemmas()[0].name()
        else:
            logger.warning(
                f"No hypernym for word {self.word}, returning word.")
            return self.word

    def hyponym(self) -> str:
        """Get a hyponym for the word using nltk.
        Pick at random among the values returned by NLTK.

        Returns:
            str: The selected hyponym.
        """
        if not self.has_synset:
            return self.word
        hyponyms = self.synset[0].hyponyms()
        if hyponyms:
            return hyponyms[random.randrange(len(hyponyms))].lemmas()[0].name()
        else:
            logger.warning(f"No hyponym for word {self.word}, returning word.")
            return self.word

    def mispell(self) -> str:
        """Mispell the word by replacing a letter with another one.

        Returns:
            str: The mispelled word.
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
