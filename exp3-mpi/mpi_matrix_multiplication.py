from mpi4py import MPI
import numpy as np
import time

# ---------------- MPI SETUP ----------------
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# ---------------- MATRIX SIZE ----------------
N = 4000   


np.set_printoptions(precision=3, suppress=True)

# ---------------- MASTER PROCESS ----------------
if rank == 0:
    print(f"\nMPI Matrix Multiplication with {size} processes\n")

    
    A = np.random.rand(N, N)
    B = np.random.rand(N, N)

    start_time = time.time()

    
    comm.bcast(B, root=0)

    
    rows_per_proc = N // size
    extra = N % size

    offset = 0
    for i in range(1, size):
        rows = rows_per_proc + (1 if i <= extra else 0)
        comm.send(A[offset:offset + rows, :], dest=i, tag=1)
        comm.send(offset, dest=i, tag=2)
        offset += rows

    
    rows = rows_per_proc + (1 if 0 < extra else 0)
    local_A = A[offset:offset + rows, :]
    local_C = np.dot(local_A, B)

    
    C = np.zeros((N, N))
    C[offset:offset + rows, :] = local_C

    
    for i in range(1, size):
        part_C = comm.recv(source=i, tag=3)
        part_offset = comm.recv(source=i, tag=4)
        C[part_offset:part_offset + part_C.shape[0], :] = part_C

    end_time = time.time()

    # ---------------- OUTPUT ----------------
    print(f"Execution Time: {end_time - start_time:.4f} seconds")

    print("\nSample of Matrix A (top-left 3x3):")
    print(A[:3, :3])

    print("\nSample of Matrix B (top-left 3x3):")
    print(B[:3, :3])

    print("\nSample of Result Matrix C (top-left 3x3):")
    print(C[:3, :3])

# ---------------- WORKER PROCESSES ----------------
else:
    
    B = comm.bcast(None, root=0)

    local_A = comm.recv(source=0, tag=1)
    offset = comm.recv(source=0, tag=2)

    local_C = np.dot(local_A, B)

    
    comm.send(local_C, dest=0, tag=3)
    comm.send(offset, dest=0, tag=4)
