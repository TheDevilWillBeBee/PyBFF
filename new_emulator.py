# TODO
# BFF version where we only have these tokens
# space < > { } [ ] . ,
# 0 1 (If we add 0 and 1 then [ will jump forward if it sees 0 and ] will jump backward if it sees 1)


# Maybe include + - (Jump to the next valid token | cyclic)



 # Initialize with random strings (of varying size)
 # strings of length L
 # L ~ 2**-L
 # P(space) vs P(Ops)


# First try without cutting at H1 to make sure things are working

# ------ -------
# I      H1
# H0


# After executing a ( or ) that moves the cut heads:
# Either flip ( or ) 
# Or replace ( or ) with @ or a noop

# Check to see if replacing 12 with .[..}>]} will eliminate the parasitic programs
# "12": "[..}>]}>" 
# "13": "...}>]}>"

import numpy as np
import random 

class bcolors:
    RED = '\033[0;30;41m'
    GREEN = '\033[0;30;42m'
    YELLOW = '\033[0;30;43m'
    BLUE = '\033[0;30;44m'
    ENDC = '\033[0m'

space_token = '@'
instructions = "<>{}-+.,[]()"
valid_tokens = list("01" + space_token + instructions)




def print_tape(tape, head0_pos=0, head1_pos=0, pc_pos=0, cut_pos=0, skip_non_instruction=True):
    """
    Print the bytestring tape and color the positions of the read head, write head and program counter
    head0_pos will be colored blue
    head1_pos will be colored red
    pc_pos will be colored green
    """
    
    zero = '0'

    for i, char in enumerate(tape):
        if i == head0_pos:
            print(bcolors.BLUE + char + bcolors.ENDC, end="")
        elif i == head1_pos:
            print(bcolors.RED + char + bcolors.ENDC, end="")
        elif i == pc_pos:
            print(bcolors.GREEN + char + bcolors.ENDC, end="")
        elif i == cut_pos:
            print(bcolors.YELLOW + char + bcolors.ENDC, end="")
        else:
            # print(bcolors.YELLOW + char + bcolors.ENDC, end="")
            print(char, end="")

    if cut_pos == len(tape):
        print(bcolors.YELLOW + ' ' + bcolors.ENDC, end="")
    print("")


def emulate(tape, head0_pos=0, head1_pos=0, pc_pos=0, max_iter=2 ** 10, verbose=0):
    """
    program: tape is a character sequence which contains the program
    head0_pos: Initial location of the read head
    head1_pos: Initial location of the write head
    pc_pos: Initial location of the instruction head (program counter)
    max_iter: Maximum number of instructions to be read before terminating
    """
    if len(tape) == 0:
        return tape, "Error, Empty Tape", 0, 0, "", ""
        

    max_iter = 2 ** 7 * len(tape)
    tape = list(tape)
    zero = '0'
    one = '1'
    open_bracket = '['
    close_bracket = ']'

    pc_pos = pc_pos
    
    
    cut_pos = head1_pos
    init_head1_pos = head1_pos
    head0_pos = head0_pos % len(tape)
    head1_pos = head1_pos % len(tape)

    pc_range = [0, init_head1_pos]

    state = "Terminated"
    iteration = 0
    skipped = 0
    while iteration < max_iter and pc_pos < pc_range[1]:
        instr = tape[pc_pos]
        if instr == '<':
            head0_pos = (head0_pos - 1) % len(tape)
        elif instr == '>':
            head0_pos = (head0_pos + 1) % len(tape)
        elif instr == ')':
            cut_pos = min(cut_pos + 1, len(tape))
            tape[pc_pos] = '@'  # Replace ( with noop to prevent unbounded loops
        elif instr == '(':
            cut_pos = max(cut_pos - 1, 0)
            tape[pc_pos] = '@'  # Replace ) with noop to prevent unbounded loops
        elif instr == '{':
            head1_pos = (head1_pos - 1) % len(tape)
        elif instr == '}':
            head1_pos = (head1_pos + 1) % len(tape)
        elif instr == '-':
            tape[head0_pos] = prev_token(tape[head0_pos])
        elif instr == '+':
            tape[head0_pos] = next_token(tape[head0_pos])
        elif instr == '.':
            tape[head1_pos] = tape[head0_pos]
        elif instr == ',':
            tape[head0_pos] = tape[head1_pos]
        elif instr == '[':
            if tape[head0_pos] == zero:
                diff = 1
                for i in range(pc_pos + 1, pc_range[1]):
                    if tape[i] == open_bracket:
                        diff += 1
                    elif tape[i] == close_bracket:
                        diff -= 1

                    if diff == 0:
                        pc_pos = i
                        break

                if diff != 0:
                    state = "Error, Unmatched ["
                    # cut_pos = init_head1_pos
                    break
        elif instr == ']':
            if tape[head0_pos] != zero:
                diff = 1
                for i in range(pc_pos - 1, pc_range[0] - 1, -1):
                    if tape[i] == close_bracket:
                        diff += 1
                    elif tape[i] == open_bracket:
                        diff -= 1

                    if diff == 0:
                        pc_pos = i
                        break

                if diff != 0:
                    state = "Error, Unmatched ]"
                    # cut_pos = init_head1_pos
                    break
        else:
            skipped += 1

        if verbose > 0:
            print(f"Iteration: {iteration:05}", end="\t\t")
            print_tape(tape, head0_pos, head1_pos, pc_pos, cut_pos, False)

        iteration += 1
        pc_pos = pc_pos + 1
        if pc_pos >= pc_range[1]:
            state = "Finished"
            break


    tape = "".join(tape)
    # cut the tape into two programs according to head0_pos and head1_pos
    # if head0_pos < head1_pos:
    #     A = tape[:head0_pos] + tape[head1_pos:]
    #     B = tape[head0_pos:head1_pos]
    # else:
    #     A = tape[head1_pos:head0_pos]
    #     B = tape[:head1_pos] + tape[head0_pos:]

    A = tape[:cut_pos]
    B = tape[cut_pos:]
    
    return tape, state, iteration, skipped, A, B



