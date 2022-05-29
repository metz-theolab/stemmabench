"""Unit tests for the stemma generator.
"""

import unittest
from pathlib import Path
import random
from stemmabench.config_parser import StemmaBenchConfig
from stemmabench.stemma_generator import Stemma

TEST_YAML = Path(__file__).resolve().parent / "test_data" / "config.yaml"


class TestStemmaGenerator(unittest.TestCase):
    """Unit tests for the stemma generator.
    """

    def setUp(self):
        """Set-up the data to test the generation.
        """
        self.text = """
        Love bade me welcome; yet my soul drew back, Guilty of dust and sin."""
        config = StemmaBenchConfig.from_yaml(TEST_YAML)
        self.stemma = Stemma(
            original_text=self.text,
            config=config
        )

    def test_get_width(self):
        """Tests that getting the width of the tree behaves as expected.
        """
        random.seed(10)
        self.assertEqual(self.stemma.width, 3)

    def test_generate(self):
        """Tests that generating the stemma behaves as expected.
        """
        print(self.stemma.generate())

    def test_apply_level(self):
        """Tests that applying on a single level behaves as expected.
        """
        random.seed(10)
        self.assertListEqual(
            self.stemma._apply_level(self.text),
            ['love bade me welcome so_far my soul draw second guilty of dust and mark_of_cain.',
                'love bade maine welcome yet my suul drew back guilty of dust and sin.',
                'love bade me welcome yet my soul absorb rear  of bust and siq.']
        )

    def test_graph_repr(self):
        """Tests that representation as a graph works as expected.
        """


if __name__ == "__main__":
    unittest.main()
