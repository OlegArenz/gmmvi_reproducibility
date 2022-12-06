#!/bin/bash
cd "$(dirname "$0")" # Set CWD to script directory 

NUM_WORKERS=16
CORES_PER_WORKER=6

for fname in "configs/experiments/exp2 (multimodal targets)/gmm20"/*.yml
do
  NUM_WORKERS=$NUM_WORKERS CORES_PER_WORKER=$CORES_PER_WORKER ./run_sweep.sh "$fname" -t 1-00:00:00
  sleep 1s
done

