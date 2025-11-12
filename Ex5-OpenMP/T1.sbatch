#!/bin/bash
#SBATCH --job-name=T1    # The name of the job
#SBATCH --partition=xeon     # The main partition of miniHPC
#SBATCH --hint=nomultithread # Disable hardware multithreading
#SBATCH --exclusive          # Exclusive access to resources
#SBATCH --time=00:10:00      # Requested execution time
#SBATCH --nodes=1            # Requested number of nodes
#SBATCH --ntasks-per-node=1  # Requested processes per node
#SBATCH --cpus-per-task=1    # Requested threads per process
#SBATCH --output=T1.out

#module load GCC/14.2.0
#gcc -O3 -fopenmp hostname_task1.c -o hostname_task1

#export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

srun hostname