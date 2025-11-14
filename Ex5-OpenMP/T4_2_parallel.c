#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

int main(void) {
    const size_t n = 1000000000;
    double *data = malloc(n * sizeof *data);
    if (!data) { return 1; }
    double start = omp_get_wtime();

    int max_threads = omp_get_max_threads(); //how many threads(workers) can we get
    double* partial_sum = calloc((size_t)max_threads, sizeof(double));
    double* partial_sum_sq = calloc((size_t)max_threads, sizeof(double));

    // LOOP 1: create synthetic data
    #pragma omp parallel
    {
        int tid = omp_get_thread_num();
        int nthreads = omp_get_num_threads();
        
        //here we determine the size of the chunk each thread has to populate
        size_t chunk   = (n + (size_t)nthreads - 1) / (size_t)nthreads;
        size_t start_i = (size_t)tid * chunk;
        size_t end_i   = start_i + chunk;
        if (end_i > n)
        {
            end_i = n; // if we had some uneven number and end up that end_i is bigger than n. 
                        //So if we had n = 10 and nthreads = 3, T0 = [0,4] T1 = [5,8] T2 = [9,12]
        }
        
        //here every thread creates data in his chunk.
        for (size_t i = start_i; i < end_i; ++i) {
            data[i] = i % 10;
        }
    
        #pragma omp barrier //make sure data is generated before continue
        

        // LOOP 2: compute sum
        for (size_t i = start_i; i < end_i; ++i) {
            partial_sum[tid] += data[n - 1 - i];
        }

        // LOOP 3: compute sum of squares
        for (size_t i = start_i; i < end_i; ++i) {
            partial_sum_sq[tid] += data[i] * data[i];
        }
    }

    double sum = 0.0;
    double sum_sq = 0.0;
    //max_threads not so big, so we don't really need parallelism here.
    for (int t = 0; t < max_threads; ++t) {
        sum    += partial_sum[t];
        sum_sq += partial_sum_sq[t];
    }

    double end = omp_get_wtime();
    double mean = sum / (double)n;
    double mean_sq = sum_sq / (double)n;
    double variance = mean_sq - mean * mean;

    printf("T4.2 Manual SPMD (single program multible data)\n"); //single program multible data
    printf("variance       = %.2f\n", variance);
    printf("total time (s) = %.2f\n", end - start);
    printf("num threads    = %d\n\n", omp_get_max_threads());

    free(data);
    return 0;
}