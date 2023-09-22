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
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

from stemmabench.data import SUPPORTED_LANGUAGES

# Define VariantAnalyzer class.
class VariantAnalyzer:

    def __init__(self,
                 table: AlignmentTable,
                 language: str = "en",
                 disable_synonym: bool = False) -> None:
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
        self.variant_locations: List[bool] = [col.variant for col in table.columns] 
        # language
        if language not in SUPPORTED_LANGUAGES:
            logger.critical(f"Unknown language {language}.")
            raise ValueError(f"Unknown language {language}.")
        self.language = language
        self.disable_synonym = disable_synonym

    @property
    def witness_names(self) -> List[str]:
        """Get the list of witness names from an AlignmentTable.

        Returns:
            List[str]: The list of witness names extracted from the table 
                rows.
        """
        return [row.header for row in self.table.rows]
    
    @property
    def array(self) -> np.ndarray[np.ndarray]:
        """Get an array representing an input Collatex AlignmentTable. 

        Returns:
            np.ndarray: A 2D numpy array representing the alignment table.
                - Rows are witnesses.
                - Columns are readings.
        """
        return self.alignment_table_to_numpy(self.table)
    
    #------------------------------------------------------------------------
    # ------------ UTILITY METHODS ------------------------------------------
    #------------------------------------------------------------------------
    @staticmethod
    def _get_token_strings(tokens_list: List[str | None], missing_reading:str="-"
        ) -> List[str]:
        """Extract token strings from a list of tokens or None values.
        """
        return [token_string.strip() if token_string else missing_reading 
                    for token_string in tokens_list]

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
        witness_data = {row.header: cls._get_token_strings(
            row.to_list_of_strings()) for row in table.rows}
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
    # ------------ VARIANT LOCATIONS: IDENTIFY AND COUNT BY TYPE ------------
    #------------------------------------------------------------------------
    def variant_locations_pairwise_matrix(self) -> np.ndarray: 
        """
        Create a symmetric Boolean matrix that identifies variant locations 
        for each pair of witnesses.

        Given an alignment table of dimensions (n, k) with n witnesses and k 
        readings, this function creates a Boolean matrix of dimensions (n, n)
        whose elements are k-d array, hence a (n, n, k)-dimension array.

        Each cell (i, j,) in the Boolean matrix represents a k-dimensional 
        Boolean vector. This vector indicates, for each reading, whether 
        witnesses i and j differ (True) or are similar (False). Note that the
        diagonal consists of k-D arrays filled only with `False` because each 
        witness is obvisouly fully similar to itself, reading by reading.

        Returns:
            np.ndarray: A 3-D (n, n, k) Boolean matrix indicating variant 
                locations among witnesses.
        """
        return np.expand_dims(self.array, axis=0) != np.expand_dims(self.array, axis=1)

    # OMIT
    @staticmethod
    def is_omit(word1: str, word2: str, missing: str = "-") -> bool:
        """
        Check if two words represent an omission based on a specified missing 
        character.

        Args:
            word1 (str): The first word.
            word2 (str): The second word.
            missing (str, optional): The character representing missing 
                readings. Defaults to "-".

        Returns:
            bool: True if the words represent an omission, False otherwise.
        """
        
        return word1 != word2 and (word1 == missing or word2 == missing)
    
    # MISPELL
    @staticmethod
    def is_mispell(word1: str, 
                   word2: str, 
                   distance: str = "DamerauLevenshtein", 
                   mispell_cutoff: float = 0.4) -> bool:
        """
        Check if two words are considered a misspelling based on a specified 
        distance metric and cutoff score.

        Args:
            word1 (str): The first word.
            word2 (str): The second word.
            distance (str, optional): The distance metric to use.
                (default: "DamerauLevenshtein").
                - "Levenshtein"
                - "DamerauLevenshtein"
                - "Hamming"
                - "JaroWinkler"
            mispell_cutoff (float, optional): The cutoff score for considering 
                two words as a misspelling (default: 0.4).

        Returns:
            bool: True if the words are a misspelling, False otherwise.
        
        Raises:
            ValueError: If an unsupported distance metric is provided.
        """
        dist_funcs = {
            "Levenshtein": textdistance.Levenshtein().normalized_distance,
            "DamerauLevenshtein": (textdistance.DamerauLevenshtein()
                                   .normalized_distance),
            "Hamming": textdistance.Hamming().normalized_distance,
            "JaroWinkler": textdistance.JaroWinkler().normalized_distance
        }
        if distance not in dist_funcs.keys():
            raise ValueError(f"Distance {distance} is not supported. "
                             f"Choose one among {dist_funcs.keys()}")
        norm_dist = dist_funcs[distance](str(word1), str(word2))
        # Mispell if distance > 0 (not exact match) 
        # but distance < cutoff (not too different)
        return bool(0 < norm_dist <= mispell_cutoff)
    
    # SYNONYMS
    @staticmethod
    def synonyms(word: str) -> set[str]:
        """
        Get synonyms for a given word using WordNet.

        Args:
            word (str): The word for which synonyms are to be found.

        Returns:
            set[str]: A set of synonyms for the given word.
        """
        return {lemma.lower() for syn in wordnet.synsets(word)
                for lemma in syn.lemma_names()
                    if lemma.lower() != word.lower()}
    
    @staticmethod
    def is_synonym(word1: str, word2: str) -> bool:
        """
        Check if two words are synonyms.

        Args:
            word1 (str): The first word.
            word2 (str): The second word.

        Returns:
            bool: True if the words are synonyms, False otherwise.
        """
        return WordNetLemmatizer().lemmatize(word2.lower()) in VariantAnalyzer.synonyms(word1)
    
    # IDENTIFYING VARIANT TYPE
    @staticmethod
    def which_variant_type(word1: str, word2: str,
                           missing: str = "-",
                           distance: str = "DamerauLevenshtein", # mispell
                           mispell_cutoff: float = 0.4 # mispell
                           ) -> str|bool:
        """
        Determine the type of variant between two words based on specified criteria.

        Args:
            word1 (str), word2 (str): The two words to consider.
            missing (str, optional): The character representing missing or 
                fragmented readings. Defaults to "-".
            distance (str, optional): The distance metric to use for mispell 
                detection. Defaults to "DamerauLevenshtein".
            mispell_cutoff (float, optional): The cutoff score for considering 
                two words as a mispell. Defaults to 0.4.

        Returns:
            str|bool: A string indicating the type of variant between the two 
                words or False if it's not a variant locations:
                - "O" for omit
                - "M" for mispell
                - "S" for synonym
                - "U" for undetermined
        """
        if word1 != word2:
            if VariantAnalyzer.is_omit(word1, word2, missing=missing):
                return "O" # Omit
            elif VariantAnalyzer.is_mispell(word1, 
                                            word2, 
                                            distance=distance,
                                            mispell_cutoff=mispell_cutoff):
                return "M"  # Mispell
            elif VariantAnalyzer.is_synonym(word1, word2):
                return "S"  # Synonym
            else:
                return "U"  # Undetermined
        return False
        
    @staticmethod
    def which_variant_type_vectorize(
            witness1: List[str],
            witness2: List[str],
            variant_locations: List[bool]|None = None,
            missing: str = "-",
            distance: str = "DamerauLevenshtein",
            mispell_cutoff: float = 0.4) -> List[str|bool]:
        """
        Determine the types of variants between two aligned witnesses (equal-
        length lists of words) based on specified criteria.

        Args:
            witness1, witness2 (List[str]): List of words from two witnesses.
            variant_locations (List[bool], optional): A list of boolean values 
                indicating variant locations between witnesses. If not provided, 
                it will be calculated based on differences between the two lists. 
                Defaults to None.
            missing (str, optional): The character representing missing or 
                fragmented readings. Defaults to "-".
            distance (str, optional): The distance metric to use for mispell 
                detection. Defaults to "DamerauLevenshtein".
            mispell_cutoff (float, optional): The cutoff score for considering 
                two words as a mispell (maximum normalized distance allowed). 
                Defaults to 0.4.

        Returns:
            List[str|bool]: A list indicating the types of variants between the
            two witnesses at each position:
                - "O" for omit
                - "M" for mispell
                - "S" for synonym
                - "U" for undetermined
                - False for non-variant locations

        Raises:
            AttributeError: If the lengths of witness1, witness2, and 
                variant_locations are not equal, or if variant_locations 
                contains non-boolean values.
        """
        # Check if variant_locations is provided and has the correct 
        # length and type.
        if variant_locations is not None:
            if len(witness1) != len(witness2) != len(variant_locations):
                raise AttributeError("Length mismatch among witnesses and or "
                                     "`variant_locations`.")
        # Get variant_locations between the two witnesses if not provided.
        if variant_locations is None:
            variant_locations = (np.array(witness1) != np.array(witness2))
        # Number of readings per witness; Initialize variant_types vector.
        k = len(variant_locations)
        variant_types = [False for _ in range(k)]
        # Loop through the witnesses' readings.
        for idx, (word1, word2, var_loc) in enumerate(zip(witness1, witness2, 
                                                          variant_locations)):
            # If it's a variant location (i.e., a place where readings differ)...
            if var_loc:
                # ...identify which variant type it is.
                variant_types[idx] = VariantAnalyzer.which_variant_type(
                    word1, word2, 
                    missing=missing, 
                    distance=distance, 
                    mispell_cutoff=mispell_cutoff)
        return variant_types
    
    def variant_type_pairwise_matrix(self,
                                missing: str = "-",
                                distance: str = "DamerauLevenshtein",
                                mispell_cutoff: float = 0.4) -> np.ndarray:
        """
        Create a matrix of variant types between pairs of witnesses in an 
        alignment table.

        Args:
            #table (np.ndarray): 2D numpy array representing aligned witnesses.
            missing (str, optional): The character representing missing or 
                fragmented readings. Defaults to "-".
            distance (str, optional): The distance metric to use for 
                misspelling detection. Defaults to "DamerauLevenshtein".
            mispell_cutoff (float, optional): The cutoff score for considering 
                two words as a misspelling. Defaults to 0.4.

        Returns:
            np.ndarray: A 3D numpy array representing variant types between 
                pairs of sequences.
        """
        # Get the shape, initialize differences matrix mask and create 
        # variant_locations matrix mask.
        n, k = self.array.shape
        diff_matrix = np.full((n, n, k), fill_value=False, dtype=object)
        var_locs_matrix: np.ndarray[(n, n, k), bool] = self.variant_locations_pairwise_matrix()
        # Iterate through pairs of witnesses (rows).
        for id1, id2 in combinations(range(n), 2):
            # get variant location mask between id1 and id2
            var_locs: np.ndarray[(k,), bool] = var_locs_matrix[id1, id2]
            # get the two manuscripts (witness) content.
            mss1: np.ndarray[(k,), str] = self.array[id1]
            mss2: np.ndarray[(k,), str] = self.array[id2]
            # add their variant type indicator mask.  
            diff_matrix[id1, id2] = diff_matrix[id2, id1] = \
                self.which_variant_type_vectorize(witness1=mss1,
                                                  witness2=mss2,
                                                  variant_locations=var_locs,
                                                  missing=missing,
                                                  distance=distance,
                                                  mispell_cutoff=mispell_cutoff
                                                  )
        return diff_matrix

    # DISSIMILIARITY MATRIX
    def dissimilarity_matrix(self,
                             variant_type: str | None = None,
                             normalize: bool = False,
                             missing: str = "-",
                             distance: str = "DamerauLevenshtein",
                             mispell_cutoff: float = 0.4) -> np.ndarray:
        """
        Calculate a dissimilarity matrix based on variant types between pairs 
        of sequences in an alignment table.

        Args:
            table (np.ndarray): 2D numpy array representing aligned witnesses.
            variant_type (str | None, optional): The type of variant to consider 
                when calculating dissimilarity. If None, consider all variant 
                types. Defaults to None.
            normalize (bool, optional): Whether to normalize the dissimilarity 
                matrix by the number of readings per witness. Defaults to False.
            missing (str, optional): The character representing missing or 
                fragmented readings. Defaults to "-".
            distance (str, optional): The distance metric to use for misspell 
                detection. Defaults to "DamerauLevenshtein".
            mispell_cutoff (float, optional): The cutoff score for considering 
                two words as a misspelling. Defaults to 0.4.

        Returns:
            np.ndarray: A 2D numpy array representing the dissimilarity matrix 
                based on variant types.
        
        Raises:
            AttributeError: If an invalid value for `variant_type` is provided.
        """
        valid_variant_types = ["O", "M", "S", "U"]
        diff_matrix = self.variant_type_pairwise_matrix(missing=missing, 
                                               distance=distance,
                                               mispell_cutoff=mispell_cutoff)
        if variant_type:
            if variant_type not in valid_variant_types:
                raise AttributeError(f"Invalid value for `variant_type`: " 
                                     f"{variant_type}. Valid in {valid_variant_types}")
            # Create a mask for the input variant type.
            count_mask = (diff_matrix == variant_type)
        else:  # variant_type is None
            # Create a mask for all variant locations regardless of the type.
            count_mask = (diff_matrix != False)
        if normalize:  # Normalize by the number of readings.
            return np.sum(count_mask, axis=2) / self.array.shape[1]
        return np.sum(count_mask, axis=2)
    
    # OPERATION RATE
    def operation_rate(self,
                       variant_type=None,
                       normalize=True,
                       decimals=4,
                       **kwargs) -> float:
        """
        Calculate the operation rate for a specific variant type in an 
        alignment table.

        Args:
            table (np.ndarray): 2D numpy array representing aligned witnesses.
            variant_type (str, optional): The type of variant to consider when 
                calculating the operation rate. Defaults to None (all).
                Possible values are: 
                    - "O": omit, 
                    - "M": mispell, 
                    - "S": synonym, 
                    - "U": undetermined
            normalize (bool, optional): Whether to normalize the operation rate. 
                Defaults to True.
            decimals (int, optional): The number of decimal places to round the 
                result to. Defaults to 4.
            **kwargs: Additional keyword arguments to pass to the 
                dissimilarity_matrix function.

        Returns:
            float: The calculated operation rate for the specified variant type, 
                rounded to the specified number of decimal places.
        """
        # Get the number of readings in the alignment table.
        n, _ = self.array.shape
        # Calculate the dissimilarity matrix.
        dissim_matrix = self.dissimilarity_matrix(variant_type=variant_type,
                                                  normalize=normalize, **kwargs)
        # Extract the lower triangle of the dissimilarity matrix.
        lower_triangle = np.tril(dissim_matrix)
        # Select the non-diagonal elements of the lower triangle.
        nondiag = lower_triangle[np.tri(n, n, k=-1, dtype=bool)]
        # Calculate the mean of non-diagonal lower triangle.
        return np.round(nondiag.mean(), decimals=decimals)
    
    def omit_rate(self, missing: str = "-", normalize=True, decimals=4) -> float:
        """
        Calculate the omit rate for an alignment table.

        Args:
            alignment_array (np.ndarray): 2D numpy array representing aligned
                witnesses.
            normalize (bool, optional): Whether to normalize the omit rate. 
                Defaults to True.
            decimals (int, optional): The number of decimal places to round the 
                result to. Defaults to 4.

        Returns:
            float: The calculated omit rate, rounded to the specified number of
                decimal places.
        """
        return self.operation_rate(variant_type="O",
                                   normalize=normalize, 
                                   decimals=decimals, 
                                   missing=missing)

    def mispell_rate(self, 
                     normalize: bool = True, 
                     decimals: int = 4, 
                     distance: str = "DamerauLevenshtein",
                     mispell_cutoff: float = 0.4) -> float:
        """
        Calculate the misspelling rate for an alignment table.

        Args:
            alignment_array (np.ndarray): 2D numpy array representing aligned 
                witnesses.
            normalize (bool, optional): Whether to normalize the misspelling 
                rate (False <-> average count). Defaults to True.
            decimals (int, optional): The number of decimal places to round the
                result to. Defaults to 4.
            distance (str, optional): The distance metric to use for 
                misspelling detection. Defaults to "DamerauLevenshtein".
            mispell_cutoff (float, optional): The cutoff score for considering 
                two words as a misspelling (maximum normalized distance 
                allowed). Defaults to 0.4.

        Returns:
            float: The calculated misspelling rate, rounded to the specified 
                number of decimal places.
        """
        return self.operation_rate(variant_type="M", 
                                   normalize=normalize,
                                   decimals=decimals, 
                                   distance=distance, 
                                   mispell_cutoff=mispell_cutoff)

    def synonym_rate(self, normalize: bool = True, decimals: int = 4) -> float:
        """
        Calculate the synonym rate for an alignment table.

        Args:
            alignment_array (np.ndarray): 2D numpy array representing aligned
                witnesses.
            normalize (bool, optional): Whether to normalize the synonym rate. 
                Defaults to True.
            decimals (int, optional): The number of decimal places to round the
                result to. Defaults to 4.

        Returns:
            float: The calculated synonym rate, rounded to the specified 
                number of decimal places.
        """
        return self.operation_rate(variant_type="S", 
                                   normalize=normalize,
                                   decimals=decimals)

    def undetermined_operation_rate(self, 
                                    normalize: bool = True, 
                                    decimals: int = 4) -> float:
        """
        Calculate the undetermined operation rate for an alignment table.

        Args:
            alignment_array (np.ndarray): 2D numpy array representing aligned
                witnesses.
            normalize (bool, optional): Whether to normalize the undetermined 
                operation rate. Defaults to True.
            decimals (int, optional): The number of decimal places to round the
                result to. Defaults to 4.

        Returns:
            float: The calculated undetermined operation rate, rounded to the 
                specified number of decimal places.
        """
        return self.operation_rate(variant_type="U", 
                                   normalize=normalize,
                                   decimals=decimals)

    #------------------------------------------------------------------------
    # ------------ FRAGMENTATION --------------------------------------------
    #------------------------------------------------------------------------
    @staticmethod
    def fragment_locations(witness: List[str], missing: str = "-"
        ) -> np.ndarray[bool]:
        """Identify fragment locations in a list of readings.
        """
        return np.array([reading == missing for reading in witness])
 
    def fragment_locations_matrix(self, missing: str = "-") -> np.ndarray[bool]:
        """
        Identify (mask) fragment locations in an alignment table.

        Args:
            alignment_table (np.ndarray): 2D numpy array representing
                aligned witnesses.
            missing (str, optional): The character representing missing
                or fragmented readings. Defaults to "-".

        Returns:
            np.ndarray[bool]: A 2D numpy array of boolean indicating
                fragment locations for each witness.
        """

        return np.array([self.fragment_locations(witness, missing=missing)
                        for witness in self.array])
    
    def fragment_locations_count(self,
                                 missing: str = "-",
                                 normalize: bool = False) -> np.ndarray[bool]:
        """
        Calculate the count of fragment locations for each witness in an 
        alignment table.

        Args:
            alignment_table (np.ndarray): 2D numpy array representing
                aligned witnesses.
            missing (str, optional): The character representing missing
                or fragmented readings. Defaults to "-".
            normalize (bool, optional): Whether to normalize the fragment
                count by the number of readings per witness. Defaults to False.

        Returns:
            List[bool]: A list of fragment counts for each witness, either
                normalized or not.
        """
        # Get the number of readings after alignment.
        n_readings = self.array.shape[1]
        # Count fragment locations per witness.
        count_fragment_location = self.fragment_locations_matrix(
            missing=missing).sum(axis=1)
        if normalize:
            # Normalize by the number of reading per witness 
            # in the alignment table. 
            return  count_fragment_location / n_readings
        return count_fragment_location
    
    def fragment_rate(self,
                      missing: str = "-", 
                      normalize: bool = True, 
                      strategy: str = "max",
                      decimals: int = 4) -> float:
        """
        Calculate the fragment rate for an alignment table based on a given 
        strategy.

        Args:
            alignment_table (np.ndarray): 2D numpy array representing aligned
                witnesses.
            missing (str, optional): The character representing missing or
                fragmented readings. Defaults to "-".
            normalize (bool, optional): Whether to normalize the fragment rate.
                Defaults to True.
            strategy (str, optional): The strategy for calculating the fragment
                rate ("mean" or "max"). Defaults to "mean".

        Returns:
            float: The calculated fragment rate.

        Raises:
            ValueError: If an unsupported strategy is provided.
        """

        fragment_counts = self.fragment_locations_count(missing=missing, 
                                                        normalize=normalize)
        if strategy == "mean":
            return fragment_counts.mean().round(decimals)
        elif strategy == "max":
            return fragment_counts.max().round(decimals)
        else:
            raise ValueError(f"Only `mean` and `max` are supported." 
                             f"Input: `{strategy}`.")

    def analysis_summary(self,
                         include: List[str] = ["all"],
                         decimals: int = 4,
                         normalize: bool = True,
                         missing: str = "-",
                         distance: str = "DamerauLevenshtein",
                         mispell_cutoff: float = 0.4,
                         frag_strategy: str = "max"
                         ) -> Dict[str, float]:
        """
        Calculate various rates of interest for an alignment table.

        Args:
            include (List[str], optional): A list of rates to include in the 
                analysis. Defaults to ["all"], which includes all rates.
                Available operations are:
                    - "omit"
                    - "mispell"
                    - "synonym"
                    - "fragment"
            decimal (int, optional): The number of decimal places to round the
                results to. Defaults to 4.

        Returns:
            Dict[str, float]: A dictionary containing the calculated rates for 
                the specified analysis types.
        """

        # If "all" is specified, include all analysis types.
        if include == ["all"]:
            include = ["omit", "mispell", "synonym", "fragment", "undetermined"]
        if self.disable_synonym and ("synonym" in  include):
            include.remove("synonym")
        
        # Define a dictionary of analysis functions.
        trf_dict = {"omit": [self.omit_rate, {"missing": missing}],
                    "mispell": [self.mispell_rate, 
                                {"distance": distance, 
                                 "mispell_cutoff": mispell_cutoff}],
                    "synonym": [self.synonym_rate, {}],
                    "fragment": [self.fragment_rate, {"missing": missing, 
                                                      "strategy": frag_strategy}],
                    "undetermined": [self.undetermined_operation_rate, {}]
                   }
        
        rates = {}
        for op_name in include:
            op_func, kwargs = trf_dict[op_name]
            rates[op_name] = op_func(decimals=decimals, 
                                     normalize=normalize, **kwargs)
        # Calculate the specified rates.
        return rates