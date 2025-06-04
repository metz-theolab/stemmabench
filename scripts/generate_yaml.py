import os
import json
from jinja2 import Environment, FileSystemLoader
from stemmabench.bench.stemma_generator import Stemma

class TemplateBuilder:
    def __init__(self, rate_mispell, rate_synonym, rate_omit, rate_duplicate, n_duplicate, specific_rate, name):
        self.rate_mispell = rate_mispell
        self.rate_synonym = rate_synonym
        self.rate_omit = rate_omit
        self.rate_duplicate = rate_duplicate
        self.n_duplicate = n_duplicate
        self.specific_rate = specific_rate
        self.name = name
        self.env = Environment(loader=FileSystemLoader(os.getcwd()))
    
    def build_template(self):
        template_content = """\
meta:
  language: {{ meta.language }}

variants:
  letters:
    mispell:
      law: {{ variants.letters.mispell.law }}
      rate: {{ variants.letters.mispell.rate }}
      {% if variants.letters.mispell.args.specific_rates %}
      args:
        specific_rates:
          {% for letter, rates in variants.letters.mispell.args.specific_rates.items() %}
          {{ letter }}:
            {% for key, value in rates.items() %}
            {{ key }}: {{ value }}
            {% endfor %}
          {% endfor %}
      {% endif %}

  words:
    synonym:
      law: {{ variants.words.synonym.law }}
      rate: {{ variants.words.synonym.rate }}
    omit:
      law: {{ variants.words.omit.law }}
      rate: {{ variants.words.omit.rate }}

  sentences:
    duplicate:
      args:
        nbr_words: {{ variants.sentences.duplicate.args.nbr_words }}
      law: {{ variants.sentences.duplicate.law }}
      rate: {{ variants.sentences.duplicate.rate }}

stemma:
  depth: {{ stemma.depth }}
  width:
    law: {{ stemma.width.law }}
    min: {{ stemma.width.min }}
    max: {{ stemma.width.max }}
  missing_manuscripts:
    law: {{ stemma.missing_manuscripts.law }}
    rate: {{ stemma.missing_manuscripts.rate }}
"""
        template_file_path = f'./{self.name}.yaml.j2'
        with open(template_file_path, 'w') as file:
            print(f"Writing file {template_file_path}")
            file.write(template_content)
        return template_file_path

    def build_scenario(self,text,name, depth_max, width_max,missing_max):
        template_file_path = self.build_template()
        template = self.env.get_template(os.path.basename(template_file_path))

        for missing in range(0, missing_max+1):
            for width in range(1, width_max+1):
                for depth in range(2, depth_max+1):
                    scenario_name = f'{name}_depth{depth}_width{width}_missing{missing}'
                    scenario_dir = os.path.join(os.getcwd(), scenario_name)
                    os.makedirs(scenario_dir, exist_ok=True)

                    missing_rate = round(0.1 * missing, 3)
                    data = {
                        'meta': {
                            'language': 'en'
                        },
                        'variants': {
                            'letters': {
                                'mispell': {
                                    'law': 'Bernouilli',
                                    'rate': self.rate_mispell,
                                    'args': {
                                        'specific_rates': self.specific_rate if self.specific_rate else {}
                                    }
                                }
                            },
                            'words': {
                                'synonym': {
                                    'law': 'Bernouilli',
                                    'rate': self.rate_synonym
                                },
                                'omit': {
                                    'law': 'Bernouilli',
                                    'rate': self.rate_omit
                                }
                            },
                            'sentences': {
                                'duplicate': {
                                    'args': {
                                        'nbr_words': self.n_duplicate
                                    },
                                    'law': 'Bernouilli',
                                    'rate': self.rate_duplicate
                                }
                            }
                        },
                        'stemma': {
                            'depth': depth,
                            'width': {
                                'law': 'Uniform',
                                'min': 2,
                                'max': width
                            },
                            'missing_manuscripts': {
                                'law': 'Bernouilli',
                                'rate': missing_rate
                            }
                        }
                    }

                    output_from_parsed_template = template.render(data)
                    output_file_path = os.path.join(scenario_dir, f'{scenario_name}.yaml')
                    with open(output_file_path, 'w') as yaml_file:
                        yaml_file.write(output_from_parsed_template)
                    stemma = Stemma(path_to_text=text,
                                        config_path=output_file_path)
                    stemma.generate()
                    stemma.dump(folder="./"+scenario_name+"/generation")

                    print(f"Text generation OK!")

        return 0

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 12:
        print("Usage: python script.py <rate_mispell> <rate_synonym> <rate_omit> <rate_duplicate> <n_duplicate> <specific_rate> <name> <text> <depth> <width> <missing>")
        sys.exit(1)

    rate_mispell = float(sys.argv[1])
    rate_synonym = float(sys.argv[2])
    rate_omit = float(sys.argv[3])
    rate_duplicate = float(sys.argv[4])
    n_duplicate = int(sys.argv[5])
    specific_rate = None if sys.argv[6].lower() == 'none' else json.loads(sys.argv[6])
    name = sys.argv[7]
    text = sys.argv[8]
    depth = sys.argv[9]
    width = sys.argv[10]
    missing = sys.argv[11]
    

    builder = TemplateBuilder(rate_mispell, rate_synonym, rate_omit, rate_duplicate, n_duplicate, specific_rate, name)
    builder.build_scenario(text,name, depth, width,missing)