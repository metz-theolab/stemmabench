"""Unit tests for the parsing of the configuration.
"""
from pathlib import Path
import unittest
from pydantic import ValidationError

from stemmabench.config_parser import ProbabilisticConfig, StemmaBenchConfig, VariantConfig

TEST_YAML = Path(__file__).resolve().parent / "test_data" / "config.yaml"


class TestBenchConfigParser(unittest.TestCase):
    """Unit tests for the configuration parser.
    """

    def setUp(self):
        """Setup the test by loading the test YAML file.
        """
        self.test_config = StemmaBenchConfig.from_yaml(TEST_YAML)

    def test_wrong_law_specification(self):
        """Check that the proper validation errors are raised
        when the specifications of the probabilistic law are wrong.
        """
        # Check for wrongly specified Bernouilli
        wrong_bernouilli = {
            "law": "Bernouilli",
            "min": 3
        }
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_bernouilli)
        # Check for wrongly specified Uniform
        wrong_uniform = {
            "law": "Uniform",
            "rate": .3
        }
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_uniform)
        # Check for wrongly specified Gaussian
        wrong_gaussian = {
            "law": "Gaussian",
            "rate": .3
        }
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_gaussian)


if __name__ == "__main__":
    unittest.main()
