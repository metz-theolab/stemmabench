"""This module define a class `Text` whose methods apply transformations at 
the text level.
"""
from typing import Any, Dict
import numpy as np
from scipy.stats import binom, poisson
from stemmabench.config_parser import (
    ProbabilisticConfig, 
    FragmentationConfig, 
    VariantConfig,
    MetaConfig
)
from stemmabench.textual_units.word import Word
from stemmabench.textual_units.sentence import Sentence


class Text:
    """Class for the representation of a text undergoing a copy
    process.
    """

    def __init__(self, text: str, punc: str = ".", seed=None) -> None:
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
        self.rng = np.random.default_rng(seed)

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

    def transform_word(self,
                       word: Word,
                       word_config: Dict[str, ProbabilisticConfig]) -> str:
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
            new_sentence = self.transform_words(
                sentence=sentence,
                word_config=variant_config.words,
                language=meta_config.language).capitalize()
            if new_sentence:
                sentence_edited_words += new_sentence + self.punc + " "
        return sentence_edited_words.strip()

    def fragment(self, 
                 fragment_config: FragmentationConfig,
                 sep: str=" "
        ) -> str:
        """
        Fragment a given text by randomly removing words.

        Args:
            text (str): The input text to be fragmented.
            fragment_config (FragmentConfig): The configuration of the fragment
                transformer.
            sep (str, optional): separator used to split the input text
                into words. Default is " ".

        Returns:
            str: fragmented text with words removed.
        
        # TODO: Use the input `Poisson` `rate` to use it as a fraction of the 
        # total number of words in the text and raise an Exception for values 
        # below a certain threshold (e.g. 5%) in order to avoid full zero 
        # distribution vector. 
        """
        # Split the text into a list of words and get total word count.
        words = self.text.split(sep)
        n_words = len(words) 
        indices = np.arange(n_words)

        # Generate a distribution for fragmentation on word indices based on 
        # the input law.
        if fragment_config.distribution.law == "Discrete Uniform":
            locations_dist = np.full(shape=n_words, fill_value=1/n_words)
        elif fragment_config.distribution.law == "Binomial":
            locations_dist = binom.pmf(k=indices, n=n_words, 
                                        p=fragment_config.distribution.rate)
        elif fragment_config.distribution.law == "Poisson":
            # The input rate is expressed as fraction of the number of words.
            # Ensure having consistent distribution with enough non-zero values.
            mu = fragment_config.distribution.rate * n_words
            locations_dist = poisson.pmf(k=indices, mu=mu)
        else:
            raise ValueError("Only 'Binomial', 'Discrete Uniform', and" 
                             "'Poisson' laws are supported.")
        locations_dist /= locations_dist.sum()

        # Calculate the number of fragment locations based on the fragment rate.
        n_frag_loc = min(
            # ensure n_frag_loc (sample size) is larger that the number of 
            # non-zero entries in the distribution vector
            np.sum(locations_dist!=0), 
            int(self.rng.uniform(0, fragment_config.max_rate) * n_words)
        )

        # Choose fragment locations according.
        frag_locations = self.rng.choice(indices, size=n_frag_loc, replace=False,
                                    p=locations_dist)
        
        # Remove words at the selected fragment locations.
        words = np.delete(words, frag_locations)
        
        # Join the remaining words to form the fragmented text.
        return sep.join(words)