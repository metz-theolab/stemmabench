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
        wrong_uniform_parametre = {
            "law": "Uniform",
            "rate": .3
        }
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_uniform_parametre)

        wrong_uniform_min_max = {
            "law": "Uniform",
            "min": 5,
            "max": 3
        }
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_uniform_min_max)
            
        # Check for wrongly specified Gaussian
        wrong_gaussian_parameter = {
            "law": "Gaussian",
            "rate": .3
        }
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_gaussian_parameter)
        

        # Check for wrongly specified Gaussian
        wrong_gaussian_sd = {
            "law": "Gaussian",
            "mean": 2,
            "sd": -1
        }
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_gaussian_sd)

        wrong_poisson_parameter = {
            "law": "Poisson",
            "rate": .5
        }
        # Check for wrongly specified Poisson
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_poisson_parameter)

        wrong_poisson_negative = {
            "law": "Poisson",
            "lambda_": -8
        }
                # Check for wrongly specified Poisson
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_poisson_negative)

        wrong_binomial = {
            "law": "Binomial",
            "min": 0.5,
        }
        # Check for wrongly specified Binomial
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_binomial)

        wrong_binomial_n = {
            "law": "Binomial",
            "rate": 0.5,
            "n": -2
        }
        # Check for wrongly specified Binomial
        with self.assertRaises(ValidationError):
            ProbabilisticConfig(**wrong_binomial_n)



if __name__ == "__main__":
    unittest.main()
