#!/bin/bash
cd "$(dirname "$0")" # Set CWD to script directory 

NUM_WORKERS=16
CORES_PER_WORKER=6
for fname in `ls "configs/experiments/exp1 (update stability for single gaussians)/breast_cancer/"`; do ./run_sweep.sh $fname; sleep 1s ; done

