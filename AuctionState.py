import pricing
import misc
import statistics
import random
# import cProfile
from typing import List, Tuple
import os
Matrix = List[List[float]]


class Unit:
    def __init__(self, name: str, recruit_order: int):
        self.name = name
        self.recruit_order = recruit_order
        self.owner = -1
        self.bids = []
        # whenever iterating over bids, we also iterate over Units
        # Simplify loops and save on zips by storing the bids in the Units


class AuctionState:
    def __init__(self):
        self.players = []
        self.units = []

        self.max_team_size = 0

        # index by player last for printing/reading and for consistency
        # used for redundancy adjusted team values
        self.bid_sums = []

        self.synergies = []
        # P x U x U, players choose value to reduce/increase value of unit pairs
        # generally negative for redundant units
        # increment value of team by manual_synergy[i][j][valuer] if i and j on same team
        # should be triangular matrix since synergy i<->j == j<->i

        self.game_dir = ''
        self.auct_dir = ''
        self.log_strings = []
        self.logs_written = 0

    # need to print as the auction runs, not just when a log is ready for the next output file
    def print_and_log(self, text: str):
        print(text)
        self.log_strings.append(text)

    def write_logs(self, filename: str):
        print()
        file = open(f'{self.auct_dir}output/{self.logs_written:02d}_{filename}.txt', 'w')
        file.write('\n'.join(self.log_strings))
        file.close()
        self.log_strings = []
        self.logs_written += 1
    
    def format_bids(self):
        self.print_and_log('--BIDS--        ' + ' '.join([f'{player:10s}' for player in self.players]))
        for unit in self.units:
            self.print_and_log(f'{unit.name:15s}' + ' '.join([f' {bid:5.2f}    ' for bid in unit.bids]))

    def set_median_synergy(self):
        print(f'Setting median synergies for {self.players[len(self.synergies)]}')
        player_synergies = []
        for u_i in range(len(self.units)):
            next_synergy_row = []
            for u_j in range(len(self.units)):
                next_synergy_row.append(statistics.median([synergy[u_i][u_j] for synergy in self.synergies]))
            player_synergies.append(next_synergy_row)
        self.synergies.append(player_synergies)

    # checks that populated section of the matrix is triangular
    def format_synergy(self, player_i: int):
        self.print_and_log(f'  Synergies for {self.players[player_i]}')

        for u_i in range(len(self.units)):
            something_to_print = False
            unit_line = f'{self.units[u_i].name:12s}: '
            for u_j, synergy in enumerate(self.synergies[player_i][u_i]):
                if synergy != 0:
                    something_to_print = True
                    unit_line += f' {self.units[u_j].name:12s}{synergy:5.2f} '
                    if u_j <= u_i:
                        self.print_and_log('NOTE, synergy matrix not triangular, possible error')
            if something_to_print:
                self.print_and_log(unit_line)

    def remove_least_valued_unit(self):
        least_value = 99999
        least_value_i = -1
        for unit in self.units:
            if least_value > sum(unit.bids):
                least_value = sum(unit.bids)
                least_value_i = unit.recruit_order

        for unit in self.units[least_value_i:]:
            unit.recruit_order -= 1

        self.print_and_log(f'Removing least valued: {self.units[least_value_i].name} {least_value/len(self.players)}')
        self.units.pop(least_value_i)
        for player_synergy in self.synergies:
            player_synergy.pop(least_value_i)
            for row in player_synergy:
                row.pop(least_value_i)

    # assign units in order of satisfaction, not recruitment
    def format_initial_assign(self):
        self.print_and_log('---Initial assignments---')

        team_sizes = [0] * len(self.players)
        team_sizes.append(len(self.units))  # all unassigned (team -1)

        for unit in self.units:
            unit.owner = -1
        
        while team_sizes[-1] > 0:  # unassigned units remain
            max_sat = -99999
            max_sat_unit = Unit('NULL', -1)
            max_sat_player = -1
            for unit in self.units:
                if unit.owner == -1:
                    for p, bid in enumerate(unit.bids):
                        sat = pricing.comp_sat(unit.bids, p)
                        if team_sizes[p] < self.max_team_size and max_sat < sat:
                            max_sat = sat
                            max_sat_unit = unit
                            max_sat_player = p

            team_sizes[max_sat_unit.owner] -= 1
            max_sat_unit.owner = max_sat_player
            team_sizes[max_sat_unit.owner] += 1
            self.print_and_log(f'{max_sat_unit.name:12s} to {max_sat_player} {self.players[max_sat_player]:12s}')

    def teams(self) -> List[List[Unit]]:
        teams = [[] for _ in self.players]

        for unit in self.units:
            teams[unit.owner].append(unit)
        return teams

    def format_teams(self):
        self.print_and_log('---Teams---')
        self.print_and_log(' '.join([f'{player:12s}' for player in self.players]))

        teams = self.teams()
        for i in range(self.max_team_size):
            self.print_and_log(' '.join([f'{(team[i].name[:12]):12s}' for team in teams]))

        self.print_and_log(' '.join([f'{price:5.2f}       ' for price in self.handicaps()]))

    # How player i values player j's team. No adjustments
    def value_matrix(self) -> Matrix:
        v_matrix = [([0] * len(self.players)) for _ in self.players]

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
        s_matrix = [([0] * len(self.players)) for _ in self.players]

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
    def format_value_matrices(self):
        self.print_and_log('           ' +
                           ' '.join([f'{player:10s}' for player in self.players]) +
                           ' Comparative satisfaction')

        def print_matrix(mat: Matrix, string: str):
            self.print_and_log('')
            self.print_and_log(string)
            for p, row in enumerate(mat):
                self.print_and_log(f'{self.players[p]:10s} ' +
                                   ' '.join([f' {value:6.2f}   ' for value in row]) +
                                   f'  {pricing.comp_sat(row, p):6.2f}')

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

        self.print_and_log('')
        self.print_and_log(f'Average team robustness: {robustness/len(self.players):6.2f}')

        prices = self.handicaps()

        self.print_and_log('HANDICAPS: ' + ' '.join([f' {price:6.2f}   ' for price in prices]))
        self.print_and_log('')

        self.print_and_log('Handicap adjusted')
        for p, row in enumerate(final_matrix):
            self.print_and_log(f'{self.players[p]:10s} ' +
                               ' '.join([f' {value - price:6.2f}   ' for value, price in zip(row, prices)]) +
                               f'  {pricing.comp_sat(row, p) - pricing.comp_sat(prices, p):6.2f}')

    def get_score(self):
        return pricing.allocation_score(self.final_matrix(), 0.25)

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
                        self.print_and_log(f'Swapping {self.players[unit_j.owner]:12s} '
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
    def improve_allocation_rotate(self, test_until_i: int, rotations: List[Tuple[int]]) -> int:
        current_score = self.get_score()
        last_rotation_i = -1

        indices = [0]*len(self.players)  # of units being traded from 0~teamsize-1, set during recursive_rotate branch
        teams = self.teams()

        def recursive_rotate(p_i):
            nonlocal teams
            nonlocal current_score
            nonlocal last_rotation_i

            if p_i >= len(self.players):  # base case
                for p in trading_players:
                    teams[p][indices[p]].owner = rotation[p]  # p's unit goes to rotation[p]

                if current_score < self.get_score():
                    current_score = self.get_score()

                    self.print_and_log('')
                    self.print_and_log('Rotating:')
                    for p2 in trading_players:
                        self.print_and_log(f'{self.players[p2]:12s} -> '
                                                f'{(teams[p2][indices[p2]].name[:12]):12s} -> '
                                                f'{self.players[rotation[p2]]:12s}')
                    self.print_and_log(f'New score {current_score:7.3f}')
                    self.print_and_log('')

                    while self.improve_allocation_swaps():
                        pass
                    current_score = self.get_score()

                    teams = self.teams()
                    last_rotation_i = r_i
                else:
                    for p in trading_players:
                        teams[p][indices[p]].owner = p  # unrotate, if teams were updated rotates to new teams

            else:
                if p_i in trading_players:
                    for indices[p_i] in range(self.max_team_size):  # for each unit in the team
                        recursive_rotate(p_i + 1)
                else:  # don't branch, this player isn't trading in this rotation, go to next player
                    recursive_rotate(p_i + 1)

        for r_i, rotation in enumerate(rotations):
            if r_i > test_until_i and last_rotation_i < 0:
                self.print_and_log('Reached latest effected rotation of prior loop. Stopping rotation early.')
                return last_rotation_i

            trading_players = [p for p, r in enumerate(rotation) if p != r]
            self.print_and_log(f'{r_i:3d}/{len(rotations):3d}  '
                               f'Rotation {rotation}  '
                               f'Trading players {trading_players}')
            recursive_rotate(0)

        return last_rotation_i

    def load(self):
        # directories.txt contains paths as first word, subsequent words may be comments
        # 1st line is game directory, 2nd auction dir, subsequent are synergy filenames
        directories = [d[0] for d in misc.read_grid('directories.txt', str)]
        self.game_dir = directories[0]
        self.auct_dir = directories[1]

        self.units = [Unit(row[0], i) for i, row in enumerate(misc.read_grid(f'{self.game_dir}units.txt', str))]
        self.players = misc.read_grid(f'{self.auct_dir}players.txt', str)[0]
        self.max_team_size = len(self.units) // len(self.players)
        bids = misc.read_grid(f'{self.auct_dir}bids.txt', float)
        misc.extend_array(bids, len(self.units), [0] * len(self.players))
        self.bid_sums = [0] * len(self.players)

        for unit, bid_row in zip(self.units, bids):
            # if fewer than max players, create dummy players from existing bids
            while len(bid_row) < len(self.players):
                bid_row.append(statistics.median(bid_row) * random.triangular(.9, 1.1))
            for i, bid in enumerate(bid_row):
                self.bid_sums[i] += bid
            unit.bids = bid_row

        self.synergies = []
        for filename in directories[2:]:
            next_synergies = misc.read_grid(f'{self.auct_dir}{filename}.txt', float)
            misc.extend_array(next_synergies, len(self.units), [0] * len(self.units))
            for row in next_synergies:
                misc.extend_array(row, len(self.units), 0)
            self.synergies.append(next_synergies)

        while len(self.synergies) < len(self.players):
            self.set_median_synergy()

    def run(self):
        self.load()

        # run and write

        if not os.path.exists(f'{self.auct_dir}output'):
            os.makedirs(f'{self.auct_dir}output')

        self.format_bids()
        self.write_logs('bids')

        for i, player in enumerate(self.players):
            self.format_synergy(i)
            self.write_logs(f'synergy{player}')

        while len(self.units) % len(self.players) != 0:
            self.remove_least_valued_unit()
        self.write_logs('remove_units')

        self.format_initial_assign()
        self.write_logs('initial_assign')

        while self.improve_allocation_swaps():
            pass

        rotations = misc.one_loop_permutations(len(self.players))
        test_until = len(rotations)
        while test_until >= 0:
            test_until = self.improve_allocation_rotate(test_until, rotations)

        self.write_logs('reassignments')

        self.format_value_matrices()
        self.write_logs('matrices')
        self.format_teams()
        self.write_logs('teams')


if __name__ == '__main__':
    test = AuctionState()
    # cProfile.run('test.run()', sort='cumulative')
    test.run()
