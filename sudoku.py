import random

sudoku = []
width = 9
height = 9
width_cell = 3
height_cell = 3

def print_sudoku():
    global sudoku, width, height, width_cell, height_cell
    for x in range(height):
        print(sudoku[x])

def generate_sudoku():
    global sudoku, width, height, width_cell, height_cell
    sudoku = []

    print("Generating sudoku skeleton...")
    for x in range(height):
        sudoku.append([])
        for y in range(width):
            sudoku[x].append(0)

    print("Finished. Generating content...")
    seq = [x for x in range(1, 10)]
    random.shuffle(seq)
    solve(seq, True)

    print("Generation finished.")

def solve(seq, shuffle):
    s(seq, shuffle)
    print("There aren't any further solutions.")

def s(seq, shuffle):
    for x in range(height):
        for y in range(width):
            if sudoku[x][y] == 0:
                #print("Generating possible content for cell [{0},{1}]...".format(x, y))
                for n in seq:
                    if is_possible(x, y, n):
                        sudoku[x][y] = n
                        #print("Setting content of [{0},{1}]: {2}.".format(x, y, n))
                        s(seq, shuffle)
                        sudoku[x][y] = 0
                        #print("That did not work. Setting content of [{0},{1}] to blank.".format(x, y))
                return
    print("Solution found:")
    print_sudoku()
    if input("Calculate another one? (y/n)") in ["Yes", "Y", "y", "yes", ""]:
        if shuffle:
            random.shuffle(seq)
    else:
        exit(0)

def is_possible(x, y, n):
    global sudoku, width, height, width_cell, height_cell

    #print("is_possible: Checking varius x and y={0} for n={1}:".format(y, n))
    for x1 in range(height):
        if x == x1: continue
        #print("is_possible: Checking x={0} and y={1} for {2}!={3}...".format(x1, y, n, sudoku[x1][y]))
        if sudoku[x1][y] == n:
            #print("is_possible: There is already a {0} in row {1}. Cannot put that in row {2}.".format(n, x1, x))
            return False

    #print("is_possible: Checking x={0} and various y for n={1}:".format(x, n))
    for y1 in range(width):
        if y == y1: continue
        #print("is_possible: Checking x={0} and y={1} for {2}!={3}...".format(x, y1, n, sudoku[x][y1]))
        if sudoku[x][y1] == n:
            #print("is_possible: There is already a {0} in column {1}. Cannot put that in column {2}.".format(n, y1, y))
            return False

    #print("is_possible: Checking box...")
    xb = x // height_cell
    yb = y // width_cell
    for x1 in range(height_cell * xb, height_cell * xb + height_cell):
        for y1 in range(width_cell * yb, width_cell * yb + width_cell):
            if x1 == x and y1 == y: continue
            #print("is_possible: Checking x={0} and y={1}.".format(x1, y1))
            if sudoku[x1][y1] == n:
                #print("is_possible: There is already a {0} in box {1},{2}. Cannot put that at {3},{4}".format(n, xb, yb, x, y))
                return False

    return True

sudoku = [
[1, 5, 2, 3, 8, 6, 7, 4, 9],
[3, 0, 0, 0, 0, 0, 0, 0, 2],
[7, 0, 9, 1, 5, 2, 3, 0, 6],
[5, 0, 3, 2, 6, 8, 4, 0, 7],
[2, 0, 8, 4, 9, 7, 5, 0, 3],
[4, 0, 7, 5, 1, 3, 2, 0, 8],
[8, 0, 0, 0, 0, 0, 0, 0, 1],
[9, 2, 5, 6, 7, 1, 8, 3, 4],
[6, 7, 1, 8, 3, 4, 9, 2, 5]
]
solve([x for x in range(1, 10)], False)
