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

    def test_wrong_law_bernouilli(self):
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

    def test_wrong_law_uniform(self):
        # Check for wrongly specified Uniform
        wrong_uniform = {
            "law": "Uniform",
            "rate": .3
        }
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_uniform)
            
    def test_wrong_law_gaussian(self):
        # Check for wrongly specified Gaussian
        wrong_gaussian = {
            "law": "Gaussian",
            "rate": .3
        }
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_gaussian)
        
    def test_wrong_law_poisson(self):
        wrong_poisson = {
            "law": "Poisson",
            "rate": .5
        }
        # Check for wrongly specified Poisson
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_poisson)

    def test_wrong_law_binomial(self):
        """Check that the proper validation errors are raised
        when the specifications of the probabilistic law are wrong."""
        wrong_binomial = {
            "law": "Binomial",
            "min": 0.5,
        }
        # Check for wrongly specified Binomial
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_binomial)

    def test_wrong_uniform_parameter(self):
        """Check that the proper validation errors are raised
        when the specifications of the probabilistic law are wrong."""
        wrong_uniform_min_max = {
            "law": "Uniform",
            "min": 5,
            "max": 3
        }
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_uniform_min_max)

    def test_wrong_gaussian_parameter(self):
        """Check that the proper validation errors are raised
        when the specifications of the probabilistic law are wrong."""
        wrong_gaussian_sd = {
            "law": "Gaussian",
            "mean": 2,
            "sd": -1
        }
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_gaussian_sd)
    
    def test_wrong_poisson_parameter(self):
        """Check that the proper validation errors are raised
        when the specifications of the probabilistic law are wrong."""
        wrong_poisson_negative = {
            "law": "Poisson",
            "lambda_": -6
        }
        # Check for wrongly specified Poisson
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_poisson_negative)
    
    def test_wrong_binomial_parameter(self):
        """Check that the proper validation errors are raised
        when the specifications of the probabilistic law are wrong."""
        wrong_binomial_parametre = {
            "law": "Binomial",
            "rate": 0.5,
            "n": -2
        }
        # Check for wrongly specified Binomial
        with self.assertRaises(ValueError):
            ProbabilisticConfig(**wrong_binomial_parametre)
        


if __name__ == "__main__":
    unittest.main()
