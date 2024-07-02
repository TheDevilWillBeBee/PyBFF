import random
from multiprocessing import Pool, cpu_count

from emulator import emulate
from utils import print_tape
from metrics import higher_order_entropy


def generate_random_program(length=64):
    return bytearray(random.randbytes(length))


if __name__ == '__main__':

    soup_size = 2 ** 17
    program_size = 64
    soup = [generate_random_program(program_size) for _ in range(soup_size)]

    soup[0] = bytearray(b"[[{.>]-]                                                ]-]>.{[[")

    iterations = 1024
    for step in range(iterations):
        #
        perm = list(range(soup_size))
        random.shuffle(perm)

        program_pairs = [(perm[i], perm[i + 1]) for i in range(0, soup_size, 2)]
        with Pool(cpu_count()) as pool:
            results = pool.starmap(emulate, [(soup[i] + soup[j],) for i, j in program_pairs])

        for (i, j), (tape, state, iteration, skipped) in zip(program_pairs, results):
            programA_new = tape[:program_size]
            programB_new = tape[program_size:]

            soup[i] = programA_new
            soup[j] = programB_new

        if step % 10 == 0:
            flat_soup = b''.join(soup)
            print("Iteration:", step, " Higher Order Entropy:", higher_order_entropy(flat_soup))
