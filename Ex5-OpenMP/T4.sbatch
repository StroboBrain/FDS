#!/bin/bash
#SBATCH --job-name=T4
#SBATCH --partition=xeon
#SBATCH --hint=nomultithread
#SBATCH --time=00:05:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1      
#SBATCH --cpus-per-task=8       
#SBATCH --output=T4.out

module load GCC/14.2.0

gcc -O3 -fopenmp T4_1_sequential.c -o T4_1
gcc -O3 -fopenmp T4_2_parallel.c -o T4_2
gcc -O3 -fopenmp T4_3_parallel.c -o T4_3
gcc -O3 -fopenmp T4_3a_parallel.c -o T4_3a

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

echo "Running T4_1"
srun ./T4_1

echo "Running T4_2"
srun ./T4_2

echo "Running T4_3"
srun ./T4_3

echo "Running T4_3a"
srun ./T4_3a

