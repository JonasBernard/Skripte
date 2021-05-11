from math import sqrt
from functools import reduce
from operator import add


def divisors(n):
    for d in range(2, int(n/2)):
        if n % d == 0:
            yield d
            if d * d != n:
                yield int(n / d)


i = 6
while True:
    if reduce(add, list(divisors(i)), 1) == i:
        print(f"Vollkommene Zahl gefunden: {i}")
    i += 1
