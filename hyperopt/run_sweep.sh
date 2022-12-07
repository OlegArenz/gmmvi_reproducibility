#!/bin/bash
cd "$(dirname "$0")" # Set CWD to script directory

# We assume that some arguments are "passed" by setting the following environment variables NUM_WORKERS, CORES_PER_WORKER
# Example usage `NUM_WORKERS=16 CORES_PER_WORKER=6 ./run_sweep ./path/to/sweep_config.yml`

# Start the sweep based on the provided config, and extract the command for starting the worker from stdout
WANDB_MSG=($(wandb sweep "$1" 2>&1))
echo $WANDB_MSG # For checking whether the config had some errors
SWEEP_CMD=${WANDB_MSG[@]: -3}
echo running sweep with $SWEEP_CMD

# Get the ID for this sweep (last part of the command for starting the worker)
SWEEP_NAME=`echo $SWEEP_CMD | awk -F"/" '{print $NF}'`

# Create a temporary slurm script by modifying the template
CONFIG_NAME=`basename "$1" .yml`
GENERATED_SBATCH=`mktemp ${SWEEP_NAME}_${CONFIG_NAME}_XXXX.sbatch -p generated/`
sed -e "s/NUM_WORKERS/${NUM_WORKERS}/g" -e "s;SWEEP_CMD;${SWEEP_CMD};g" -e "s/CORES_PER_WORKER/${CORES_PER_WORKER}/g" wandb_sweep_slurm.sbatch-template > $GENERATED_SBATCH

# Start the workers
echo generated sbatch file: $GENERATED_SBATCH
sbatch ${@:2} $GENERATED_SBATCH

# Also store the name of the sweep, so that we can use it later on for retrieving the correct sweep
echo $1 $SWEEP_NAME >> sweep_names.txt
