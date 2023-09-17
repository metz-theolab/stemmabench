"""
This module analyzes an alignment table of variant texts and provides 
estimates of the frequency and distribution of various types of transformation 
(modification operations) within the overall tradition.
"""

# Import libraries.
import numpy as np
import textdistance

from loguru import logger
from typing import List, Dict, Union
from itertools import combinations
from collatex.core_classes import AlignmentTable, Token

from stemmabench.data import SUPPORTED_LANGUAGES


# Define AlignmentTableAnalysis class.
class VariantAnalyzer:
    
    def __init__(self,
                 table: AlignmentTable,
                #  array: Union[np.ndarray[object], None] = None,
                 language: str = "en") -> None:
        """_summary_

        Args:
            table (AlignmentTable): _description_.
            array (Union[np.ndarray[object], None], optional): _description_. 
                Defaults to None.
            language (str, optional): _description_. 
                Defaults to "en".
        """
        # alignment table
        self.table = table
        self.array = self.alignment_table_to_numpy(self.table)
        self.variant_locations: List[bool] = [col.variant for col in table.columns] 
        # language
        if language not in SUPPORTED_LANGUAGES:
            logger.critical(f"Unknown language {language}.")
            raise ValueError(f"Unknown language {language}.")
        self.language = language

    @property
    def witness_names(self) -> List[str]:
        """Get the list of witness names from an AlignmentTable.

        Returns:
            List[str]: The list of witness names extracted from the table 
                rows.
        """
        return [row.header for row in self.table.rows]
    
    #------------------------------------------------------------------------
    # ------------ UTILITY METHODS ------------------------------------------
    #------------------------------------------------------------------------
    @staticmethod
    def _iter_token(token: Union[List[Token], None]) -> List[Union[Token, None]]:
        """Iterate over a single-element list of tokens.
        """
        if token and not isinstance(token, list):
            raise AttributeError("`token` should be a `List[Token]` object.")
        return token if token else [None]

    @staticmethod
    def _get_token_string(token: Token | None, 
                        missing_reading: str = "-") -> str:
        """
        Get the token string from a Token object, or return a default value.

        Args:
            missing_reading (str, optional): The default string to return if 
                the token is `None`. Defaults to "-".
        """
        return token.token_string if token else missing_reading

    @staticmethod
    def _get_token_strings_from_list(tokens: List[List[Token] | None]) -> List[str]:
        """Extract token strings from a nested list of tokens or None values.
        """
        return [VariantAnalyzer._get_token_string(token) 
                for token_ls in tokens 
                for token in VariantAnalyzer._iter_token(token_ls)]

    ### CLASS METHODS
    @classmethod
    def alignment_table_to_numpy(cls, table: AlignmentTable) -> np.ndarray[object]:
        """
        Convert an AlignmentTable to a numpy array.

        Args:
            table (AlignmentTable): The AlignmentTable to be converted.

        Returns:
            np.ndarray: A 2-D numpy array representing the alignment table.
                - Rows (first dimension) correspond to the witnesses.
                - Columns (second dimension) correspond to the readings.
        """
        # Create a dictionary to store witness data.
        witness_data = {row.header: cls._get_token_strings_from_list(row.to_list()) 
                        for row in table.rows}
        # Get the list of row names (witness names).
        row_names = list(witness_data.keys())
        # Create an empty numpy array with the same shape as the alignment table.
        alignment_array = np.empty(shape=(len(table.rows), len(table.columns)), 
                                   dtype=object)
        # Fill the numpy array with the token strings lists from the witness data.
        alignment_array = np.array([witness_data[name] for name in row_names], 
                                   dtype=object)
        return alignment_array


    #------------------------------------------------------------------------
    # ------------ VARIANT LOCATIONS ----------------------------------------
    #------------------------------------------------------------------------
    def variant_locations_pairwise_matrix(self) -> np.ndarray: 
        """
        Create a symmetric Boolean matrix that identifies variant locations 
        for each pair of witnesses.

        Given an alignment table of dimensions (n, k) with n witnesses and k 
        readings, this function creates a Boolean matrix of dimensions (n, n, k).

        Each cell (i, j) in the Boolean matrix represents a k-dimensional 
        Boolean vector. This vector indicates, for each reading, whether 
        witnesses i and j differ (True) or are similar (False). Note that the
        diagonal consists of k-D arrays filled only with `False` because each 
        witness is obvisouly fully similar to itself, reading by reading.

        Returns:
            np.ndarray: A 3-D (n, n, k) Boolean matrix indicating variant 
                locations among witnesses.
        """
        return np.expand_dims(self.array, axis=0) != np.expand_dims(self.array, axis=1)