def next_token(token):
    idx = valid_tokens.index(token)
    return valid_tokens[(idx + 1) % len(valid_tokens)]

def prev_token(token):
    idx = valid_tokens.index(token)
    return valid_tokens[(idx - 1) % len(valid_tokens)]

def sample_program(length, prob_template=None):
    if prob_template is None or len(prob_template) == 0:
        probs = [1.0 / len(valid_tokens)] * len(valid_tokens)
    else:
        probs = []
        total_score = sum(prob_template.get(k, 0) for k in valid_tokens)
        for k in valid_tokens:
            probs.append(prob_template.get(k, 0) / total_score)

    return "".join(np.random.choice(list(valid_tokens), size=length, p=probs))


def mutate(tape, mutation_rate=0, prob_template=None):
    # Don't mutate if rate is 0
    if not mutation_rate:
        return tape

    tape = list(tape)
    mask = [random.random() < mutation_rate for _ in range(len(tape))]
    for i in range(len(tape)):
        if mask[i]:
            tape[i] = sample_program(1, prob_template=prob_template)
    return "".join(tape)

def create_soup(size=1000, avg_length=10, prob_template=None):
    soup = []
    for _ in range(size):
        length = np.random.geometric(1.0 / avg_length)
        length = avg_length
        prog = sample_program(length, prob_template)
        soup.append(prog)
    return soup


if __name__ == '__main__':
    prob_template = { '@': 5, '<': 1, '>': 1, '{': 1, '}': 1, '[': 1, ']': 1, '.': 1, ',': 1, '(': 1, ')': 1, '+': 0, '-': 0, '0': 0, '1': 0 }
    soup = create_soup(size=10, avg_length=10, prob_template=prob_template)
    for prog in soup:
        print(prog)

    A = soup[0]
    B = soup[1]
    # A = ".[..}>]..{"
    # A = "[.}>]@@@"
    # A = "...>]@.."
    # A = "[.}>.]@."
    # B = "@" * len(A)

    # A = "[...[>}["
    # B = "...}>]}>"

    # A = "."
    # B = sample_program(1)

    
    _, _, _, _, Af, Bf = emulate(A + B, head0_pos=0, head1_pos=len(A), pc_pos=0, max_iter=1000, verbose=1)
    print("Initial A:", A)
    print("Initial B:", B)
    print("Final A:", Af)
    print("Final B:", Bf)
    print("Mutated A:", mutate(A, mutation_rate=0.99, prob_template=prob_template))

    # emulate(A, verbose=1)