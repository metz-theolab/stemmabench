# StemmaBench

StemmaBench is a Python package for quick generation of artificial, synthetic scribal traditions. From an original text, it generates a series of witnesses based on a set of variable aiming at describing the different scribal behaviors.

## Motivation and theory

## Quickstart

Installation can be done through `invoke`:

`pip install invoke`

`invoke install`

### Command line

A possible way to generate a tradition is running the `generate` command:

```bash
generate --help
Usage: generate [OPTIONS] INPUT_TEXT OUTPUT_FOLDER CONFIGURATION

  Generate a tradition of manuscripts.

  Args:     input_text (str): The text to give as input for the tradition.
  output_folder (str): The output folder for the tradition.     configuration
  (str): The configuration of the tradition.

Arguments:
  INPUT_TEXT     [required]
  OUTPUT_FOLDER  [required]
  CONFIGURATION  [required]
```

For example:
`generate .\test_text.txt output_folder .\config.yaml`

with `config.yaml` being:

```yaml
meta:
  language: eng

variants:
  words:
    synonym:
      law: Bernouilli
      rate: 0.1
    hyponym:
      law: Bernouilli
      rate: 0.1
    hypernym:
      law: Bernouilli
      rate: 0.1
    mispell:
      law: Bernouilli
      rate: 0.05
    omit:
      law: Bernouilli
      rate: 0.05
  sentences:
    duplicate:
      args:
        nbr_words: 2
      law: Bernouilli
      rate: 0.1

stemma:
  depth: 2
  width:
    law: Uniform
    min: 2
    max: 4
```

### Interactive use

See: ["./docs/quickstart.ipynb"]

## To do list

[] Add support for ancient languages (greek, hebrew mainly) => Will be done through using MACULA API
[] Add the possibility to work with contamination
[] Add support for missing manuscripts (new variable in stemma generation that will skip generations)
[] Make vizualization more resiliant + a whole part of the package
