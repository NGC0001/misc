import random

from functools import reduce


def step_into_magic(n=4, magic=6174):
    l = [random.randrange(0, 10) for i in range(n)]
    nstep = 0
    while nstep < 100:
        l.sort()
        nstep += 1
        bigger = reduce(int.__add__, [d * 10**i for i, d in enumerate(l)], 0)
        smaller = reduce(int.__add__,
                         [d * 10**i for i, d in enumerate(l[::-1])], 0)
        difference = bigger - smaller
        print(nstep, bigger, smaller, difference)
        if difference == magic:
            print()
            break

        l.clear()
        for i in range(n):
            l.append(difference % 10)
            difference //= 10


if __name__ == '__main__':
    for i in range(100):
        step_into_magic(n=4, magic=6174)
