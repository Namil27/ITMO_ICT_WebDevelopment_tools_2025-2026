import threading
import time

TOTAL = 100_000_000
NUM_THREADS = 4

result = 0
lock = threading.Lock()


def calculate_sum(start, end):
    global result

    local_sum = 0

    for i in range(start, end + 1):
        local_sum += i

    with lock:
        result += local_sum


threads = []

chunk_size = TOTAL // NUM_THREADS

start_time = time.time()

for i in range(NUM_THREADS):
    start_num = i * chunk_size + 1

    if i == NUM_THREADS - 1:
        end_num = TOTAL
    else:
        end_num = (i + 1) * chunk_size

    thread = threading.Thread(
        target=calculate_sum,
        args=(start_num, end_num)
    )

    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

end_time = time.time()

print("Threading result:", result)
print("Time:", end_time - start_time)