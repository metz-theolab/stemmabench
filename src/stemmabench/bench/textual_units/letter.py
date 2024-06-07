"""This module defines the `Letter` class whose methods apply transformations at 
the letter level.
"""
from typing import Dict, Any, List
from numpy.random import choice
from string import punctuation
from stemmabench.bench.data import LETTERS
import numpy as np


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
            if letter in specific_rates:
                if not all(specific_letter in alphabet for specific_letter in specific_rates[letter]):
                    raise ValueError(f"One or more specific letters for '{letter}' are not in the alphabet")  
                
            specific_rate = specific_rates.get(letter, {})
            total_specific_rate = sum(specific_rate.values())

            if total_specific_rate > rate:
                raise ValueError(f"Sum of specific rates for '{letter}' is higher than the global rate")

            probability_matrix[letter] = {**specific_rate, letter: 1 - rate}
            remaining_rate = rate - total_specific_rate
            remaining_letters = len(alphabet) - len(probability_matrix[letter])

            ponderate_rate = remaining_rate / remaining_letters if remaining_letters > 0 else 1

            for other_letter in set(alphabet) - set(probability_matrix[letter]):
                probability_matrix[letter][other_letter] = ponderate_rate if letter in specific_rates else rate / (len(alphabet)-1)

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
            p_normalized  = np.array(list(proba_vector.values()))/np.array(list(proba_vector.values())).sum()
            return choice(list(proba_vector.keys()),
                                     p=p_normalized)
