import yaml
import argparse
import random
import json
import numpy as np
from collections import deque
from pathlib import Path
from multiprocessing import Pool, cpu_count

from new_emulator import (
    emulate,
    print_tape,
    create_soup,
    sample_program,
    mutate,
    valid_tokens,
)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--config", type=str, default="configs/new_config.yaml", help="configuration"
)


import brotli
import math

# import lru cache
from functools import lru_cache


def get_base_entropy(prob_template=None):
    entropy = 0
    total_sum = sum(prob_template.values())
    for k in prob_template.keys():
        frequency = prob_template[k] / total_sum
        if frequency > 0:
            entropy += frequency * math.log(frequency, 2)
    return -entropy


def shannon_entropy(tape):
    entropy = 0
    for k in valid_tokens:
        frequency = tape.count(k) / len(tape)
        if frequency > 0:
            entropy += frequency * math.log(frequency, 2)
    return -entropy


def kolmogrov_complexity_estimate(tape):
    """
    Complexity of 1.0 means that the string is incompressible
    Complexity of 0.0 means that the string is fully compressible
    """
    byte_string = tape.encode("ascii")  # ASCII encoding
    return len(brotli.compress(byte_string)) / len(byte_string) * 8.0


def get_tape_stats(tape):
    entropy = shannon_entropy(tape)
    complexity = kolmogrov_complexity_estimate(tape)
    return entropy, complexity, entropy - complexity


def main(config):
    soup_size = config.soup_size
    avg_program_length = config.avg_program_length
    mutation_rate = config.mutation_rate
    random.seed(config.random_seed)
    np.random.seed(config.random_seed)
    epochs = config.epochs

    history_length = getattr(config, "history_length", 100)
    replicator_threshold = getattr(config, "replicator_threshold", 0.5)
    history_log_path = Path(getattr(config, "history_log_path", "soup_history_log.json"))
    history_buffer = deque(maxlen=max(1, history_length))

    prob_template = config.prob_template

    soup = create_soup(
        size=soup_size, avg_length=avg_program_length, prob_template=prob_template
    )
    for i in range(len(soup)):
        soup[i] = ".[.}>].." + "@" * (len(soup[i]) - 8)
    # flat_soup = ''.join(soup)
    # print("Entropy of initial soup:", shannon_entropy(flat_soup))
    # print("Kolmogorov Complexity Estimate of initial soup:", kolmogrov_complexity_estimate(flat_soup))

    # base_entropy = get_base_entropy(prob_template=prob_template)
    # print("Base Entropy of the instruction set:", base_entropy)
    # print("Higher Order Entropy of initial soup:", higher_order_entropy(flat_soup, base_entropy=base_entropy))

    # exit()

    for epoch in range(epochs):
        perm = list(range(soup_size))
        random.shuffle(perm)
        program_pairs = [(perm[i], perm[i + 1]) for i in range(0, soup_size, 2)]
        # print(program_pairs)
        # exit()
        with Pool(cpu_count()) as pool:
            results = pool.starmap(
                emulate,
                [(soup[i] + soup[j], 0, len(soup[i])) for i, j in program_pairs],
            )

        total_iterations = 0
        total_skipped = 0
        finished_runs = 0
        terminated_runs = 0
        avg_length = 0
        maximum_length = 0
        for (i, j), (tape, state, iteration, skipped, A_new, B_new) in zip(
            program_pairs, results
        ):
            # programA_new = mutate(tape[:program_size], mutation_rate=mutation_rate)
            # programB_new = mutate(tape[program_size:], mutation_rate=mutation_rate)
            A_new = mutate(
                A_new, mutation_rate=mutation_rate, prob_template=prob_template
            )
            B_new = mutate(
                B_new, mutation_rate=mutation_rate, prob_template=prob_template
            )
            soup[i] = A_new
            soup[j] = B_new

            total_iterations += iteration
            total_skipped += skipped
            avg_length += len(A_new) + len(B_new)
            maximum_length = max(maximum_length, len(A_new), len(B_new))

            finished_runs += (state == "Finished") * 1.0
            terminated_runs += (state == "Terminated") * 1.0

        total_skipped /= len(program_pairs)
        total_iterations /= len(program_pairs)
        terminated_runs /= len(program_pairs)
        finished_runs /= len(program_pairs)
        avg_length /= soup_size

        flat_soup = "".join(soup)
        entropy, complexity, hoe = get_tape_stats(flat_soup)

        if epoch % config.eval_interval == 0:
            print(
                f"Epoch: {epoch}"
                f"\tEntropy={entropy:.3f},"
                f"\tComplexity={complexity:.3f},"
                f"\tHigher Order Entropy={hoe:.3f},"
                f"\n\t\tAvg Iters={total_iterations:.3f},"
                f"\tAvg Skips={total_skipped:.3f},"
                f"\n\t\tFinished Ratio={finished_runs:.3f},"
                f"\tTerminated Ratio={terminated_runs:.3f}"
                #   f"\tAvg Program Length={avg_length:.3f}"
                #   f"\tMax Program Length={maximum_length}"
            )

            # Print top 10 longest programs
            # top_k = min(10, len(soup))
            # lengths_with_indices = [(idx, len(prog)) for idx, prog in enumerate(soup)]
            # lengths_with_indices.sort(key=lambda x: x[1], reverse=True)
            # print("Top 10 longest programs:")
            # for rank, (idx, length) in enumerate(lengths_with_indices[:top_k], start=1):
            #     print(f"#{rank} idx={idx} length={length}")
            #     print_tape(soup[idx], -1, -1, -1, -1, skip_non_instruction=False)

        if True or hoe > -3.0:
            for i in range(min(config.num_print_programs, len(soup))):
                # print(f"Program #{i}, Length={len(soup[i])}")
                print_tape(soup[i], -1, -1, -1, -1, skip_non_instruction=False)

        history_buffer.append(
            {
                "epoch": epoch,
                "entropy": entropy,
                "complexity": complexity,
                "higher_order_entropy": hoe,
                "avg_iterations": total_iterations,
                "avg_skipped": total_skipped,
                "finished_ratio": finished_runs,
                "terminated_ratio": terminated_runs,
                "avg_program_length": avg_length,
                "max_program_length": maximum_length,
                "program_pairs": [list(pair) for pair in program_pairs],
                "soup": {i: soup[i] for i in range(len(soup))},
            }
        )

        # if hoe >= replicator_threshold and False:
        if False and epoch == 30:
            history_log_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "trigger_epoch": epoch,
                "replicator_threshold": replicator_threshold,
                "history_length": history_length,
                "records": list(history_buffer),
            }
            with open(history_log_path, "w") as f:
                json.dump(payload, f, indent=2)
            print(
                f"Self-replicator detected (hoe={hoe:.3f}). "
                f"History for last {len(history_buffer)} epochs saved to {history_log_path}."
            )
            return


if __name__ == "__main__":
    args = parser.parse_args()
    with open(args.config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    config = argparse.Namespace(**config)
    main(config)
