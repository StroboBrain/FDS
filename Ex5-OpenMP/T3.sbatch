#!/bin/bash
#SBATCH --job-name=T3
#SBATCH --partition=xeon
#SBATCH --hint=nomultithread
#SBATCH --time=00:05:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1      
#SBATCH --cpus-per-task=1        
#SBATCH --output=T3_%j.out

module load GCC/14.2.0

gcc -O3 -fopenmp T3.c -o T3

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

srun ./T3
