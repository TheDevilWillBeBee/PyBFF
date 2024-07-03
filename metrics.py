import brotli
import math


def shannon_entropy(byte_string):
    entropy = 0
    for byte in range(256):
        frequency = byte_string.count(byte) / len(byte_string)
        if frequency > 0:
            entropy += frequency * math.log(frequency, 2)
    return -entropy


def kolmogrov_complexity_estimate(byte_string):
    """
    Complexity of 8.0 means that the string is incompressible and 0.0 bits can be saved per byte
    Complexity of 0.0 means that the string is fully compressible and 8.0 bits can be saved per byte
    """
    return len(brotli.compress(byte_string)) / len(byte_string) * 8.0


def higher_order_entropy(byte_string):
    return shannon_entropy(byte_string) - kolmogrov_complexity_estimate(byte_string)
