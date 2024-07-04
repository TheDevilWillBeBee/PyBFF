# Python implementation of BrainFuck Family

This repository is an attempt to reproduce the results of the following newly published paper:
**Computational Life: How Well-formed,
Self-replicating Programs Emerge from Simple
Interaction**: [https://arxiv.org/pdf/2406.19108](https://arxiv.org/pdf/2406.19108)

The [original source code](https://github.com/paradigms-of-intelligence/cubff) is implemented using C++ and Cuda to
achieve high performance.
This python implementation sacrifices p erformance for readability and ease of use.

## Getting started

The requirements for this project are very light and include the _brotli_ and _pyyaml_ libraries.
The _brotli_ library implements the compression algorithms which is used for calculating the _higher order entropy_
metric.

```bash
pip install -r requirements.txt
```

The `main.py` includes a minimal implementation of the primordial soup and its update.

```bash
python main.py --config configs/base_config.yaml
```

### Configs

* Contrary to the original paper, I set the initial position of the write_head to `program_size`. This means that in the
  beginning of the execution the read head points to the start of program A and the write head points to the start of
  the program B. In this way, the two programs are treated with more symmetry, which seems to speed up the
  emergence of the self-replicating programs. Also, this change allows non-palindrome self-replicating programs to
  emerge.

* **base_config.yaml** This simulation uses a soup size of 16384 programs with 64 bytes each and a mutation rate of
  0.00012. The first self-replicating program emerges between epoch 240 and 250. The following program shows one of the
  mutations the self-replicating program that emerged : `.Z     [o<J {TT,,    ]G/H    B     u  P_      F  q~- 5I    K/`.
* **small_config.yaml** This simulation uses a soup size of 4096 programs with 32 bytes each and a mutation rate of
  0.001. The first self-replicating program emerges between epoch 13900 and 14000. The following program shows one of
  the
  mutations the self-replicating program that emerged : `. 4 .p     [2:      M =|< {, ]`.

## Notes

* Since python is much slower than c++ and cuda, I have tried to reduce the computational requirements of the simulation
  to make the experiments run in reasonable time. For starter, I have decreased the soup size and the maximum number of
  iterations per program execution. I have also found that placing the write head in the middle of the tape, i.e. at the
  start of the second program, speeds up the emergence of self-replicating programs.
* The check for the programs validity (correct `[` and `]` brackets) is done during the execution of the program. Hence,
  If a program is invalid, the instructions before reaching the invalid brackets are still executed and the soup is
  still updated.
* I use python's default multiprocessing to speed up the execution of programs in each epoch. This speeds up the
  execution by the number of cpu cores available. On my workstation with an Intel i7-13700K, and given a soup of 2**17
  programs with 64 bytes each, each update step takes roughly 1.2 seconds.
* The `random.randbytes` method was introduced in Python 3.9.

## Description of the files

* **emulator.py**: The `emulate` function in this file receives a _bytearray_ tape that contains a BrainFuck program and
  emulates it. You can pass `verbose=1` to see the state of the tape at each moment of
  execution. The emulator also contains a simple self-replicating program which its executions shown in the image
  below: ![State of the tape](data/tape_state.png)

* **metrics.py**: This file include the Shanon entropy and Lempel–Ziv compression functionalities which are required to
  calculate the _higher order entropy_ metric proposed in the original paper. The _brotli_ library is used for the
  compression algorithms.
* **utils.py**: This function includes the `print_tape` utility function that allows you to print the state of a
  program. The read and write heads are highlighted using the blue and red colors and the instruction pointer is
  highlighted using green.
  in the paper.

## TODO List

* Implement the tracer functionality.
* ~~Implement mutations.~~ :white_check_mark: