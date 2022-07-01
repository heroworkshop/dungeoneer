import random


def pick_from_weighted_table(table):
    """A weighted table is a dict where the values are the relative probability (weight)"""
    choices = random.choices(list(table.keys()), weights=list(table.values()))
    return choices[0]


def dice(n, d):
    return sum(random.randint(1, d) for _ in range(n))
