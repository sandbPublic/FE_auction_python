import itertools
from typing import List, Tuple


def extend_array(array, length: int, filler) -> None:
    while len(array) < length:
        array.append(filler)


# reads a file as a grid of values of a specific type
def read_grid(filename: str, grid_type: type = str) -> List[List]:
    try:
        file = open(filename, 'r')
    except FileNotFoundError as error:
        print(error)
    else:
        print(f'reading {filename}')
        grid = []
        for line in file.readlines():
            try:
                next_row = [grid_type(i) for i in line.split()]
            except ValueError as error:
                print(error)
            else:
                if len(next_row) > 0:  # skip empty rows
                    grid.append(next_row)
        file.close()
        return grid


# If a permutation has one loop longer than two (because swaps are already covered) then we
# want to try it. If there is more than one loop, we don't test it because we already tested
# the loops individually
def just_one_loop(permutation: Tuple) -> bool:
    players_trading = 0
    highest_trading_player = 0
    for index, item in enumerate(permutation):
        if index != item:
            players_trading += 1
            highest_trading_player = index

    if players_trading < 3:
        return False

    def highest_loop_member(x):
        record = x

        def recursive(y):
            nonlocal record
            if record < y:
                record = y
            if permutation[y] == x:
                return record
            return recursive(permutation[y])

        return recursive(x)

    for index, item in enumerate(permutation):
        if highest_loop_member(index) < highest_trading_player and index != item:
            return False

    return True


def one_loop_permutations(max_loop_size: int) -> List[Tuple]:
    return [p for p in itertools.permutations(range(max_loop_size)) if just_one_loop(p)]
