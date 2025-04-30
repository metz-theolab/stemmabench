from pathlib import Path
import json
from itertools import chain
from string import ascii_lowercase


base_folder = Path(__file__).resolve().parent


# Load synonyms
SUPPORTED_LANGUAGES = ["en","gr"]

SYNONYM_DICT = {}
for language in SUPPORTED_LANGUAGES:
    with open(base_folder / f"{language}_synonyms.json", encoding="utf-8") as f:
        SYNONYM_DICT[language] = json.load(f)

# Load letters depending on language
LETTERS ={"gr": ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω'],
          "en": ascii_lowercase}