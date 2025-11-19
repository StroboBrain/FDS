#include <mpi.h>
#include <stdio.h>
#include <unistd.h>

int main(int argc, char **argv) {

    MPI_Barrier(MPI_COMM_WORLD); // TODO(done): causes a runtime error because we can't use a barrier before initialization.
    MPI_Init(&argc, &argv);
    MPI_Barrier(MPI_COMM_WORLD); // TODO(done): No real workload done or danger of one process still beeing initialized.

    int rank, size, len;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    printf("Rank %d: Hello World\n", rank);
    fflush(stdout);
    
    usleep(150000 * (rank + 1));
    if (rank == 0) { MPI_Barrier(MPI_COMM_WORLD); } // TODO(done): does not make sense, barrier is a collective method, so if only one waits here and the others wait one after, we end up in a deadlock.
    MPI_Barrier(MPI_COMM_WORLD); // TODO(done): see above, but without this above, this barrier looks fine because the threads are in a different sleep timer. This does not really matter to much because if there was no barrier here, they would just wait in bcast.

    char msg[128] = {0};
    if (rank == 0) { snprintf(msg, sizeof(msg), "Root %d", rank); }
    MPI_Bcast(msg, 128, MPI_CHAR, 0, MPI_COMM_WORLD);
    MPI_Barrier(MPI_COMM_WORLD); // TODO(done): ok but bcast is already a collective action. So all processes should be synchronized already before.

    printf("Rank %d: got \"%s\"\n", rank, msg);
    fflush(stdout);

    MPI_Finalize();
    MPI_Barrier(MPI_COMM_WORLD); // TODO(done): Illegal to use a barrier after finalize.

    return 0;
}