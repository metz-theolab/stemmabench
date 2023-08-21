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
    DISCRETE_UNIFORM: str = "Discrete Uniform"
    BERNOUILLI: str = "Bernouilli"
    BINOMIAL: str = "Binomial"
    GAUSSIAN: str = "Gaussian"
    UNIFORM: str = "Uniform"
    POISSON: str = "Poisson"


class ProbabilisticConfig(BaseModel):
    """Model describing the configuration of a probabilistic law.
    """
    law: ProbabilisticLaw
    rate: Optional[float]
    min: Optional[float]
    max: Optional[float]
    mean: Optional[float]
    sd: Optional[float]
    n: Optional[int]
    args: Dict[str, Any] = {}

    @root_validator(pre=True)
    def check_law_parameters(cls, values):
        """Check that depending on the selected law, the
        right parameters are given as input.
        """
        if values["law"] in ("Bernouilli", "Binomial", "Poisson"):
            if not ("rate" in values):
                raise ValidationError("You asked for Bernouilli, Binomial or"
                                      "Poisson law but did not provide a rate "
                                      "value")
        elif values["law"] == "Uniform":
            if not (("min" in values) and ("max" in values)):
                raise ValidationError("You asked for Uniform "
                                      "law but did not provide "
                                      "a min and a max value")
        elif values["law"] == "Gaussian":
            if not (("mean" in values) and ("sd" in values)):
                raise ValidationError("You asked for Gaussian "
                                      "law but did not provide "
                                      "a mean and sd value")
        return values


class FragmentationConfig(BaseModel):
    """Model describing the configuration of a fragmentation operation.
    """
    max_rate: float
    distribution: ProbabilisticConfig

    @root_validator(pre=True)
    def check_fragmentation_rate(cls, values):
        """Check that the maximum fragmenation rate is between 0 and 1.
        """
        if not 0 <= values["max_rate"] <= 1:
            raise ValueError(
                "Maximum fragmentation rate should be between 0 and 1."
            )
        return values


class TextConfig(BaseModel):
    """Model describing the configuration of operations on text.
    """
    fragmentation: FragmentationConfig
    # Contamination: ContaminationConfig ???


class VariantConfig(BaseModel):
    """Model describing the configuration of the different variants.
    """
    words: Dict[str, ProbabilisticConfig]
    sentences: Dict[str, ProbabilisticConfig]
    texts: TextConfig


class StemmaConfig(BaseModel):
    """Model describing the configuration of the stemma.
    """
    depth: int
    width: ProbabilisticConfig
    missing_manuscripts: ProbabilisticConfig
    fragmentation_proba: float

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
