"""
Source code for emulating the Brain Fuck Family programming lanuages.
An attempt to reproduce the results from: https://arxiv.org/pdf/2406.19108

instruction set:
head0: read head
head1: write head
jump changes to position of the instruction head

    < head0 = head0 - 1
    > head0 = head0 + 1
    { head1 = head1 - 1
    } head1 = head1 + 1
    - tape[head0] = tape[head0] - 1
    + tape[head0] = tape[head0] + 1
    . tape[head1] = tape[head0]
    , tape[head0] = tape[head1]
    [ if (tape[head0] == 0): jump forwards to matching ] command.
    ] if (tape[head0] != 0): jump backwards to matching [ command.
"""
import string

from utils import timeit, print_tape


def emulate(tape, head0_pos=0, head1_pos=0, pc_pos=0, max_iter=2 ** 13, verbose=0):
    """
    program: tape is a byte sequence which contains the program
    head0_pos: Initial location of the read head
    head1_pos: Initial location of the write head
    pc_pos: Initial location of the instruction head (program counter)
    max_iter: Maximum number of instructions to be read before terminating
    """
    instructions = b"<>{}-+.,[]"
    zero = b'0'[0]
    open_bracket = b"["[0]
    close_bracket = b"]"[0]

    head0_pos = head0_pos
    head1_pos = head1_pos
    pc_pos = pc_pos

    iteration = 0
    skipped = 0

    state = "Terminated"
    while iteration < max_iter:
        instr = tape[pc_pos]
        if instr == instructions[0]:
            head0_pos = (head0_pos - 1) % len(tape)
        elif instr == instructions[1]:
            head0_pos = (head0_pos + 1) % len(tape)
        elif instr == instructions[2]:
            head1_pos = (head1_pos - 1) % len(tape)
        elif instr == instructions[3]:
            head1_pos = (head1_pos + 1) % len(tape)
        elif instr == instructions[4]:
            tape[head0_pos] = (tape[head0_pos] - 1) % 256
        elif instr == instructions[5]:
            tape[head0_pos] = (tape[head0_pos] + 1) % 256
        elif instr == instructions[6]:
            tape[head1_pos] = tape[head0_pos]
        elif instr == instructions[7]:
            tape[head0_pos] = tape[head1_pos]
        elif instr == instructions[8]:
            if tape[head0_pos] == zero:
                diff = 1
                for i in range(pc_pos + 1, len(tape)):
                    if tape[i] == open_bracket:
                        diff += 1
                    elif tape[i] == close_bracket:
                        diff -= 1

                    if diff == 0:
                        pc_pos = i
                        break

                if diff != 0:
                    state = "Error, Unmatched ["
                    break

        elif instr == instructions[9]:
            if tape[head0_pos] != zero:
                diff = 1
                for i in range(pc_pos - 1, -1, -1):
                    if tape[i] == close_bracket:
                        diff += 1
                    elif tape[i] == open_bracket:
                        diff -= 1

                    if diff == 0:
                        pc_pos = i
                        break

                if diff != 0:
                    state = "Error, Unmatched ]"
                    break
        else:
            skipped += 1

        if verbose > 0:
            print(f"Iteration: {iteration:05}", end="\t\t")
            print_tape(tape, head0_pos, head1_pos, pc_pos, False)

        iteration += 1
        pc_pos = pc_pos + 1
        if pc_pos >= len(tape):
            state = "Finished"
            break

    return tape, state, iteration, skipped


if __name__ == "__main__":
    program1 = bytearray(b"[[{.>]-]                ]-]>.{[[")
    program2 = bytearray(b"0" * len(program1))
    tape = program1 + program2

    tape, state, iteration, skipped = emulate(tape, verbose=1, max_iter=1024)

    print(state, iteration, skipped)
