"""Unit test for variant_analyzer.py module.
"""
import unittest
from unittest.mock import Mock, patch

import numpy as np
from collatex.core_classes import AlignmentTable, Token, Column, Row
from stemmabench.variant_analyzer import VariantAnalyzer


# ----------------------------------------------------------------------------
# -------- TEST VARIANT ANALYZER PROPERTIES AND CLASS METHODS ----------------
# ----------------------------------------------------------------------------
class TestVariantAnalyzerProperties(unittest.TestCase):
    """Test VariantAnalyzer properties.
    """
    def setUp(self):
        # Create a mock AlignmentTable for testing
        self.mock_table = Mock(spec=AlignmentTable)
        self.mock_table2 = Mock(spec=AlignmentTable)
        # Mock columns
        self.column1 = Mock(spec=Column, variant=True)
        self.column2 = Mock(spec=Column, variant=False)
        self.mock_table.columns = self.mock_table2.columns = [self.column1, self.column2]
        # Mock rows
        self.token11 = Mock(spec=Token, token_data={"n": "token11"}, token_string="token11")
        self.token12 = Mock(spec=Token, token_data={"n": "token12"}, token_string="token12")
        self.row1 = Mock(spec=Row, header="Witness1", cells=[[self.token11], None])
        self.row2 = Mock(spec=Row, header="Witness2", cells=[[self.token12], None])
        self.mock_table.rows = [self.row1, self.row2]
        # --- Mock table 2 (Hand design to avoid iteration error over `Mock`
        # when calling `alignment_table_to_numpy`.)
        row21 = Mock(spec=Row, header="Witness1")
        row21.to_list_of_strings.return_value = ["token11", None]
        row22 = Mock(spec=Row, header="Witness2")
        row22.to_list_of_strings.return_value = ["token12", None]
        self.mock_table2.rows = [row21, row22]
        # Create a VariantAnalyzer instance for testing
        self.analyzer = VariantAnalyzer(self.mock_table, language="en", disable_synonym=False)

    def test_variant_locations_property(self):
        """Test `variant_locations` property.
        """
        # Ensure that the variant_locations property returns the expected list of booleans
        expected_variant_locations = [True, False]
        self.assertEqual(self.analyzer.variant_locations, expected_variant_locations)

    def test_language_property(self):
        """Test `language` property.
        """
        # Ensure that the language property returns the expected language
        self.assertEqual(self.analyzer.language, "en")
        # Test if the language property logs an error for an unsupported language
        with self.assertRaises(ValueError):
            VariantAnalyzer(self.mock_table, language="de")

    def test_witness_names_property(self):
        """Test `witness_names` property.
        """
        # Ensure that the witness_names property returns the expected list of witness names
        self.assertEqual(self.analyzer.witness_names, ["Witness1", "Witness2"])

    def test_array_property(self):
        """Test `array` property.
        """
        self.analyzer = VariantAnalyzer(self.mock_table2)
        # Accessing the array property should call alignment_table_to_numpy.
        with unittest.mock.patch.object(self.analyzer, 'alignment_table_to_numpy') \
            as mock_to_numpy:
            _ = self.analyzer.array
            mock_to_numpy.assert_called_once_with(self.mock_table2)
        # Check if the array property is set after calling it.
        self.assertIsNotNone(self.analyzer.array)

    def test_get_token_strings_static_method(self):
        """Test `_get_token_strings` static method.
        """
        # Test the _get_token_strings_from_list static method with a list of tokens and None values
        tokens_list = [self.token11.token_string, None, self.token12.token_string]
        expected = ["token11", "-", "token12"]
        self.assertEqual(self.analyzer._get_token_strings(tokens_list), expected)

    def test_alignment_table_to_numpy(self):
        """Test `alignment_table_to_numpy` class method.
        """
        result = VariantAnalyzer.alignment_table_to_numpy(self.mock_table2)
        expected_array = np.array([["token11", "-"],
                                   ["token12", "-"]])
        self.assertTrue(np.array_equal(result, expected_array))

