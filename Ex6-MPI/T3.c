#include <mpi.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);

    int rank, len;
    char hostname[MPI_MAX_PROCESSOR_NAME];
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Get_processor_name(hostname, &len);

    char msg[256];

    if (rank == 0) {
        snprintf(msg, sizeof(msg), "Hello World from rank: %d on node: %s", rank, hostname);
        MPI_Request req;

        for (int dest = 1; dest < 4; dest++) {
            MPI_Isend(msg, strlen(msg) + 1, MPI_CHAR, dest, 0, MPI_COMM_WORLD, &req);
            MPI_Wait(&req, MPI_STATUS_IGNORE);
        }

    } else {
        MPI_Request req;
        MPI_Irecv(msg, sizeof(msg), MPI_CHAR, 0, 0, MPI_COMM_WORLD, &req);
        MPI_Wait(&req, MPI_STATUS_IGNORE);
        printf("Rank: %d on node: %s received the following message: %s\n", rank, hostname, msg);
        fflush(stdout);
    }

    MPI_Finalize();
    return 0;
}
