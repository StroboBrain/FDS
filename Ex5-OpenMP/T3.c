// T3: Hello from OpenMP threads, with runtime + SLURM info
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <omp.h>

static const char* getenv_default(const char* k, const char* d){
    const char* v = getenv(k);
    return v ? v : d;
}

int main(void) {
    char host[256]; gethostname(host, sizeof(host));
    int pid = (int)getpid();
    int omp_procs = omp_get_num_procs();
    int omp_max_threads = omp_get_max_threads();
    const char* slurm_ntasks_per_node  = getenv_default("SLURM_NTASKS_PER_NODE", "unknown");
    const char* slurm_cpus_per_task    = getenv_default("SLURM_CPUS_PER_TASK",   "unknown");
    const char* slurm_jobid            = getenv_default("SLURM_JOB_ID",          "n/a");
    const char* omp_num_threads_env    = getenv_default("OMP_NUM_THREADS",       "unset");

    printf("=== Process report ===\n");
    printf("Host: %s  PID: %d  SLURM_JOB_ID: %s\n", host, pid, slurm_jobid);
    printf("SLURM_NTASKS_PER_NODE=%s  SLURM_CPUS_PER_TASK=%s  OMP_NUM_THREADS=%s\n",
           slurm_ntasks_per_node, slurm_cpus_per_task, omp_num_threads_env);
    printf("omp_get_num_procs()=%d  omp_get_max_threads()=%d\n", omp_procs, omp_max_threads);
    fflush(stdout);

    //parallel region
    #pragma omp parallel
    {
        int tid  = omp_get_thread_num();
        int nthr = omp_get_num_threads();
        printf("Hello World from thread ID: %d / %d on %s (PID %d)\n",
               tid, nthr, host, pid);
    }

    return 0;
}
