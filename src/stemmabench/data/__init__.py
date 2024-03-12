from pathlib import Path
import json
from itertools import chain
from string import ascii_lowercase


base_folder = Path(__file__).resolve().parent


# Load synonyms
SUPPORTED_LANGUAGES = ["en","gr","gr_diacritic"]

SYNONYM_DICT = {}
for language in SUPPORTED_LANGUAGES:
    with open(base_folder / f"{language}_synonyms.json", encoding="utf-8") as f:
        SYNONYM_DICT[language] = json.load(f)

# Greek alphabet
greek_alphabet = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']

# Greek alphabet with diacritics signs
greek_diacritic = greek_alphabet + [
    'ἀ','ἁ','ἂ','ἃ','ἄ','ἅ',
    'ἐ', 'ἑ', 'ἒ','ἓ','ἔ','ἕ',
    'ἠ','ἡ','ἢ','ἣ','ἤ','ἥ',
    'ἰ', 'ἱ',
    'ὰ','ά','ὲ','έ','ὴ','ή','ὶ','ί','ὸ','ό','ὺ','ύ','ὼ','ώ',
    'ὀ', 'ὁ',
    'ὐ','ὑ',
    'ὠ', 'ὡ',
    'ὴ',
    'ᾐ','ᾑ',
    'ᾠ', 'ᾡ']

# Load letters depending on language
LETTERS ={"gr": greek_alphabet,
          "gr_diactritic": greek_diacritic,
          "en": ascii_lowercase}