"""Unit tests for the stemma generator.
"""
import unittest
import os
import shutil
from pathlib import Path

import numpy as np
from stemmabench.config_parser import StemmaBenchConfig
from stemmabench.stemma_generator import Stemma

TEST_YAML = Path(__file__).resolve().parent / "test_data" / "config.yaml"
OUTPUT_FOLDER = "output_folder"

class TestStemmaGenerator(unittest.TestCase):
    """Unit tests for the stemma generator.
    """
    def setUp(self):
        """Set-up the data to test the generation.
        """
        self.text = """
        love bade  welcome yet my soul hrew back guilty of dust ajd sin."""
        config = StemmaBenchConfig.from_yaml(TEST_YAML)
        self.stemma = Stemma(
            original_text=self.text,
            config=config,
            random_state=10
        )
        # Create the output folder
        os.mkdir(OUTPUT_FOLDER)


    def tearDown(self):
        """Clean up by deleting the output folder and its contents.
        """
        if os.path.exists(OUTPUT_FOLDER):
            shutil.rmtree(OUTPUT_FOLDER)


    def test_get_width(self):
        """Tests that getting the width of the tree behaves as expected.
        """
        np.random.seed(10)
        self.assertEqual(self.stemma.width, 3)


    def test_generate(self):
        """Tests that generating the stemma behaves as expected.
        """
        # Test if stemma generation works well.
        print(self.stemma.generate())
        # Sanity check for the number of manuscripts.
        width_min = self.stemma.config.stemma.width.min
        width_max = self.stemma.config.stemma.width.max - 1
        depth = self.stemma.depth
        nbr_mss_max = (1 - width_max**(depth + 2)) / (1 - width_max)
        nbr_mss_min = (1 - width_min**(depth + 2)) / (1 - width_min)
        self.assertTrue(
            nbr_mss_min <= len(self.stemma.texts_lookup) <= nbr_mss_max
        )


    def test_apply_level(self):
        """Tests that applying on a single level behaves as expected.
        """
        expected_result = [
            'Love bade welcome yet oy soul hrew back hangdog of dust bjd sin.',
            'love bade welcome yet my soulfulness hrew back guilty of dust ajd .', 
            'love bade welcome yet my soul hbew back guilty of dust ajd sin.'
        ]
        np.random.seed(10)
        self.assertListEqual(
            self.stemma._apply_level(self.text),
            expected_result
        )


    def test_graph_repr(self):
        """Tests that representation as a graph works as expected.
        """

    def test_apply_fragmentation(self):
        """_summary_
        """


    def test_dict(self):
        """Tests the dict representation of the stemma.
        """
        generated_stemma = self.stemma.generate()
        stemma_dict = generated_stemma.dict()
        # Check if the dictionary is a non-empty dict
        self.assertIsInstance(stemma_dict, dict)
        self.assertGreater(len(stemma_dict), 0)
        self.assertIn(self.text, stemma_dict)

    def test_missing_manuscripts(self):
        """Tests the missing_manuscripts method.
        """
        # Generate the stemma
        generated_stemma = self.stemma.generate()

        # Call the missing_manuscripts method
        mss_non_missing, edges_non_missing = generated_stemma.missing_manuscripts()

        # Check if the selected missing manuscripts are not present in edge.
        for mss in generated_stemma.texts_lookup:
            if mss not in mss_non_missing:
                for edge in edges_non_missing:
                    self.assertNotIn(mss, edge)

        # Check if the returned data is of the correct types
        self.assertIsInstance(mss_non_missing, dict)
        self.assertIsInstance(edges_non_missing, list)

        # Calculate the expected number of missing manuscripts based on the configured rate
        total_manuscripts = len(generated_stemma.texts_lookup)
        configured_rate = generated_stemma.missing_manuscripts_rate
        expected_missing_count = int(configured_rate * total_manuscripts)
        # Check if the number of missing manuscripts matches the expected count
        actual_missing_count = total_manuscripts - len(mss_non_missing)
        self.assertEqual(actual_missing_count, expected_missing_count)


    def test_dump(self):
        """Tests the dump method and checks the generated folder and files.
        """
        # Generate the stemma and dump it
        generated_stemma = self.stemma.generate()
        generated_stemma.dump(OUTPUT_FOLDER)

        # Check if the output folder exists
        self.assertTrue(os.path.exists(OUTPUT_FOLDER))
        self.assertTrue(os.path.isdir(OUTPUT_FOLDER))

        # Check if all files in the folder have the ".txt" extension
        for filename in os.listdir(OUTPUT_FOLDER):
            file_path = os.path.join(OUTPUT_FOLDER, filename)
            if os.path.isfile(file_path):  # Check if it's a file (not a folder)
                self.assertTrue(filename.endswith(".txt"))

        # Check that the "edges.txt" file exists in the folder
        edges_file_path = os.path.join(OUTPUT_FOLDER, "edges.txt")
        self.assertTrue(os.path.exists(edges_file_path))

        # Check that a subfolder "missing_manuscripts" is created
        missing_manuscripts_folder = os.path.join(OUTPUT_FOLDER, "missing_tradition")
        self.assertTrue(os.path.exists(missing_manuscripts_folder))
        self.assertTrue(os.path.isdir(missing_manuscripts_folder))



if __name__ == "__main__":
    unittest.main()
