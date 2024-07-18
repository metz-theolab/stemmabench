import os

from jinja2 import Environment, FileSystemLoader

# Définir le répertoire contenant le template
template_dir = '/home/chausser/test/'



# Configuration de Jinja2 pour charger le template
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template('scenario5.yaml.j2')
for missing in range(1,7):
    for width in range(1,9):
        for depth in range(2,11):
            name = 'scenario_1_depth'+str(depth)+'_width'+str(width)+'_missing'+str(missing)
            # Les données à insérer dans le template
            missing_rate = 0.1*missing
            missing_rate = round(missing_rate,3)
            data = {
                'meta': {
                    'language': 'en'
                },
                'variants': {
                    'letters': {
                        'mispell': {
                            'law': 'Bernouilli',
                            'rate': 0.05,
                            'args': {
                                'specific_rates': {
                                    'a': {
                                        'o': 0.05
                                    },
                                    'o': {
                                        'a': 0.05
                                    },
                                    'm': {
                                        'n': 0.05
                                    },
                                    'n': {
                                        'm': 0.05
                                    }
                                }
                            }
                        }
                    },
                    'words': {
                        'synonym': {
                            'law': 'Bernouilli',
                            'rate': 0.03
                        },
                        'omit': {
                            'law': 'Bernouilli',
                            'rate': 0.01
                        }
                    },
                    'sentences': {
                        'duplicate': {
                            'args': {
                                'nbr_words': 2
                            },
                            'law': 'Bernouilli',
                            'rate': 0.05
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
                
            # Rendu du template avec les données
            output_from_parsed_template = template.render(data)
            os.mkdir("/home/chausser/scenario5/")
            os.mkdir("/home/chausser/scenario5/"+name)
            # Sauvegarder le rendu dans un fichier YAML
            output_file = "/home/chausser/scenario5/"+name+"/"+name+".yaml"
            with open(output_file, 'w') as yaml_file:
                yaml_file.write(output_from_parsed_template)
            print(f"Fichier YAML généré avec succès : {output_file}")