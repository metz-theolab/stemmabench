"""Module for parsing of the configuration file from a YAML file
into a pydantic model.
"""
from pathlib import Path
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, ValidationError, root_validator
import yaml


class ProbabilisticLaw(str, Enum):
    """Enumeration of the implemented probabilistic laws.
    """
    Bernouilli: str = "Bernouilli"
    Gaussian: str = "Gaussian"
    Uniform: str = "Uniform"
    Poisson: str = "Poisson"
    Binomial: str = "Binomial"


class ProbabilisticConfig(BaseModel):
    """Model describing the configuration of a probabilistic law.
    """
    law: ProbabilisticLaw
    rate: Optional[float]
    min: Optional[float]
    max: Optional[float]
    mean: Optional[float]
    sd: Optional[float]
    lambda_: Optional[float]
    n: Optional[float]
    args: Dict[str, Any] = {}

    @root_validator(pre=True)
    def check_law_parameters(cls, values):
        """Check that depending on the selected law, the
        right parameters are given as input.
        """
        if values["law"] == "Bernouilli":
            if not ("rate" in values):
                raise ValidationError("You asked for Bernouilli"
                                      "law but did not provide a rate value")
        elif values["law"] == "Uniform":
            if not (("min" in values) and ("max" in values)):
                raise ValidationError("You asked for Uniform "
                                      "law but did not provide "
                                      "a min and a max value")
            if (values["min"] > values["max"]):
                raise ValidationError("In a uniform distribution"
                                      "the maximum must be greater than the minimum"
                                      )
        elif values["law"] == "Gaussian":
            if not (("mean" in values) and ("sd" in values)):
                raise ValidationError("You asked for Gaussian "
                                      "law but did not provide "
                                      "a mean and sd value")
            if values["sd"] < 0:              
                raise ValidationError("Gaussian law"
                                      "requires a positive standard deviation value")
            
        elif values["law"] == "Poisson":
            if not ("lambda_" in values):
                raise ValidationError("You asked for Poisson"
                                      "Law but did not provide a lambda value")
            if (values["lambda_"] < 0):
                raise ValidationError("Poisson law "
                                      "requires a positive lambda value")
        
        elif values["law"] == "Binomial":
            if not (("rate" in values) and ("n" in values)):
                raise ValidationError("You asked for Binomial"
                                      "Law but did not provide a n or rate value")
            if (values["n"] <= 0):
                raise ValidationError("Binomial law"
                                "requires a positive value for n")
        return values


class VariantConfig(BaseModel):
    """Model describing the configuration of the different variants.
    """
    words: Dict[str, ProbabilisticConfig]
    sentences: Dict[str, ProbabilisticConfig]


class StemmaConfig(BaseModel):
    """Model describing the configuration of the stemma.
    """
    depth: int
    width: ProbabilisticConfig
    missing_manuscripts: ProbabilisticConfig


class MetaConfig(BaseModel):
    """Model describing the configuration of the language.
    """
    language: str


class StemmaBenchConfig(BaseModel):
    """Parser for the Stemma bench config.
    """
    meta: MetaConfig
    variants: VariantConfig
    stemma: StemmaConfig

    @classmethod
    def from_yaml(cls, yaml_file: str):
        """Load the configuration from a YAML file.

        Args:
            yaml_file (str): Path to the Yaml file.

        Returns:
            StemmaBenchConfig: The parsed object.
        """
        return cls(**yaml.load(Path(yaml_file).read_text(),
                               Loader=yaml.SafeLoader))
