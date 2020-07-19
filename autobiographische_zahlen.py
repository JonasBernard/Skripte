import math
import time
import random


def autobiographische_zahl(min, max):
    zahlen = {}
    for a in range(min, max):
        zahlen[a] = ist_autobiographisch(a)
        if zahlen[a]:
            print(a)
    return zahlen


def ist_autobiographisch(zahl):
    stellen = jonas(zahl)
    zählung = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
    for stelle in range(len(stellen)):
        wert = stellen[stelle]
        zählung[wert] = zählung[wert] + 1
    for stelle in range(len(stellen)):
        if stellen[stelle] != zählung[stelle]:
            return False
    return True


def jonas(zahl):
    zahl_string = str(zahl)
    stellen = {}
    for s in range(len(zahl_string)):
        stellen[s] = int(zahl_string[s])
    return stellen


def nils(zahl):
    ergebnis = {}
    stellen = math.floor(math.log(zahl, 10)) + 1
    for stelle in range(stellen):
        ergebnis[stelle] = math.floor(zahl / (10 ** (stellen - stelle - 1))) % 10
    return ergebnis


def speed_test():
    anzahl = 1000000
    zahlen = []
    r = random.Random()
    for s in range(anzahl):
        zahlen += [r.randint(1, 100000)]

    start = time.process_time()
    for s in zahlen:
        jonas(s)
    zeit_jonas = time.process_time() - start
    print("Methode von Jonas brauchte: " + str(zeit_jonas) + "s")

    start = time.process_time()
    for s in zahlen:
        nils(s)
    zeit_nils = time.process_time() - start
    print("Methode von Nils brauchte: " + str(zeit_nils) + "s")

    if zeit_nils == zeit_jonas:
        print("UNENTSCHIEDEN!")
    elif zeit_jonas > zeit_nils:
        print("GEWINNER: Nils")
    else:
        print("GEWINNER: Jonas")


autobiographische_zahl(0, 1000000000000)