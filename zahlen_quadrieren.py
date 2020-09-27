import random
import time


def numberToBase(n, b):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(str(int(n % b)))
        n //= b
    return digits[::-1]


def methode_1(zahl):
    digits = numberToBase(zahl, zahl)[1:]
    return int('1' + ''.join(digits + digits), zahl)


def methode_2(zahl):
    return zahl * zahl


def speed_test():
    anzahl = 20
    zahlen = []
    r = random.Random()
    for s in range(anzahl):
        zahlen += [r.randint(1, 36)]

    start = time.process_time()
    for s in zahlen:
        ergebnis = methode_1(s)
        # assert ergebnis == s * s
    zeit_methode_1 = time.process_time() - start
    print("Methode 1 brauchte: " + str(zeit_methode_1) + "s")

    start = time.process_time()
    for s in zahlen:
        ergebnis = methode_2(s)
        # assert ergebnis == s * s
    zeit_methode_2 = time.process_time() - start
    print("Methode 2 brauchte: " + str(zeit_methode_2) + "s")

    if zeit_methode_1 == zeit_methode_2:
        print("UNENTSCHIEDEN!")
    elif zeit_methode_2 > zeit_methode_1:
        print("GEWINNER: Methode 1")
    else:
        print("GEWINNER: Methode 2")


speed_test()