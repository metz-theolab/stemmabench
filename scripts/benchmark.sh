#!/bin/bash
set -e
#FIX ME fix argument parsing
#EDIT path scripts stemmabench
bash "/home/chausser/dev/stemmabench/scripts/generate.sh" $1 $2 $3 $4 $5 $6 $7 $8 $9 ${10} ${11}
bash "/home/chausser/dev/stemmabench/scripts/compute.sh"
bash "/home/chausser/dev/stemmabench/scripts/metric.sh"
