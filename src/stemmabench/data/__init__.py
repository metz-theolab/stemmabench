from pathlib import Path
import json


base_folder = Path(__file__).resolve().parent


# Load synonyms
# TODO: make loading synonyms prettier and more flexible
with open(base_folder / "en_synonyms.json", encoding="utf-8") as f:
    SYNONYM_DICT = {"en": json.load(f)}

# List supported languages
SUPPORTED_LANGUAGES = list(SYNONYM_DICT.keys())
