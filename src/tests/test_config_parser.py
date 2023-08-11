"""Unit tests for the parsing of the configuration.
"""
from pathlib import Path
import unittest
from pydantic import ValidationError

from stemmabench.config_parser import (ProbabilisticConfig, StemmaBenchConfig, 
                                       FragmentationConfig)

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

        # Check for wrongly specified Binomial
        wrong_binomial = {
            "law": "Binomial",
            "min": 1
        }
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_binomial)
        # Check for wrongly specified Poisson
        wrong_poisson = {
            "law": "Poisson",
            "min": 2
        }
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_poisson)

    def test_wrong_fragmentation_rate(self):
        """Check that the proper validation error is raised
        when the fragmentation rate is out of range.
        """
        wrong_fragmentation_rate = {
            "max_rate": 1.5,
            "distribution": {
                "law": "Discrete Uniform"
            }
        }
        wrong_fragmentation_rate2 = {
            "max_rate": -1,
            "distribution": {
                "law": "Discrete Uniform"
            }
        }
        with self.assertRaises(ValidationError):
            FragmentationConfig(**wrong_fragmentation_rate)
        with self.assertRaises(ValidationError):
            FragmentationConfig(**wrong_fragmentation_rate2)


if __name__ == "__main__":
    unittest.main()
