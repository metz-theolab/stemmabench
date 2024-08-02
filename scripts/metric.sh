#!/bin/bash
#OAR -n run_algo_stemma
#OAR -l /nodes=1/cpu=1,walltime=01:30:00
#OAR --stdout metric.%jobid%.stdout
#OAR --stderr metric.%jobid%.stderr
#OAR --project pr-stemmabench

source /applis/environments/conda.sh
conda activate env-stemmabench


for dir in /silenus/PROJECTS/pr-stemmabench/COMMON/*; do
  echo $dir
  if [ -d "$dir" ]; then
    if [ -d "$dir/resultat" ]; then
      echo "Skipping $dir because 'resultat' already exists."
      continue
    fi

    cd "$dir" || continue
    mkdir resultat
    cd resultat

    generation_dir="../generation"
    
    if [ -d "$generation_dir" ]; then
      for file in "$generation_dir"/edges_* "$generation_dir"/rhm-*; do
        if [ -f "$file" ]; then
          file_name=$(basename "$file")
          python3 ./tree_metrics.py \
            "../generation/edges.txt" "$file" "result_${dir##*/}_${file_name}.txt"
        fi
      done
    fi

    # Revenir au dossier parent
    cd ../..
  fi
done
