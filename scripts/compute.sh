#!/bin/bash

#OAR -n run_algo_stemma
#OAR -l /nodes=2/cpu=2,walltime=00:30:00
#OAR --stdout scenario.%jobid%.stdout
#OAR --stderr scenario.%jobid%.stderr
#OAR --project pr-stemmabench

#CHECK chose path on cp line 33 and paste it on metric.sh line 12

source /applis/environments/conda.sh
conda activate env-stemmabench

sc_dirs=($(find . -maxdepth 1 -type d))
for dir in "${sc_dirs[@]}"; do
  if [ -d "$dir" ]; then
    echo "Dir : $dir"
    cd "$dir/generation" || continue

    if [ -d "missing_tradition" ]; then
      for file in missing_tradition/*.txt; do
        basefile=$(basename "$file")
        if [ -f "$basefile" ]; then
          rm "$basefile"
        fi
    done

      mv missing_tradition ../ || continue
    fi
    echo "Path compute : ./$dir/generation/"
    python ./computation.py ./$dir/generation/
    cd ../..
    cp -r ./$dir /silenus/PROJECTS/pr-stemmabench/COMMON
    rm -r ./$dir
  fi
done
