from math import floor
from random import Random


def random_round(random: Random, val: float) -> int:
    whole = floor(val)
    chance = val - whole
    if random.random() < chance:
        return whole + 1
    return whole
