import pricing
import itertools
import time
import statistics
import random
import cProfile
from typing import List
Matrix = List[List[float]]


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
        grid = []
        for line in file.readlines():
            try:
                next_row = [grid_type(i) for i in line.split()]
            except ValueError as error:
                print('reading ', filename)
                print(error)
            else:
                if len(next_row) > 0:  # skip empty rows
                    grid.append(next_row)
        file.close()
        return grid


class Unit:
    def __init__(self, name: str, recruit_order: int):
        self.name = name
        self.recruit_order = recruit_order
        self.owner = -1
        self.bids = []
        # whenever iterating over bids, we also iterate over Units
        # Simplify loops and save on zips by storing the bids in the Units


class AuctionState:
    def __init__(self, robust_factor: float = 0.25):
        self.robust_factor = robust_factor  # bias in favor of good teams rather than expected victory
        self.rotations = []

        self.players = []
        self.units = []

        self.max_team_size = 0
        self.team_sizes = []  # index -1 for unassigned

        # index by player last for printing/reading and for consistency
        # used for redundancy adjusted team values
        self.bid_sums = []

        self.synergies = []
        # P x U x U, players choose value to reduce/increase value of unit pairs
        # generally negative for redundant units
        # increment value of team by manual_synergy[i][j][valuer] if i and j on same team
        # should be triangular matrix since synergy i<->j == j<->i

    def print_bids(self):
        print('--BIDS--       ', end=' ')
        for player in self.players:
            print(f'{player:10s}', end=' ')
        print()

        for unit in self.units:
            unit_line = f'{unit.name:15s}'
            for bid in unit.bids:
                unit_line += f' {bid:5.2f}     '
            print(unit_line)

    def set_median_synergy(self):
        player_synergies = []
        for u_i in range(len(self.units)):
            next_synergy_row = []
            for u_j in range(len(self.units)):
                next_synergy_row.append(statistics.median([synergy[u_i][u_j] for synergy in self.synergies]))
            player_synergies.append(next_synergy_row)
        self.synergies.append(player_synergies)

    # checks that populated section of the matrix is triangular
    def print_synergy(self, player_i: int):
        print(f'  Synergies for {self.players[player_i]:10s}')

        for u_i in range(len(self.units)):
            something_to_print = False
            unit_line = f'{self.units[u_i].name:12s}: '
            for u_j, synergy in enumerate(self.synergies[player_i][u_i]):
                if synergy != 0:
                    something_to_print = True
                    unit_line += f' {self.units[u_j].name:12s}{synergy:5.2f} '
                    if u_j <= u_i:
                        print('NOTE, synergy matrix not triangular, possible error')
            if something_to_print:
                print(unit_line)

    def clear_assign(self):
        self.team_sizes = [0] * len(self.players)
        self.team_sizes.append(len(self.units))  # all unassigned (team -1)

        for unit in self.units:
            unit.owner = -1

    # Only need to track team size during initial assignment;
    # afterward all assignment changes maintain team sizes, using blank slots if necessary.
    def assign_unit(self, unit: Unit, new_owner: int):
        self.team_sizes[unit.owner] -= 1
        unit.owner = new_owner
        self.team_sizes[unit.owner] += 1

    def quick_assign(self):
        self.clear_assign()
        for unit in self.units:
            max_bid = -1
            for p, bid in enumerate(unit.bids):
                if self.team_sizes[p] < self.max_team_size and max_bid < bid:
                    max_bid = bid
                    self.assign_unit(unit, p)

    # assign units in order of satisfaction, not recruitment
    def max_sat_assign(self):
        print()
        print('---Initial assignments---')
        self.clear_assign()
        while self.team_sizes[-1] > 0:  # unassigned units remain
            max_sat = -999
            max_sat_unit = Unit('NULL', -1)
            max_sat_player = -1
            for unit in self.units:
                if unit.owner == -1:
                    for p, bid in enumerate(unit.bids):
                        sat = pricing.comp_sat(unit.bids, p)
                        if self.team_sizes[p] < self.max_team_size and max_sat < sat:
                            max_sat = sat
                            max_sat_unit = unit
                            max_sat_player = p

            self.assign_unit(max_sat_unit, max_sat_player)
            print(f'{max_sat_unit.name:12s} to {max_sat_player} {self.players[max_sat_player]:12s}')

    # P x S
    def teams(self):
        teams = [[] for player in self.players]

        for unit in self.units:
            teams[unit.owner].append(unit)
        return teams

    def print_teams(self):
        print('\n---Teams---')
        for player in self.players:
            print(f'{player:12s}', end=' ')
        print()

        teams = self.teams()
        for i in range(self.max_team_size):
            for team in teams:
                print(f'{(team[i].name[:12]):12s}', end=' ')
            print()

        for price in self.handicaps():
            print(f'{price:5.2f}       ', end=' ')
        print()

    # How player i values player j's team. No adjustments
    def value_matrix(self) -> Matrix:
        v_matrix = [([0] * len(self.players)) for player in self.players]

        for unit in self.units:
            for valuer_row, bid in zip(v_matrix, unit.bids):
                valuer_row[unit.owner] += bid

        return v_matrix

    # Could avoid recalculating in some circumstances, but these are not common;
    # at minimum, when a unit is reassigned, need to check for synergy relationship with new teammates;
    # also when leaving a team; can't save from that unit's prior swap because other teammates may have changed.
    # Depends on synergy relationship graph density, but on tests with FE8:
    # 54993/55440 calls to synergy_matrix() required a recalculation, implying very few reassignments meet
    # the circumstances of having no former or current teammates as connected to any moving unit.
    # If no synergy relationships, much faster on FE6, but cannot conclude any speedup in general.
    # Could also only update rows/columns of affected players, but most time is all-player rotations
    def synergy_matrix(self) -> Matrix:
        s_matrix = [([0] * len(self.players)) for player in self.players]

        teams = self.teams()
        for u_i in range(self.max_team_size):
            for u_j in range((u_i+1), self.max_team_size):
                for player_i, synergies in enumerate(self.synergies):
                    for player_j, team in enumerate(teams):
                        s_matrix[player_i][player_j] += synergies[team[u_i].recruit_order][team[u_j].recruit_order]

        return s_matrix

    def v_s_matrix(self) -> Matrix:
        v_matrix = self.value_matrix()
        s_matrix = self.synergy_matrix()
        for v_row, s_row in zip(v_matrix, s_matrix):
            for i in range(len(v_row)):
                v_row[i] += s_row[i]
                v_row[i] = max(0.0, v_row[i])  # team value should never be negative
        return v_matrix

    # Adjusted for synergy and redundancy
    def final_matrix(self) -> Matrix:
        return pricing.apply_redundancy(self.v_s_matrix(), self.bid_sums)

    def handicaps(self) -> List[float]:
        return pricing.pareto_prices(self.final_matrix())

    # Print matrix, comp_sat, handicaps, and matrix+sat after handicapping
    def print_value_matrices(self):
        def print_matrix(m: Matrix, string: str):
            print()
            print(string)
            for p, row in enumerate(m):
                print(f'{self.players[p]:10s}', end=' ')
                for i, value in enumerate(row):
                    print(f' {value:6.2f}   ', end=' ')
                print(f' {pricing.comp_sat(row, p):6.2f}')

        print()
        print('          ', end=' ')
        for player in self.players:
            print(f'{player:10s}', end=' ')
        print('Comparative satisfaction')

        print_matrix(self.value_matrix(), 'Unadjusted value matrix')

        print_matrix(self.synergy_matrix(), 'Synergy')

        print_matrix(self.v_s_matrix(), 'Synergy adjusted')

        final_matrix = self.final_matrix()
        print_matrix(final_matrix, 'Redundancy adjusted')

        robustness = 0
        for p, row in enumerate(final_matrix):
            for i, value in enumerate(row):
                if p == i:
                    robustness += value

        print()
        print(f'Average team robustness: {robustness/len(self.players):6.2f}')

        print('HANDICAPS:', end=' ')
        prices = self.handicaps()
        for price in prices:
            print(f' {price:6.2f}   ', end=' ')
        print()
        print()

        print('Handicap adjusted')
        for p, row in enumerate(final_matrix):
            print(f'{self.players[p]:10s}', end=' ')
            for value, price in zip(row, prices):
                print(f' {value - price:6.2f}   ', end=' ')
            print(f' {pricing.comp_sat(row, p) - pricing.comp_sat(prices, p):6.2f}')

    def get_score(self):
        return pricing.allocation_score(self.final_matrix(), self.robust_factor)

    # try all swaps to improve score
    def improve_allocation_swaps(self) -> bool:
        current_score = self.get_score()
        swapped = False

        for u_i, unit_i in enumerate(self.units):
            for unit_j in self.units[u_i+1:]:
                if unit_i.owner != unit_j.owner:
                    unit_i.owner, unit_j.owner = unit_j.owner, unit_i.owner

                    if current_score < self.get_score():
                        current_score = self.get_score()
                        swapped = True
                        # Use name of owner before swap
                        print(f'Swapping {self.players[unit_j.owner]:12s} '
                              f'{(unit_i.name[:12]):12s} <-> {(unit_j.name[:12]):12s} '
                              f'{self.players[unit_i.owner]:12s}, '
                              f'new score {current_score:7.3f}')
                    else:  # return units to owners
                        unit_i.owner, unit_j.owner = unit_j.owner, unit_i.owner
        return swapped

    # try all rotations (swaps of three or more) to improve score
    # iterate over rotations at the highest level,
    # skip branching tree if player at that level of recursion isn't trading
    # only full p rotations will cost much time

    # If this didn't rotate from rotations[test_until], only need to check until that point:
    # Complete one "lap" without any successful rotation, lap doesn't need to start at rotation[0]
    # Set last_rotation to index r whenever a rotation occurs to pass to next execution.
    def improve_allocation_rotate(self, test_until: int) -> int:
        start = time.time()

        current_score = self.get_score()
        last_rotation = -1

        indices = [0]*len(self.players)  # of units being traded from 0~teamsize-1, set during recursive_rotate branch
        teams = self.teams()

        def recursive_rotate(p_i):
            nonlocal teams
            nonlocal current_score
            nonlocal last_rotation

            if p_i >= len(self.players):  # base case
                for p in trading_players:
                    teams[p][indices[p]].owner = rotation[p]  # p's unit goes to rotation[p]

                if current_score < self.get_score():
                    current_score = self.get_score()

                    print('\nRotating:')
                    for p2 in trading_players:
                        print(f'{self.players[p2]:12s} -> '
                              f'{(teams[p2][indices[p2]].name[:12]):12s} -> '
                              f'{self.players[rotation[p2]]:12s}')
                    print(f'New score {current_score:7.3f}')
                    print()

                    while self.improve_allocation_swaps():
                        pass
                    current_score = self.get_score()

                    teams = self.teams()
                    last_rotation = r
                else:
                    for p in trading_players:
                        teams[p][indices[p]].owner = p  # unrotate, if teams were updated rotates to new teams

            else:
                if p_i in trading_players:
                    for indices[p_i] in range(self.max_team_size):  # for each unit in the team
                        recursive_rotate(p_i + 1)
                else:  # don't branch, this player isn't trading in this rotation, go to next player
                    recursive_rotate(p_i + 1)

        for r, rotation in enumerate(self.rotations):
            if r > test_until and last_rotation < 0:
                print('Reached latest effected rotation of prior loop. Stopping rotation early.')
                return last_rotation

            trading_players = [p for p, r in enumerate(rotation) if p != r]
            print(f'{time.time() - start:7.2f} {r:3d}/{len(self.rotations):3d}  '
                  'Rotation ', rotation, '  Trading players ', trading_players)
            recursive_rotate(0)

        return last_rotation

    def run(self):
        directories = [_[0] for _ in read_grid('directories.txt', str)]

        self.players = read_grid(directories[0], str)[0]
        self.rotations = [p for p in itertools.permutations(range(len(self.players))) if pricing.just_one_loop(p)]

        self.units = [Unit(row[0], i) for i, row in enumerate(read_grid(directories[1], str))]

        bids = read_grid(directories[2], float)
        extend_array(bids, len(self.units), [0] * len(self.players))

        self.bid_sums = [0] * len(self.players)
        for unit, bid_row in zip(self.units, bids):
            # if fewer than max players, create dummy players from existing bids
            while len(bid_row) < len(self.players):
                bid_row.append(statistics.median(bid_row) * random.triangular(.9, 1.1))

            for i, bid in enumerate(bid_row):
                self.bid_sums[i] += bid

            unit.bids = bid_row

        self.synergies = []
        for filename in directories[3:]:
            synergies = read_grid(filename, float)
            extend_array(synergies, len(self.units), [0] * len(self.units))
            for row in synergies:
                extend_array(row, len(self.units), 0)
            self.synergies.append(synergies)

        while len(self.synergies) < len(self.players):
            self.set_median_synergy()

        # TODO remove least valued units until len(units) % len(players) == 0

        self.max_team_size = len(self.units)//len(self.players)
        self.max_sat_assign()
        self.print_bids()
        self.print_synergy(0)

        while self.improve_allocation_swaps():
            pass

        test_until = len(self.rotations)
        while test_until >= 0:
            test_until = self.improve_allocation_rotate(test_until)

        self.print_value_matrices()
        self.print_teams()


test = AuctionState()

# cProfile.run('test.run()', sort='cumulative')
test.run()
