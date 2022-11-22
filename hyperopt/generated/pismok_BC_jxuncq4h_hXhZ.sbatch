#!/bin/bash
#SBATCH -A project01883
#SBATCH -J wandb_sweep
# Please use the complete path details :
#SBATCH -o /work/scratch/j_arenz/wandb_sweeps/slurmlog/out_%A_%a.log
#SBATCH -e /work/scratch/j_arenz/wandb_sweeps/slurmlog/err_%A_%a.log
# Cluster Settings
#SBATCH -n 16         # Number of workers
#SBATCH -c 6  # Number of cores per worker
#SBATCH -t 0-12:00:00           # 1:00:00 Hours, minutes and seconds, or '#SBATCH -t 10' - only minutes
#SBATCH --mem-per-cpu=3800
#SBATCH -C avx512
#SBATCH --exclusive
# -------------------------------
# Load the required modules
module purge
module load gcc python/3.8

# Activate the virtualenv / conda environment
source ~/virtualenvs/gmmvi_test/bin/activate

# Run on SLURM
cd $HOME/src/gmmvi_test

# Start 16 Workers
count=16
for i in $(seq $count); do
    srun -c6  wandb agent joa/SteinVIPS/jxuncq4h &
done

wait
