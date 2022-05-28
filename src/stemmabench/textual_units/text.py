import random
from stemmabench.textual_units.sentence import Sentence

from stemmabench.textual_units.word import Word


class Text:
    """Class for representation of a text during the copy process.
    """

    def __init__(self, text) -> None:
        self.text = text

    def transform(self,
                  hyponym_rates=.05,
                  hypernym_rate=.05,
                  mispells_rates=.01,
                  omission_rates=0,
                  duplication_rate=.01,
                  duplication_nbr_words=2):
        """Transforms a text, first at a word level.
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

    @staticmethod
    def draw_boolean(rate: float):
        """Simulate a bernouilli law and returns True if the drawn value is < the rate.

        Args:
            rate (float): _description_
        """
        return random.random() < rate
