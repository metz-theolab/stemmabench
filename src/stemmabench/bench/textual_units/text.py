"""This module define a class `Text` whose methods apply transformations at 
the text level.
"""
from typing import Any, Dict

import numpy as np
from stemmabench.bench.config_parser import ProbabilisticConfig, VariantConfig, MetaConfig
from stemmabench.bench.textual_units.sentence import Sentence
from stemmabench.bench.textual_units.word import Word
from stemmabench.bench.textual_units.letter import Letter

class Text:
    """Class for the representation of a text undergoing a copy
    process.
    """

    def __init__(self, text: str, punc: str = ".") -> None:
        """Initializes an object of class Text, by wrapping a text into it.

        Args:
            text (str): The content of the text.
            punc (str): The standard punctuation to use
                as separator between sentences.

        # FIXME: deal with punctuations
        # FIXME: become more flexible in terms of modelization.
        """
        self.text = text
        self.sentences = [Sentence(sentence)
                          for sentence in text.split(punc) if sentence]
        self.words = [Word(word) for word in text.split(" ") if word]

        # TODO: improve punctuation diversity
        self.punc = punc

    @staticmethod
    def draw_boolean(rate: float) -> bool:
        """Simulate a bernouilli law and returns True
        if the drawn value is < the rate.

        Args:
            rate (float): The rate of the Bernouilli law.

        Returns:
            bool: The result of the draw
        """
        return np.random.random() < rate

    def transform_letter(self,
                         letter: Letter,
                         letter_config: Dict[str, Any]) -> str:
        """Transform the text at the letter level, by applying
        every method specified in the configuration.
        """
        for transformation, law in letter_config.items():
            if self.draw_boolean(law.rate):
                letter.letter = getattr(letter,
                                        transformation)(rate=law.rate,
                                                        **law.args)
        return letter.letter

    def transform_letters(self,
                          sentence: str,
                          letter_config: Dict[str, Any],
                          language: str) -> str:
        """Transform the text at the letter level, by applying to every word
        a possible transformation"""
        edited_letters = []
        # instantiate a class for every letter in the word
        letter_word = [Letter(letter, language=language)
                       for letter in sentence]
        for letter in letter_word:
            if letter.letter == " ":
                edited_letters.append(" ")
            else:
                edited_letters.append(self.transform_letter(letter=letter,
                                                        letter_config=letter_config))
        return "".join(edited_letters)

    def transform_word(self,
                       word: Word,
                       word_config: Dict[str, Any]) -> str:
        """Transform the text at the word level, by applying
        every method specified in the configuration.

        Args:
            word (Word): The word to transform.
            word_config (Dict[str, ProbabilisticConfig]): The configuration
                to use to set up word transformation.
        Returns:
            str: The newly transformed text.
        """
        for transformation, law in word_config.items():
            if self.draw_boolean(law.rate):
                word.word = getattr(word,
                                    transformation)(**law.args)
        return word.word

    def transform_words(self,
                        sentence: str,
                        word_config: Dict[str, ProbabilisticConfig],
                        language: str)\
            -> str:
        """Transform the text at the word level, by applying every
        method in the configuration on each word of a sentence.

        Args:
            sentence (str): The sentence to compute the transformation for.
            word_config (Dict[str, ProbabilisticConfig]): The dictionary
                describing the wanted configuration.
            language (str): The language used for word transformation.

        Return:
            str: The text transformed at the sentence level.
        """
        edited_words = []
        words_in_sentence = [Word(word, language=language)
                             for word in sentence.split(" ") if len(word) > 0]
        for word in words_in_sentence:
            edited_words.\
                append(self.transform_word(word=word,
                                           word_config=word_config
                                           )
                       )
        return " ".join(edited_words)

    def transform_sentence(self,
                           sentence: Sentence,
                           sentence_config: Dict[str, ProbabilisticConfig]) \
            -> str:
        """Transform the text at the sentence level, by applying
        every method in the configuration.

        Args:
            sentence (Sentence): The sentence to transform.
            sentence_config (Dict[str, ProbabilisticConfig]): The configuration
                of the sentence transformer.

        Returns:
            str: The transformed sentence.
        """
        for transformation, law in sentence_config.items():
            if self.draw_boolean(law.rate):
                sentence.sentence = getattr(sentence,
                                            transformation)(**law.args)
        return sentence.sentence

    def transform_sentences(self,
                            sentence_config: Dict[str, ProbabilisticConfig]) \
            -> str:
        """Transform every sentences of the text.

        Args:
            sentence_config (Dict[str, ProbabilisticConfig]): The configuration
                of the sentence transformer.

        Return:
            str: The text transformed at the sentence level.
        """
        edited_sentences = []
        for sentence in self.sentences:
            edited_sentences.\
                append(self.transform_sentence(sentence=sentence,
                                               sentence_config=sentence_config
                                               ).capitalize()
                       )
        return " ".join(edited_sentences)

    def transform(self,
                  variant_config: VariantConfig,
                  meta_config: MetaConfig):
        """Transforms the test using the configuration specified in the
        configuration variant_config. Operates first at the sentence level,
        and then moves on to the word level.
        """
        # Transform at sentence level
        text_edited_sentences = self.transform_sentences(
            sentence_config=variant_config.sentences)
        # Transform at word level
        sentence_edited_words = " "
        for sentence in text_edited_sentences.split(self.punc):
            sentence = self.transform_letters(
                sentence=sentence,
                letter_config=variant_config.letters,
                language=meta_config.language)
            new_sentence = self.transform_words(
                sentence=sentence,
                word_config=variant_config.words,
                language=meta_config.language).capitalize()
            if new_sentence:
                sentence_edited_words += new_sentence + self.punc + " "
        return sentence_edited_words.strip()