# ----------------------------------------------------------------------------
# -------- TEST VARIANT LOCATIONS TYPE IDENTIFICATION METHODS ----------------
# ----------------------------------------------------------------------------
class TestVariantAnalyzerMethods(unittest.TestCase):
    """Test VariantAnalyzer methods : variant locations and variant types.
    """
    def setUp(self):
        # Create a mock AlignmentTable for testing
        self.mock_table = Mock(spec=AlignmentTable)
        self.mock_table.columns = [Mock(variant=True) for _ in range(3)]
        self.mock_table.rows = [
            Mock(header="Witness1", to_list_of_strings=lambda: ["The", "dog"]),
            Mock(header="Witness2", to_list_of_strings=lambda: ["The", "cat"]),
            Mock(header="Witness3", to_list_of_strings=lambda: [  "A", "dog"])
        ]
        self.mock_table2 = Mock(spec=AlignmentTable)
        var_locs = [False, True, True, True, True, True]
        self.mock_table2.columns = [Mock(variant=var_loc) for var_loc in var_locs]
        witness1 = ["The", "truth", "should", "be", "revealed", "now"]
        witness2 = ["The", "truht", "ground", "-",   "expose",   '-']
        self.mock_table2.rows = [
            Mock(header="Witness1", to_list_of_strings=lambda: witness1),
            Mock(header="Witness2", to_list_of_strings=lambda: witness2),
        ]
        # Create a VariantAnalyzer instance for testing
        self.analyzer = VariantAnalyzer(self.mock_table)
        self.analyzer2 = VariantAnalyzer(self.mock_table2)
        self.witnesses = np.array([witness1, witness2])

    def test_variant_locations_pairwise_matrix(self):
        """Test `variant_locations_pairwise_matrix` method.
        """
        # Sample data = [[["The", "dog"], ["The", "cat"], ["A", "dog"]]]
        expected_output = [[[False, False], [False,  True], [True,  False]],
                           [[False,  True], [False, False], [True,   True]],
                           [[True,  False], [True,   True], [False, False]]]
        # Call the variant_locations_pairwise_matrix method
        result = self.analyzer.variant_locations_pairwise_matrix()
        # Check if the result matches the expected output
        self.assertTrue(np.array_equal(result, expected_output))

    def test_is_omit(self):
        """Test `is_omit` static method.
        """
        # Test cases for is_omit
        self.assertTrue(self.analyzer.is_omit("a", "-"))
        self.assertFalse(self.analyzer.is_omit("a", "b"))
        self.assertFalse(self.analyzer.is_omit("-", "-"))

    def test_is_mispell(self):
        """Test `is_mispell` static method.
        """
        # Test cases for is_mispell
        self.assertTrue(self.analyzer.is_mispell("truth", "truht"))
        self.assertFalse(self.analyzer.is_mispell("truth", "truht", mispell_cutoff=0.01))
        # Test case for ValueError when using an unsupported distance metric
        with self.assertRaises(ValueError):
            self.analyzer.is_mispell("truth", "truht", distance="fake_distance")

    @patch('stemmabench.variant_analyzer.VariantAnalyzer.synonyms', return_value={
        'altogether', 'completely', 'entirely', 'totally', 'whole', 'wholly'})
    def test_synonyms(self, mock_synonyms):
        """Test `is_mispell` static method.
        """
        # Call the synonyms method
        result = self.analyzer.synonyms("all")
        # Check if the result matches the expected set of synonyms
        expected_synonyms = mock_synonyms.return_value
        self.assertEqual(result, expected_synonyms)

    @patch('stemmabench.variant_analyzer.VariantAnalyzer.synonyms')
    def test_is_synonym(self, mock_synonyms):
        """Test `is_synonym` static method.
        """
        mock_synonyms.return_value = {'altogether', 'completely', 'entirely',
                                      'totally', 'whole', 'wholly'}
        # Test cases for is_synonym
        self.assertTrue(self.analyzer.is_synonym('all', 'TOTALLY'))
        self.assertFalse(self.analyzer.is_synonym('all', 'nothing'))

    def test_which_variant_type(self):
        """Test `which_variant_type` static method.
        """
        # Test cases for which_variant_type
        self.assertEqual(self.analyzer.which_variant_type("a", "-"), "O")
        self.assertEqual(self.analyzer.which_variant_type("a", "b"), "U")
        self.assertEqual(self.analyzer.which_variant_type("-", "-"), False)
        self.assertEqual(self.analyzer.which_variant_type("truth", "truht"), "M")
        self.assertEqual(self.analyzer.which_variant_type("all", "TOTALLY"), "S")
        # Test case for ValueError when using an unsupported distance metric
        with self.assertRaises(ValueError):
            self.analyzer.which_variant_type("truth", "truht", distance="fake_distance")

    def test_which_variant_type_vectorize(self):
        """Test `which_variant_type_vectorize` static method.
        """
        expected_output = [False, "M", "U", "O", "S", "O"]
        # Call the which_variant_type_vectorize method
        result = self.analyzer.which_variant_type_vectorize(self.witnesses[0], self.witnesses[1])
        # Check if the result matches the expected output
        self.assertEqual(result, expected_output)

    def test_variant_type_pairwise_matrix(self):
        """Test `variant_type_pairwise_matrix` method.
        """
        diag = [False, False, False, False, False, False]
        var_types12 = var_types21 = [False, "M", "U", "O", "S", "O"]
        expected_output = np.array([[       diag, var_types12],
                                    [var_types21,        diag]], dtype=object)
        # Call the variant_type_pairwise_matrix method
        result = self.analyzer2.variant_type_pairwise_matrix()
        self.assertTrue(np.array_equiv(result, expected_output))

    def test_dissimilarity_matrix(self):
        """Test `dissimilarity_matrix` method.
        """
        # Test dissimilarity_matrix general variant location (no normalization)
        result = self.analyzer2.dissimilarity_matrix(variant_type=None)
        expected_output = [[0, 5], [5, 0]]
        self.assertTrue(np.array_equal(result, expected_output))

        # Test dissimilarity_matrix general variant location (with normalization)
        result = self.analyzer2.dissimilarity_matrix(variant_type=None, normalize=True)
        expected_output = [[0, 5/6], [5/6, 0]]
        self.assertTrue(np.allclose(result, expected_output))

        # Test dissimilarity_matrix with variant_type "O" (omit)
        result = self.analyzer2.dissimilarity_matrix(variant_type="O")
        expected_output = [[0, 2], [2, 0]]
        self.assertTrue(np.array_equal(result, expected_output))

        # Test dissimilarity_matrix with variant_type "M" (mispell)
        result = self.analyzer2.dissimilarity_matrix(variant_type="M")
        expected_output = [[0, 1], [1, 0]]
        self.assertTrue(np.array_equal(result, expected_output))

        # Test dissimilarity_matrix with variant_type "U" (undetermined)
        result = self.analyzer2.dissimilarity_matrix(variant_type="U")
        expected_output = [[0, 1], [1, 0]]
        self.assertTrue(np.array_equal(result, expected_output))

    def test_operation_rate(self):
        """Test `operation_rate` method.
        """
        # Test operation_rate with variant_type=None
        self.assertAlmostEqual(self.analyzer2.operation_rate(variant_type=None),
                               round(5/6, 4))
        # Test operation_rate with variant_type="M"
        self.assertAlmostEqual(self.analyzer2.operation_rate(variant_type="M"),
                               round(1/6, 4))
        # Test operation_rate with variant_type="S"
        self.assertAlmostEqual(self.analyzer2.operation_rate(variant_type="S"),
                               round(1/6, 4))
        # Test operation_rate with variant_type="U"
        self.assertAlmostEqual(self.analyzer2.operation_rate(variant_type="U"),
                               round(1/6, 4))
        # Test operation_rate with variant_type="O"
        self.assertAlmostEqual(self.analyzer2.operation_rate(variant_type="O"),
                               round(2/6, 4))

