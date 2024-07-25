#!/bin/bash

#OAR -n run_algo_stemma
#OAR -l /nodes=2/cpu=2,walltime=6:00:00
#OAR --stdout scenario.%jobid%.stdout
#OAR --stderr scenario.%jobid%.stderr
#OAR --project pr-stemmabench

source /applis/environments/conda.sh
conda activate env-stemmabench

# Parcourir tous les dossiers de la forme sc*
for dir in sc*; do
  if [ -d "$dir" ]; then
    # Aller dans le dossier generation
    cd "$dir/generation" || continue

    # Vérifier si le dossier missing_tradition existe
    if [ -d "missing_tradition" ]; then
      # Parcourir les fichiers .txt dans missing_tradition
      for file in missing_tradition/*.txt; do
        basefile=$(basename "$file")
        # Vérifier si le fichier existe également dans le dossier parent (generation)
        if [ -f "$basefile" ]; then
          # Supprimer le fichier en double dans generation
          rm "$basefile"
        fi
    done

      # Déplacer le dossier missing_tradition dans le dossier de base
      mv missing_tradition ../
    fi
    python /home/chausser/dev/stemmabench/scripts/computation.py ~/prod/$dir/generation/
    while [ ! -f ~/prod/$sc_dir/generation/edges_NJ_Dist_inverse_jaccard.txt ]; do
        sleep 1
    done
    # Revenir au dossier de base
    cd ../..
  fi
done
