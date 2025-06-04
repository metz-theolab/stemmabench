#OAR -n benchmarking
#OAR -l /nodes=1/cpu=1,walltime=04:00:00
#OAR --stdout scenario.%jobid%.stdout
#OAR --stderr scenario.%jobid%.stderr
#OAR --project pr-stemmabench

source /applis/environments/conda.sh
conda activate env-stemmabench

python /home/chausser/dev/stemmabench/scripts/generate_yaml.py "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9$ "${10}" "${11}"
