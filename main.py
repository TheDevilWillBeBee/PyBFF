import yaml
import argparse
import random
from multiprocessing import Pool, cpu_count

from emulator import emulate
from utils import print_tape, mutate
from metrics import higher_order_entropy

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str, default='configs/small_config.yaml', help="configuration")


def generate_random_program(length=64):
    try:
        return bytearray(random.randbytes(length))
    except:
        return bytearray([random.randint(0, 256) for i in range(length)])


def main(config):
    soup_size = config.soup_size
    program_size = config.program_size
    mutation_rate = config.mutation_rate
    random.seed(config.random_seed)
    epochs = config.epochs

    soup = [generate_random_program(program_size) for _ in range(config.soup_size)]
    for epoch in range(epochs):
        perm = list(range(soup_size))
        random.shuffle(perm)
        program_pairs = [(perm[i], perm[i + 1]) for i in range(0, soup_size, 2)]
        with Pool(cpu_count()) as pool:
            results = pool.starmap(emulate, [(soup[i] + soup[j], 0, program_size) for i, j in program_pairs])

        total_iterations = 0
        total_skipped = 0
        finished_runs = 0
        terminated_runs = 0
        for (i, j), (tape, state, iteration, skipped) in zip(program_pairs, results):
            programA_new = mutate(tape[:program_size], mutation_rate=mutation_rate)
            programB_new = mutate(tape[program_size:], mutation_rate=mutation_rate)
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

        if epoch % config.eval_interval == 0:
            flat_soup = b''.join(soup)
            hoe = higher_order_entropy(flat_soup)
            print(f"Epoch: {epoch}"
                  f"\n\tHigher Order Entropy={hoe:.3f},"
                  f"\tAvg Iters={total_iterations:.3f},"
                  f"\tAvg Skips={total_skipped:.3f},"
                  f"\tFinished Ratio={finished_runs:.3f},"
                  f"\tTerminated Ratio={terminated_runs:.3f}")

            if hoe > 1.0:
                print(f"The first {config.num_print_programs} programs:")
                for program_idx in range(config.num_print_programs):
                    print_tape(soup[program_idx], skip_non_instruction=False)


if __name__ == '__main__':
    args = parser.parse_args()
    with open(args.config, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    config = argparse.Namespace(**config)
    main(config)
