import multiprocessing
import time

TOTAL = 100_000_000
NUM_PROCESSES = 4


def calculate_sum(start, end, queue):
    local_sum = 0

    for i in range(start, end + 1):
        local_sum += i

    queue.put(local_sum)


if __name__ == "__main__":

    queue = multiprocessing.Queue()

    processes = []

    chunk_size = TOTAL // NUM_PROCESSES

    start_time = time.time()

    for i in range(NUM_PROCESSES):

        start_num = i * chunk_size + 1

        if i == NUM_PROCESSES - 1:
            end_num = TOTAL
        else:
            end_num = (i + 1) * chunk_size

        process = multiprocessing.Process(
            target=calculate_sum,
            args=(start_num, end_num, queue)
        )

        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    result = 0

    while not queue.empty():
        result += queue.get()

    end_time = time.time()

    print("Multiprocessing result:", result)
    print("Time:", end_time - start_time)