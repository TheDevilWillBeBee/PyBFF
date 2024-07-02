import brotli
import math


def shannon_entropy(byte_string):
    entropy = 0
    for byte in range(256):
        frequency = byte_string.count(byte) / len(byte_string)
        if frequency > 0:
            entropy += frequency * math.log(frequency, 2)
    return -entropy


def compressibility(byte_string):
    """
    Compressibility  of 0.0 means that the string is incompressible.
    Compressibility of 1.0 means that the string is fully compressible.
    """
    return 1.0 - len(brotli.compress(byte_string)) / len(byte_string)


def higher_order_entropy(byte_string):
    return shannon_entropy(byte_string) + compressibility(byte_string)
