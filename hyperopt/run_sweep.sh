#!/bin/bash
cd "$(dirname "$0")" # Set CWD to script directory

# We assume that some arguments are "passed" by setting the following environment variables NUM_WORKERS, CORES_PER_WORKER
# Example usage `NUM_WORKERS=16 CORES_PER_WORKER=6 ./run_sweep ../path/to/sweep_config.yml`

SWEEP_CMD=$(wandb sweep $1 2>&1 | tail -1 | cut -c 29-)

echo running sweep with $SWEEP_CMD

CONFIG_NAME=`basename $1 .yml` 
SWEEP_NAME=`echo $SWEEP_CMD | awk -F"/" '{print $NF}'`

GENERATED_SBATCH=`mktemp ${SWEEP_NAME}_${CONFIG_NAME}_XXXX.sbatch -p generated/`

sed -e "s/NUM_WORKERS/${NUM_WORKERS}/g" -e "s;SWEEP_CMD;${SWEEP_CMD};g" -e "s/CORES_PER_WORKER/${CORES_PER_WORKER}/g" wandb_sweep_slurm.sbatch-template > $GENERATED_SBATCH

echo generated sbatch file: $GENERATED_SBATCH
# sbatch ${@:2} $GENERATED_SBATCH

echo $1 $SWEEP_NAME >> sweep_names.txt
