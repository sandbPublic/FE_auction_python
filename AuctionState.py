import GameData
import Pricing
import itertools
import time
import statistics
import random


def extend_array(array, length, filler):
    while len(array) < length:
        array.append(filler)


class AuctionState:
    def __init__(self, players):
        self.players = players
        self.max_team_size = len(GameData.units)//len(players)
        self.opp_ratio = 1 - 1/len(players)  # used in pricing functions
        self.team_sizes = []  # index -1 for unassigned

        self.robust_factor = 0.125  # bias in favor of good teams rather than expected victory
        # index by player last for printing/reading and for consistency
        self.bids = []  # U x P, indexing for reading files/printing
        self.bid_sums = [0] * len(players)  # P, used for redundancy adjusted team values
        self.MC_matrix = []  # C x P, M values by chapter
        self.unit_value_per_chapter = []  # U x P, unmodified by promo items

        self.synergies = []
        # P x U x U, players choose value to reduce/increase value of unit pairs
        # generally negative for redundant units
        # increment value of team by manual_synergy[i][j][valuer] if i and j on same team
        # should be triangular matrix since synergy i<->j == j<->i

        self.synergy_relationship_graph = [set() for i in range(len(GameData.units))]

        self.rotations = [p for p in itertools.permutations(range(len(players))) if Pricing.just_one_loop(p)]

    def read_bids(self, bid_file_name):
        try:
            self.bid_sums = [0] * len(self.players)
            self.bids = []

            bid_file = open(bid_file_name, 'r')
            for line in bid_file.readlines():
                next_bid_row = [float(i) for i in line.split()]

                if len(next_bid_row) > 0:  # skip empty lines
                    # if fewer than max players, create dummy players from existing bids
                    while len(next_bid_row) < len(self.players):
                        next_bid_row.append(statistics.median(next_bid_row) * random.triangular(0.8, 1.2))

                    self.bids.append(next_bid_row)

                    for i, bid in enumerate(next_bid_row):
                        self.bid_sums[i] += bid

            bid_file.close()
            extend_array(self.bids, len(GameData.units), [0] * len(self.players))

        except ValueError as error:
            print(error)
        except FileNotFoundError as error:
            print(error)

    def print_bids(self):
        print('--BIDS--       ', end=' ')
        for player in self.players:
            print(f'{player:10s}', end=' ')
        print()

        for bid_row, unit in zip(self.bids, GameData.units):
            unit_line = f'{unit.name:15s}'
            for bid in bid_row:
                unit_line += f' {bid:5.2f}     '
            print(unit_line)

    def read_synergy(self, synergy_file_name):
        try:
            print(f'Reading synergy values from {synergy_file_name:s}.')
            synergy_file = open(synergy_file_name, 'r')
            player_synergies = []
            for line in synergy_file.readlines():
                next_line = [float(i) for i in line.split()]
                extend_array(next_line, len(GameData.units), 0)
                player_synergies.append(next_line)

            extend_array(player_synergies, len(GameData.units), [0] * len(GameData.units))

            for u_i, synergy_row in enumerate(player_synergies):
                for u_j, syn in enumerate(synergy_row):
                    if syn != 0:
                        self.synergy_relationship_graph[u_i].add(u_j)
                        self.synergy_relationship_graph[u_j].add(u_i)

            self.synergies.append(player_synergies)
            synergy_file.close()

        except ValueError as error:
            print(error)
        except FileNotFoundError as error:
            print(error)

    def set_median_synergy(self):
        player_synergies = []
        for u_i in range(len(GameData.units)):
            next_synergy_row = []
            for u_j in range(len(GameData.units)):
                next_synergy_row.append(statistics.median([synergy[u_i][u_j] for synergy in self.synergies]))
            player_synergies.append(next_synergy_row)
        self.synergies.append(player_synergies)

    # checks that populated section of the matrix is triangular
    def print_synergy(self, player_i):
        print(f'  Synergies for {self.players[player_i]:10s}')

        for u_i in range(len(GameData.units)):
            something_to_print = False
            unit_line = f'{GameData.units[u_i].name:12s}: '
            for u_j, synergy in enumerate(self.synergies[player_i][u_i]):
                if synergy != 0:
                    something_to_print = True
                    unit_line += f' {GameData.units[u_j].name:12s}{synergy:5.2f} '
                    if u_j <= u_i:
                        print('NOTE, synergy matrix not triangular, possible error')
            if something_to_print:
                print(unit_line)

    # C x P matrix of each player's max team value on a chapter basis.
    # Divide each unit's value (bid) evenly across each chapter it is present.
    # Account for promo item competition reducing values of late promoters.
    def create_max_chapter_values(self):
        self.MC_matrix = [[0] * len(self.players) for chapter in GameData.chapters]

        self.unit_value_per_chapter = []
        for u, unit in enumerate(GameData.units):
            self.unit_value_per_chapter.append([])
            for p in range(len(self.players)):
                uvpc = self.bids[u][p] / (len(GameData.chapters) - unit.join_chapter)
                self.unit_value_per_chapter[u].append(uvpc)
                for c in range(unit.join_chapter, len(GameData.chapters)):
                    if unit.late_promo_factors:
                        # assume max competition when creating max values
                        self.MC_matrix[c][p] += uvpc * unit.late_promo_factors[-1][c]
                    else:
                        self.MC_matrix[c][p] += uvpc

    def print_max_chapter_values(self):
        print('\n---Max values by chapter---')
        for player in self.players:
            print(f'{player:10s}', end=' ')
        print()

        for row, chapter in zip(self.MC_matrix, GameData.chapters):
            for m in row:
                print(f' {m:6.2f}   ', end=' ')
            print(chapter)

    def clear_assign(self):
        self.team_sizes = [0] * len(self.players)
        self.team_sizes.append(len(GameData.units))  # all unassigned (team -1)

        for unit in GameData.units:
            unit.owner = -1

    # Only need to track team size during initial assignment;
    # afterward all assignment changes maintain team sizes, using blank slots if necessary.
    def assign_unit(self, unit, new_owner):
        unit.set_owner(new_owner)
        self.team_sizes[unit.prior_owner] -= 1
        self.team_sizes[unit.owner] += 1

    def quick_assign(self):
        self.clear_assign()
        for bid_row, unit in zip(self.bids, GameData.units):
            max_bid = -1
            for p, bid in enumerate(bid_row):
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
            max_sat_unit = -1
            max_sat_player = -1
            for u, bid_row in enumerate(self.bids):
                if GameData.units[u].owner == -1:
                    for p, bid in enumerate(bid_row):
                        sat = Pricing.comp_sat(bid_row, p)
                        if self.team_sizes[p] < self.max_team_size and max_sat < sat:
                            max_sat = sat
                            max_sat_unit = u
                            max_sat_player = p

            self.assign_unit(GameData.units[max_sat_unit], max_sat_player)
            print(f'{GameData.units[max_sat_unit].name:12s} to {max_sat_player} {self.players[max_sat_player]:12s}')

    # P x S
    def teams(self):
        teams = [[] for player in self.players]

        for unit in GameData.units:
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

    def print_teams_detailed(self):
        print('\n---Teams detailed---', end='')

        teams = self.teams()
        prices = self.handicaps()
        for team, player, price in zip(teams, self.players, prices):
            print(f'\n{player}')
            for member in team:
                print(f'{member.name:12s} | '
                      f'{GameData.promo_strings[member.promo_type]} | '
                      f'{GameData.chapters[member.join_chapter]:30s}')
            print(f'Handicap: {price:5.2f}')
        print()

    # How player i values player j's team. No adjustments
    def value_matrix(self):
        v_matrix = [([0] * len(self.players)) for player in self.players]

        for valuer_i, valuer_row in enumerate(v_matrix):
            for unit, bid_row in zip(GameData.units, self.bids):
                valuer_row[unit.owner] += bid_row[valuer_i]

        return v_matrix

    # Could avoid recalculating in some circumstances, but these are not common;
    # at minimum, when a unit is reassigned, need to check for synergy relationship with new teammates;
    # also when leaving a team; can't save from that unit's prior swap because other teammates may have changed.
    # Depends on synergy relationship graph density, but on tests with FE8:
    # 54993/55440 calls to synergy_matrix() required a recalculation, implying very few reassignments meet
    # the circumstances of having no former or current teammates as connected to any moving unit.
    # If no synergy relationships, much faster on FE6, but cannot conclude any speedup in general.
    # Could also only update rows/columns of affected players, but most time is all-player rotations
    def synergy_matrix(self):
        s_matrix = [([0] * len(self.players)) for player in self.players]

        teams = self.teams()
        for u_i in range(self.max_team_size):
            for u_j in range((u_i+1), self.max_team_size):
                for player_i, synergies in enumerate(self.synergies):
                    for player_j, team in enumerate(teams):
                        s_matrix[player_i][player_j] += synergies[team[u_i].ID][team[u_j].ID]

        return s_matrix

    def v_s_matrix(self):
        v_matrix = self.value_matrix()
        s_matrix = self.synergy_matrix()
        for v_row, s_row in zip(v_matrix, s_matrix):
            for i in range(len(v_row)):
                v_row[i] += s_row[i]
                v_row[i] = max(0, v_row[i])
        return v_matrix

    # Adjusted for synergy and redundancy
    def final_matrix(self):
        return Pricing.apply_redundancy(self.v_s_matrix(), self.bid_sums, self.opp_ratio)

    def handicaps(self):
        return Pricing.pareto_prices(self.final_matrix(), self.opp_ratio)

    # Sum of values adjusted for redundancy for each chapter.
    # Also adjusted for promo competition
    def value_matrix_by_chapter(self):
        v_matrix = [([0] * len(self.players)) for player in self.players]

        for unit_c in GameData.units_with_competitors:
            unit_c.set_current_competitors()

        for c, MC_row in enumerate(self.MC_matrix):
            for p_i in range(len(self.players)):
                team_values_this_chapter = [0] * len(self.players)

                for unit, uvpc in zip(GameData.units, self.unit_value_per_chapter):
                    if unit.join_chapter <= c:
                        if unit.current_competitors == 0:
                            team_values_this_chapter[unit.owner] += uvpc[p_i]
                        else:
                            team_values_this_chapter[unit.owner] += uvpc[p_i] * unit.get_late_promo_factor(c)
                    else:  # all subsequent units have not appeared yet
                        break

                for p_j in range(len(self.players)):
                    v_matrix[p_i][p_j] += Pricing.redundancy(
                        team_values_this_chapter[p_j], MC_row[p_i], self.opp_ratio)

        return v_matrix

    # Print matrix, comp_sat, handicaps, and matrix+sat after handicapping
    def print_value_matrices(self):
        def print_matrix(m, string):
            print()
            print(string)
            for p, row in enumerate(m):
                print(f'{self.players[p]:10s}', end=' ')
                for i, value in enumerate(row):
                    print(f' {value:6.2f}   ', end=' ')
                print(f' {Pricing.comp_sat(row, p):6.2f}')

        print()
        print('          ', end=' ')
        for player in self.players:
            print(f'{player:10s}', end=' ')
        print('Comparative satisfaction')

        print_matrix(self.value_matrix(), 'Unadjusted value matrix')

        print_matrix(self.synergy_matrix(), 'Synergy')

        print_matrix(self.v_s_matrix(), 'Synergy adjustments')

        final_matrix = self.final_matrix()
        print_matrix(final_matrix, 'Redundancy adjustments')

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

        print('Handicap adjustments')
        for p, row in enumerate(final_matrix):
            print(f'{self.players[p]:10s}', end=' ')
            for value, price in zip(row, prices):
                print(f' {value - price:6.2f}   ', end=' ')
            print(f' {Pricing.comp_sat(row, p) - Pricing.comp_sat(prices, p):6.2f}')

    def get_score(self):
        return Pricing.allocation_score(self.final_matrix(), self.robust_factor)

    # try all swaps to improve score
    def improve_allocation_swaps(self):
        current_score = self.get_score()
        swapped = False

        for u_i, unit_i in enumerate(GameData.units):
            for unit_j in GameData.units[u_i+1:]:
                if unit_i.owner != unit_j.owner:
                    unit_i.set_owner(unit_j.owner)
                    unit_j.set_owner(unit_i.prior_owner)

                    if current_score < self.get_score():
                        current_score = self.get_score()
                        swapped = True
                        # Use name of owner before swap
                        print(f'Swapping {self.players[unit_j.owner]:12s} '
                              f'{unit_i.name:12s} <-> {unit_j.name:12s} '
                              f'{self.players[unit_i.owner]:12s}, '
                              f'new score {current_score:6.2f}')
                    else:  # return units to owners
                        unit_i.set_owner(unit_j.owner)
                        unit_j.set_owner(unit_i.prior_owner)
        return swapped

    # try all rotations (swaps of three or more) to improve score
    # iterate over rotations at the highest level,
    # skip branching tree if player at that level of recursion isn't trading
    # only full p rotations will cost much time

    # If this didn't rotate from rotations[test_until], only need to check until that point:
    # Complete one "lap" without any successful rotation, lap doesn't need to start at rotation[0]
    # Set last_rotation to index r whenever a rotation occurs to pass to next execution.
    def improve_allocation_rotate(self, test_until):
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
                    teams[p][indices[p]].set_owner(rotation[p])  # p's unit goes to rotation[p]

                if current_score < self.get_score():
                    current_score = self.get_score()

                    print('\nRotating:')
                    for p2 in trading_players:
                        print(f'{self.players[p2]:12s} -> '
                              f'{teams[p2][indices[p2]].name:12s} -> '
                              f'{self.players[rotation[p2]]:12s}')
                    print(f'New score {current_score:6.2f}')
                    print()

                    while self.improve_allocation_swaps():
                        pass
                    current_score = self.get_score()

                    teams = self.teams()
                    last_rotation = r
                else:
                    for p in trading_players:
                        teams[p][indices[p]].set_owner(p)  # unrotate, if teams were updated rotates to new teams

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
        self.print_bids()
        self.max_sat_assign()

        while self.improve_allocation_swaps():
            pass

        test_until = len(self.rotations)
        while test_until >= 0:
            test_until = self.improve_allocation_rotate(test_until)

        self.print_teams()
        self.print_value_matrices()
