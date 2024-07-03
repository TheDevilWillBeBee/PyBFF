import random
from multiprocessing import Pool, cpu_count

from emulator import emulate
from utils import print_tape
from metrics import higher_order_entropy


def generate_random_program(length=64):
    try:
        return bytearray(random.randbytes(length))
    except:
        return bytearray([random.randint(0, 256) for i in range(length)])


if __name__ == '__main__':
    soup_size = 2 ** 14
    program_size = 32
    random.seed(52)
    soup = [generate_random_program(program_size) for _ in range(soup_size)]

    # soup[0] = bytearray(b"[[{.>]-]                                                ]-]>.{[[")
    # for i in range(1):
    #     soup[i] = bytearray(b"[[{.>]-]                ]-]>.{[[")

    iterations = 1024 * 1024
    for step in range(iterations):
        #
        perm = list(range(soup_size))
        random.shuffle(perm)

        program_pairs = [(perm[i], perm[i + 1]) for i in range(0, soup_size, 2)]
        with Pool(cpu_count()) as pool:
            results = pool.starmap(emulate, [(soup[i] + soup[j],) for i, j in program_pairs])

        total_iterations = 0
        total_skipped = 0
        finished_runs = 0
        terminated_runs = 0
        for (i, j), (tape, state, iteration, skipped) in zip(program_pairs, results):
            programA_new = tape[:program_size]
            programB_new = tape[program_size:]
            soup[i] = programA_new
            soup[j] = programB_new

            total_iterations += iteration
            total_skipped += skipped

            finished_runs += (state == "Finished") * 1.0
            terminated_runs += (state == "Terminated") * 1.0


        total_skipped /= len(program_pairs)
        total_iterations /= len(program_pairs)
        terminated_runs /= len(program_pairs)
        finished_runs /= len(program_pairs)

        if step % 100 == 0:
            flat_soup = b''.join(soup)
            hoe = higher_order_entropy(flat_soup)
            print(f"Iteration: {step}, "
                  f" Higher Order Entropy =  {hoe:.3f},"
                  f"\n\tAvg Iters = {total_iterations:.3f},"
                  f"\tAvg Skips = {total_skipped:.3f},"
                  f"\tAvg Finished = {finished_runs:.3f},"
                  f"\tAvg Terminated = {terminated_runs:.3f}")
