import random
from typing import Any, Dict
from stemmabench.config_parser import ProbabilisticConfig, VariantConfig
from stemmabench.textual_units import sentence
from stemmabench.textual_units.sentence import Sentence
from stemmabench.textual_units.word import Word


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
        return random.random() < rate

    def transform_word(self,
                       word_config: Dict[str, Any]) -> str:
        """Transform the text at the word level, by applying
        every method specified in the configuration.

        Args:
            word_config (Dict[str, ProbabilisticConfig]): The configuration
                to use to set up word transformation.
        Returns:
            str: The newly transformed text.
        """

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
                return getattr(sentence,
                               transformation)(**law.args)
            return sentence.sentence

    def transform_sentences(self,
                            sentence_config: Dict[str, ProbabilisticConfig]) \
            -> str:
        """Transform every sentences of the text.

        Args:
            sentence_config (Dict[str, ProbabilisticConfig]): The configuration
                of the sentence transformer.
        """
        edited_sentences = []
        for sentence in self.sentences:
            edited_sentences.\
                append(self.transform_sentence(sentence=sentence,
                                               sentence_config=sentence_config
                                               )
                       )
        return " ".join(edited_sentences)

    def transform(self,
                  variant_config: VariantConfig):
        """Transforms the test using the configuration specified in the
        configuration variant_config. Operates first at the sentence level,
        and then moves on to the word level.
        """
        new_text = ""
        # Transform at sentence level
        for sentence in self.text.split("."):
            if len(sentence) > duplication_nbr_words + 1:
                if self.draw_boolean(duplication_rate):
                    new_text += Sentence(sentence).duplicate(
                        duplication_nbr_words) + "."
                else:
                    new_text += sentence + "."
        # Transform at word level
        transformed_text = ""
        for word in new_text.split(" "):
            if word:
                if self.draw_boolean(hyponym_rates):
                    transformed_text += Word(word).hyponym() + " "
                elif self.draw_boolean(hypernym_rate):
                    transformed_text += Word(word).hypernym() + " "
                elif self.draw_boolean(mispells_rates):
                    transformed_text += Word(word).mispell() + " "
                elif self.draw_boolean(omission_rates):
                    transformed_text += Word(word).omit() + " "
                else:
                    transformed_text += word + " "
        return transformed_text.strip()