# ----------------------------------------------------------------------------
# -------- TEST FRAGMENTATION AND SUMMARY ANALYSIS METHODS -------------------
# ----------------------------------------------------------------------------
class TestFragmentMethods(unittest.TestCase):
    """Test VariantAnalyzer methods (2): fragmentation and analyis summary.
    """
    def setUp(self):
        self.mock_table = Mock(spec=AlignmentTable)
        var_locs = [False, True, False, True, True]
        self.mock_table.columns = [Mock(variant=var_loc) for var_loc in var_locs]
        self.witness1 = ["The", "ground", "truth", "is",      "-", "now"]
        self.witness2 = ["The",      "-", "truht",  "-", "expose", "when"]
        self.mock_table.rows = [
            Mock(header="Witness1", to_list_of_strings=lambda: self.witness1),
            Mock(header="Witness2", to_list_of_strings=lambda: self.witness2),
        ]
        # Create a VariantAnalyzer instance for testing
        self.analyzer = VariantAnalyzer(self.mock_table, language="en", disable_synonym=False)

    def test_fragment_locations(self):
        """Test `fragment_locations` method.
        """
        result = self.analyzer.fragment_locations(self.witness1)
        self.assertTrue(np.array_equal(result, np.array([False, False, False, False, True, False])))

    def test_fragment_locations_matrix(self):
        """Test `fragment_locations_matrix` method.
        """
        result = self.analyzer.fragment_locations_matrix()
        expected_output = np.array([[False, False, False, False,  True, False],
                                    [False,  True, False,  True, False, False]])
        self.assertTrue(np.array_equal(result, expected_output))

    def test_fragment_locations_count(self):
        """Test `fragment_locations_count` method.
        """
        # Test fragment_locations_count method
        result = self.analyzer.fragment_locations_count()
        expected_output = np.array([1, 2])
        self.assertTrue(np.array_equal(result, expected_output))

        # Test fragment_locations_count with normalization
        result = self.analyzer.fragment_locations_count(normalize=True)
        expected_output = np.array([1/6, 1/3])
        self.assertTrue(np.allclose(result, expected_output))

    def test_fragment_rate(self):
        """Test `fragment_rate` method.
        """
        # Test fragment_rate method with strategy="mean"
        expected_output = 1/4 # [(1/6 + 2/6) / 2] = 3/12 = 1/4
        self.assertEqual(self.analyzer.fragment_rate(strategy="mean"),
                         expected_output)
        # Test fragment_rate method with strategy="max" (default)
        expected_output = 1/3 # max(1/6, 2/6) = 2/6 = 1/3
        self.assertAlmostEqual(self.analyzer.fragment_rate(strategy="max"),
                         expected_output, places=4)
        # Test fragment_rate method with unsupported strategy
        with self.assertRaises(ValueError):
            self.analyzer.fragment_rate(strategy="invalid_strategy")

    def test_analysis_summary(self):
        """Test `analysis_summary` method.
        """
        # Test analysis_summary with default parameters
        result = self.analyzer.analysis_summary()
        expected_output = {
            "omit": 3/6,
            "mispell": 1/6,
            "synonym": 0/6,
            "fragment": 1/3, # max
            "undetermined": 1/6
        }
        for key, value in expected_output.items():
            self.assertAlmostEqual(result[key], value, places=4)

        # update disable_synonym
        self.analyzer.disable_synonym = True
        expected_output = {
            "omit": 3/6,
            "mispell": 1/6,
            # "synonym": 0/6,
            "fragment": 1/3, # max
            "undetermined": 1/6
        }
        for key, value in expected_output.items():
            self.assertAlmostEqual(result[key], value, places=4)

        # Test analysis_summary with custom parameters
        result = self.analyzer.analysis_summary(
            include=["omit", "mispell"],
            decimals=2,
            normalize=False, # return count instead of proportion
            missing="-",
            distance="DamerauLevenshtein",
            mispell_cutoff=0.01, # lower distance allowed
            frag_strategy="max"
        )
        expected_output = {
            "omit": 3,
            "mispell": 0
        }
        for key, value in expected_output.items():
            self.assertAlmostEqual(result[key], value)


if __name__ == '__main__':
    unittest.main()
