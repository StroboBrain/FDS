#!/bin/bash
#SBATCH --job-name=T5
#SBATCH --partition=xeon
#SBATCH --hint=nomultithread
#SBATCH --time=00:05:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1      
#SBATCH --cpus-per-task=16       
#SBATCH --output=T5.out

module load GCC/14.2.0

gcc -O3 -fopenmp T4_2_parallel.c -o T4_2


export OMP_NUM_THREADS=1

echo "========================================="
echo "Running T4_2_parallel with 1 OpenMP threads"
echo "========================================="
srun ./T4_2

export OMP_NUM_THREADS=2
echo "========================================="
echo "Running T4_2_parallel with 2 OpenMP threads"
echo "========================================="
srun ./T4_2

export OMP_NUM_THREADS=4
echo "========================================="
echo "Running T4_2_parallel with 4 OpenMP threads"
echo "========================================="
srun ./T4_2

export OMP_NUM_THREADS=8
echo "========================================="
echo "Running T4_2_parallel with 8 OpenMP threads"
echo "========================================="
srun ./T4_2

export OMP_NUM_THREADS=16
echo "========================================="
echo "Running T4_2_parallel with 16 OpenMP threads"
echo "========================================="
srun ./T4_2

