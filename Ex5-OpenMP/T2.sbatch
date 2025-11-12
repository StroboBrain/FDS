#!/bin/bash
#SBATCH --job-name=T2                    # The name of the job
#SBATCH --partition=xeon                 # The main partition of miniHPC
#SBATCH --hint=nomultithread             # Disable hardware multithreading
#SBATCH --exclusive                      # Exclusive access to resources
#SBATCH --time=00:10:00                  # Requested execution time
#SBATCH --nodes=1                        # Requested number of nodes
#SBATCH --ntasks-per-node=1              # Requested processes per node
#SBATCH --cpus-per-task=1                # Requested threads per process
#SBATCH --output=T2.out                  # Stdout/stderr log file

module load hwloc

#Keep threads consistent for later add OpenMP
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

echo "== Hostname =="
srun hostname

echo
echo "== lscpu (summary) =="
srun lscpu | egrep 'Model name|Socket|Core|Thread|NUMA|CPU\(s\)'

echo
echo "== Full lscpu =="
srun lscpu

echo
echo "== NUMA hardware via numactl (if available) =="
srun bash -lc 'numactl --hardware || echo "numactl not available"'

echo
echo "== lstopo topology =="
# Use console output to avoid Unicode box-drawing mojibake
srun lstopo --no-io --of console

echo
echo "== /proc/meminfo (first 40 lines) =="
srun bash -lc 'head -n 40 /proc/meminfo'

echo
echo "== End of T2 report =="
