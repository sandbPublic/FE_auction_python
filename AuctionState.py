import GameData
import Pricing
import itertools
import time
import random


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

        self.manual_synergy = []  # U x U x P, players choose ratio to reduce/increase value of unit pairs
        # generally negative for redundant units
        # multiply value of unit i by manual_synergy[i][j][valuer] if i and j on same team
        self.synergy_ratios = []  # U x P, changes based on team allocation

        self.rotations = [p for p in itertools.permutations(range(len(players))) if Pricing.just_one_loop(p)]

    def read_bids(self, bid_file_name):
        try:
            self.bids = []
            bid_file = open(bid_file_name, 'r')
            for line in bid_file.readlines():
                next_bid_row = []
                unit_average = 0
                for i, item in enumerate(line.split()):
                    bid = float(item)
                    next_bid_row.append(bid)
                    self.bid_sums[i] += bid
                    unit_average += bid
                unit_average /= (i+1)

                while len(next_bid_row) < len(self.players):
                    next_bid_row.append(next_bid_row[1])  # median
                    # next_bid_row.append(unit_average * random.triangular(0.75, 1.25))

                self.bids.append(next_bid_row)
            bid_file.close()
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

    # todo
    def read_synergy(self, synergy_file_name):
        try:
            self.manual_synergy = [[[1] * len(self.players) for
                                    u_j in range(len(GameData.units))] for u_i in range(len(GameData.units))]
            # synergy_file = open(synergy_file_name, 'r')
            # for line in synergy_file.readlines():
            #     pass
            # synergy_file.close()

            for i in range(7):
                self.manual_synergy[0][i][0] = .8

        except ValueError as error:
            print(error)
        except FileNotFoundError as error:
            print(error)

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

    def assign_unit(self, unit, new_owner):
        self.team_sizes[unit.owner] -= 1
        unit.owner = new_owner
        self.team_sizes[unit.owner] += 1

    def quick_assign(self):
        self.clear_assign()
        for bid_row, unit in zip(self.bids, GameData.units):
            max_bid = -1
            for p, bid in enumerate(bid_row):
                if self.team_sizes[p] < self.max_team_size and max_bid < bid:
                    max_bid = bid
                    self.assign_unit(unit, p)

    # assign in max sat, not recruit order
    def max_sat_assign(self):
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

    def print_teams_detailed(self):
        print('\n---Teams detailed---', end='')

        teams = self.teams()
        for team, player in zip(teams, self.players):
            print(f'\n{player}')
            for member in team:
                print(f'{member.name:15s} | '
                      f'{GameData.promo_strings[member.promo_type]} | '
                      f'{GameData.chapters[member.join_chapter]:20s}  | '
                      f'{GameData.chapters[member.join_chapter]}')
        print()

    # How player i values player j's team. Adjusted for redundancy across the game.
    def value_matrix(self):
        v_matrix = [([0] * len(self.players)) for player in self.players]

        for valuer_i, valuer_row in enumerate(v_matrix):
            for u_j, bid_row in enumerate(self.bids):
                valuer_row[GameData.units[u_j].owner] += bid_row[valuer_i]

            for owner_j in range(len(self.players)):
                valuer_row[owner_j] = Pricing.redundancy(valuer_row[owner_j], self.bid_sums[valuer_i], self.opp_ratio)

        return v_matrix

    def set_synergy_ratios(self):
        teams = self.teams()
        self.synergy_ratios = [[0] * len(self.players) for unit in range(len(GameData.units))]

        for unit_i, bid_row in enumerate(self.bids):
            owner_j = GameData.units[unit_i].owner

            for valuer_j in range(len(self.players)):
                ratio = 1
                for teammate_k in teams[owner_j]:
                    ratio *= self.manual_synergy[unit_i][teammate_k.ID][valuer_j]

                self.synergy_ratios[unit_i][valuer_j] = ratio

    def print_synergy_ratios(self):
        print('\n---Synergy Ratios---')
        print(f'            ', end=' ')
        for player in self.players:
            print(f'{player:6s}', end=' ')
        print()

        for u_i, unit in enumerate(GameData.units):
            print(f'{unit.name[:12]:12s}', end=' ')
            for p_j in range(len(self.players)):
                print(f'{int(self.synergy_ratios[u_i][p_j] * 100):4d}% ', end='')
            print()

    # How player i values player j's team. Adjusted for redundancy across the game and manual synergy.
    def value_matrix_synergy(self):
        v_matrix = [([0] * len(self.players)) for player in self.players]
        self.set_synergy_ratios()

        for valuer_i, valuer_row in enumerate(v_matrix):
            for u_j in range(len(self.units)):
                valuer_row[GameData.units[u_j].owner] += self.synergy_ratios[u_j][valuer_i]

            for owner_j in range(len(self.players)):
                valuer_row[owner_j] = Pricing.redundancy(valuer_row[owner_j], self.bid_sums[valuer_i], self.opp_ratio)

        return v_matrix

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
    def print_value_matrix(self, v_matrix):
        print()
        print('          ', end=' ')
        for player in self.players:
            print(f'{player:10s}', end=' ')
        print('Comparative satisfaction')

        robustness = 0
        for p, row in enumerate(v_matrix):
            print(f'{self.players[p]:10s}', end=' ')
            for i, value in enumerate(row):
                print(f' {value:6.2f}   ', end=' ')
                if p == i:
                    robustness += value
            print(f' {Pricing.comp_sat(row, p):6.2f}')

        print()
        print(f'Average team robustness: {robustness/p:6.2f}')
        prices = Pricing.pareto_prices(v_matrix, self.opp_ratio)

        print('HANDICAPS:', end=' ')
        for price in prices:
            print(f' {price:6.2f}   ', end=' ')
        print()

        print()
        for p, row in enumerate(v_matrix):
            print(f'{self.players[p]:10s}', end=' ')
            for value, price in zip(row, prices):
                print(f' {value - price:6.2f}   ', end=' ')
            print(f' {Pricing.comp_sat(row, p) - Pricing.comp_sat(prices, p):6.2f}')

    def get_score(self):
        return Pricing.allocation_score(self.value_matrix(), self.robust_factor)

    # try all swaps to improve score
    def improve_allocation_swaps(self):
        current_score = self.get_score()
        swapped = False

        for u_i, unit_i in enumerate(GameData.units):
            for unit_j in GameData.units[u_i+1:]:
                if unit_i.owner != unit_j.owner:
                    unit_i.owner, unit_j.owner = unit_j.owner, unit_i.owner

                    if current_score < self.get_score():
                        current_score = self.get_score()
                        swapped = True
                        # Use name of owner before swap
                        print(f'Swapping {self.players[unit_j.owner]} '
                              f'{unit_i.name} <-> {unit_j.name} '
                              f'{self.players[unit_i.owner]}')
                        print(f'New score {current_score:6.2f}')
                        print()
                    else:
                        unit_i.owner, unit_j.owner = unit_j.owner, unit_i.owner
        return swapped

    # try all rotations (swaps of three or more) to improve score
    # iterate over rotations at the highest level,
    # skip branching tree if player at that level of recursion isn't trading
    # only full p rotations will cost much time
    def improve_allocation_rotate(self):
        start = time.time()

        current_score = self.get_score()
        rotated = False

        indices = [0]*len(self.players)
        teams = self.teams()

        def recursive_rotate(p_i):
            nonlocal teams
            nonlocal current_score
            nonlocal rotated

            if p_i >= len(self.players):  # base case
                for p in trading_players:
                    teams[p][indices[p]].owner = rotation[p]  # p's unit goes to rotation[p]

                if current_score < self.get_score():
                    current_score = self.get_score()

                    print('\nRotating:')
                    for p2 in trading_players:
                        print(f'{self.players[p2]:10s} -> '
                              f'{teams[p2][indices[p2]].name:10s} -> '
                              f'{self.players[rotation[p2]]:10s}')
                    print(f'New score {current_score:6.2f}')
                    print()

                    while self.improve_allocation_swaps():
                        pass
                    current_score = self.get_score()

                    teams = self.teams()
                    rotated = True
                else:
                    for p in trading_players:
                        teams[p][indices[p]].owner = p  # unrotate, if teams were updated rotates to new teams

            else:
                if p_i in trading_players:
                    for indices[p_i] in range(self.max_team_size):
                        recursive_rotate(p_i + 1)
                else:  # don't branch, this player isn't trading in this rotation
                    recursive_rotate(p_i + 1)

        for r, rotation in enumerate(self.rotations):
            trading_players = [p for p, r in enumerate(rotation) if p != r]
            print(f'{time.time() - start:7.2f} {r:3d}/{len(self.rotations):3d}  '
                  'Rotation ', rotation, '  Trading players ', trading_players)
            recursive_rotate(0)

        return rotated
