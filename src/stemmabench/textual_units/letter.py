"""This module define the `Letter` class whose methods apply transformations at 
the letter level.
"""
from typing import Dict, Any, List
from numpy.random import choice
from string import punctuation
from stemmabench.data import LETTERS


class Letter:
    """The Letter class defines several methods for variants at
    the letter level.
    """

    def __init__(self,
                 letter: str,
                 language: str = "en"
                 ) -> None:
        """Initialize a class of type Letter.

        Args:
            letter (str): The letter to wrap the class around.
        """
        self.letter = letter.lower()
        self.alphabet = LETTERS[language]

    @staticmethod
    def build_probability_matrix(rate: float,
                                 specific_rates: Dict[str, Dict[str, float]],
                                 alphabet: List[str]) -> Dict[str, Any]:
        """Build the probability matrix for the letter transformation.

        Args:
            rate (float): The global rate of transformation.
            specific_rates (Dict[str, Any]): The specific rates of transformation, with the format
                {
                 "a":
                    {
                     "b": 0.1,
                     "c": 0.2
                    ...
                    },
                "e": {
                    "a": 0.1
                }
                }
        """
        probability_matrix = {}
        for letter in alphabet:
            if letter in specific_rates.keys():
                # Store current specific rate matrix
                probability_matrix[letter] = specific_rates[letter]
            else:
                probability_matrix[letter] = {}
            for other_letter in alphabet:
                # FIXME: improve the computation of the probability of the letters
                # For now, there is no check on the rate value and it can sum higher than 1
                # should we really trust user input ?
                if other_letter not in probability_matrix[letter].keys() and other_letter != letter:
                    probability_matrix[letter].update(
                        {other_letter: rate/(len(alphabet))})
            # FIXME: compute the probability of the letter staying the same
            probability_matrix[letter].update({
                    letter: 1 -
                    sum(probability_matrix[letter].values())
                })
        return probability_matrix

    def mispell(self,
                rate: float,
                specific_rates: Dict[str, Any] = {}
                ) -> str:
        """Transform the letter into a variant.

        Probability matrix gives out for a given letter the probability of being switched
        into another one using the format:
            {
                "a": {
                    {
                    "b": 0.1,
                    "c": 0.2
                    ...
                    }
                }
            }.

        Returns:
            str: The newly transformed letter.
        """
        probability_matrix = self.build_probability_matrix(rate,
                                                           specific_rates,
                                                           self.alphabet)
        if self.letter in punctuation:
            return self.letter
        if self.letter in probability_matrix:
            proba_vector = probability_matrix[self.letter]
            return choice(list(proba_vector.keys()),
                                     p=list(proba_vector.values()))
