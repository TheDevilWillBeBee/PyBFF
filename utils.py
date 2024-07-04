import time
import random
import string

def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print('func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te - ts))
        return result

    return timed


class bcolors:
    RED = '\033[0;30;41m'
    GREEN = '\033[0;30;42m'
    YELLOW = '\033[0;30;43m'
    BLUE = '\033[0;30;44m'
    ENDC = '\033[0m'


printable_chars = string.digits + string.ascii_letters + string.punctuation


def print_tape(tape, head0_pos=0, head1_pos=0, pc_pos=0, skip_non_instruction=True):
    """
    Print the bytestring tape and color the positions of the read head, write head and program counter
    head0_pos will be colored blue
    head1_pos will be colored red
    pc_pos will be colored green
    """
    instructions = b"<>{}-+.,[]"
    zero = b'0'[0]

    for i, byte in enumerate(tape):
        if skip_non_instruction and byte not in instructions and byte != zero:
            char = ' '
        else:
            char = chr(byte)
            if char not in printable_chars:
                char = ' '

        if i == head0_pos:
            print(bcolors.BLUE + char + bcolors.ENDC, end="")
        elif i == head1_pos:
            print(bcolors.RED + char + bcolors.ENDC, end="")
        elif i == pc_pos:
            print(bcolors.GREEN + char + bcolors.ENDC, end="")
        else:
            # print(bcolors.YELLOW + char + bcolors.ENDC, end="")
            print(char, end="")
    print("")


def mutate(tape, mutation_rate=0):
    # Don't mutate if rate is 0
    if not mutation_rate:
        return tape

    mask = [random.random() < mutation_rate for _ in range(len(tape))]
    random_bytes = random.randbytes(len(tape))

    for i in range(len(tape)):
        if mask[i]:
            tape[i] = random_bytes[i]

    return tape
