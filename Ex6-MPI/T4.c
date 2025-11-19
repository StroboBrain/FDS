#include <mpi.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);

    int rank, len;
    char hostname[MPI_MAX_PROCESSOR_NAME];
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Get_processor_name(hostname, &len);

    char msg[256] = {0};

    if (rank == 0) {
        snprintf(msg, sizeof(msg), "Hello World from rank: %d on node: %s", rank, hostname);
    }

    MPI_Bcast(msg, 256, MPI_CHAR, 0, MPI_COMM_WORLD);

    if (rank != 0) {
        printf("Rank: %d on node: %s received the following message: %s\n", rank, hostname, msg);
        fflush(stdout);
    }

    MPI_Finalize();
    return 0;
}
