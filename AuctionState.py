import GameData
import Pricing
import itertools
import time


# todo save chapterwise values, update only for trading player/chapters after earliest trade


class AuctionState:
    def __init__(self, players):
        self.players = players
        self.max_team_size = len(GameData.units)//len(players)
        self.opp_ratio = 1 - 1/len(players)  # used in pricing functions
        self.team_sizes = []  # index -1 for unassigned

        # index by player last for printing/reading and for consistency
        self.bids = []  # U x P, indexing for reading files/printing
        self.bid_sums = [0] * len(players)  # P, used for redundancy adjusted team values
        self.MC_matrix = []  # C x P, M values by chapter
        self.unit_value_per_chapter = []  # U x P, unmodified by promo items

        # Memoize these; when a swap occurs, only update values for trading players
        # starting from chapter of earliest swap.
        # running_total_by_chapter[-1] == final value matrix
        self.value_matrix_by_chapter = []  # C x P x P
        self.running_total_by_chapter = []  # C x P x P
        for c in range(len(GameData.chapters)):
            self.value_matrix_by_chapter.append([[0] * len(players) for player in players])
            self.running_total_by_chapter.append([[0] * len(players) for player in players])

        # save these so that, after a trade,
        # ownership can quickly be reverted without updating values,
        # but the next trade will update the reversion as well
        self.prev_chapter_update = 0
        self.prev_players_trading = set(range(len(players)))

        self.rotations = [p for p in itertools.permutations(range(len(players))) if Pricing.just_one_loop(p)]

    def read_bids(self, bid_file_name):
        try:
            bid_file = open(bid_file_name, 'r')
            for line in bid_file.readlines():
                next_bid_row = []
                for i, item in enumerate(line.split()):
                    next_bid_row.append(float(item))
                    self.bid_sums[i] += float(item)
                self.bids.append(next_bid_row)
            bid_file.close()
        except ValueError as error:
            print(error)
        except FileNotFoundError as error:
            print(error)

    def print_bids(self):
        print('BIDS           ', end=' ')
        for player in self.players:
            print(f'{player:10s}', end=' ')
        print()

        for bid_row, unit in zip(self.bids, GameData.units):
            unit_line = f'{unit.name:15s}'
            for bid in bid_row:
                unit_line += f' {bid:5.2f}     '
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
        print('\n---TEAMS---')
        for player in self.players:
            print(f'{player:12s}', end=' ')
        print()

        teams = self.teams()
        for i in range(self.max_team_size):
            for team in teams:
                print(f'{(team[i].name[:12]):12s}', end=' ')
            print()

    def print_teams_detailed(self):
        print('\n---TEAMS---', end='')

        teams = self.teams()
        for team, player in zip(teams, self.players):
            print(f'\n{player}')
            for member in team:
                print(f'{member.name:15s} | '
                      f'{GameData.promo_strings[member.promo_type]} | '
                      f'{GameData.chapters[member.join_chapter]}')

    # How player i values player j's team. Adjusted for redundancy across the game.
    def value_matrix(self):
        v_matrix = [([0] * len(self.players)) for player in self.players]

        for p_i in range(len(self.players)):
            for u_j, bid_row in enumerate(self.bids):
                v_matrix[p_i][GameData.units[u_j].owner] += bid_row[p_i]

            for p_j in range(len(self.players)):
                v_matrix[p_i][p_j] = Pricing.redundancy(v_matrix[p_i][p_j], self.bid_sums[p_i], self.opp_ratio)

        return v_matrix

    # Sum of values adjusted for redundancy for each chapter.
    # Also adjusted for promo competition
    def value_matrix_by_chapter_fn(self):
        v_matrix = [([0] * len(self.players)) for player in self.players]
        promo_competitors = [0] * len(GameData.units)

        for u_i in range(len(GameData.units)):
            for u_j in range(u_i + 1, len(GameData.units)):
                if GameData.units[u_i].competitor(GameData.units[u_j]):
                    promo_competitors[u_j] += 1

        for p_i in range(len(self.players)):
            for c in range(len(GameData.chapters)):
                team_values_this_chapter = [0] * len(self.players)

                for unit, uvpc, comp in zip(GameData.units, self.unit_value_per_chapter, promo_competitors):
                    if unit.join_chapter <= c:
                        if comp == 0:
                            team_values_this_chapter[unit.owner] += uvpc[p_i]
                        else:
                            team_values_this_chapter[unit.owner] += uvpc[p_i] * unit.late_promo_factors[comp-1][c]
                    else:  # all subsequent units have not appeared yet
                        break

                for p_j in range(len(self.players)):
                    v_matrix[p_i][p_j] += Pricing.redundancy(
                        team_values_this_chapter[p_j], self.MC_matrix[c][p_i], self.opp_ratio)

        return v_matrix

    def update_value_matrix_by_chapter(self, new_trading_players, new_first_chapter):
        # make sure to update changes that should have been done by reverted trades
        trading_players = self.prev_players_trading | new_trading_players
        self.prev_players_trading = new_trading_players

        first_chapter = min(self.prev_chapter_update, new_first_chapter)
        self.prev_chapter_update = new_first_chapter

        promo_competitors = [0] * len(GameData.units)
        units_to_update_no_comp = []
        units_to_update_with_comp = []

        for u_i, unit in enumerate(GameData.units):
            if unit.owner in trading_players:
                for u_j in range(u_i + 1, len(GameData.units)):
                    if unit.competitor(GameData.units[u_j]):
                        promo_competitors[u_j] += 1
                if promo_competitors[u_i] == 0:
                    units_to_update_no_comp.append(unit)
                else:
                    units_to_update_with_comp.append(unit)

        for c in range(first_chapter, len(GameData.chapters)):
            for p_i, row in enumerate(self.value_matrix_by_chapter[c]):
                for p_j in trading_players:
                    row[p_j] = 0

                for unit in units_to_update_no_comp:
                    if unit.join_chapter > c:
                        break
                    row[unit.owner] += self.unit_value_per_chapter[unit.ID][p_i]

                for unit in units_to_update_with_comp:
                    if unit.join_chapter > c:
                        break
                    row[unit.owner] += self.unit_value_per_chapter[unit.ID][p_i] \
                        * unit.late_promo_factors[promo_competitors[unit.ID]-1][c]

                for p_j in trading_players:
                    row[p_j] = Pricing.redundancy(row[p_j], self.MC_matrix[c][p_i], self.opp_ratio)
                    if c > 0:
                        self.running_total_by_chapter[c][p_i][p_j] \
                             = self.running_total_by_chapter[c-1][p_i][p_j] \
                             + row[p_j]
                    else:
                        self.running_total_by_chapter[c][p_i][p_j] = row[p_j]

    # Print matrix, comp_sat, handicaps, and matrix+sat after handicapping
    def print_value_matrix(self, v_matrix):
        print()
        print('          ', end=' ')
        for player in self.players:
            print(f'{player:10s}', end=' ')
        print('Comparative satisfaction')

        for p, row in enumerate(v_matrix):
            print(f'{self.players[p]:10s}', end=' ')
            for value in row:
                print(f' {value:6.2f}   ', end=' ')
            print(f' {Pricing.comp_sat(row, p):6.2f}')

        prices = Pricing.pareto_prices(v_matrix, self.opp_ratio)

        print()
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
        # return Pricing.allocation_score(self.value_matrix_by_chapter_fn())
        return Pricing.allocation_score(self.running_total_by_chapter[-1])

    # try all swaps to improve score
    def improve_allocation_swaps(self):
        self.update_value_matrix_by_chapter(set(range(len(self.players))), 0)

        current_score = self.get_score()
        swapped = False
        for u_i, unit_i in enumerate(GameData.units):
            for unit_j in GameData.units[u_i+1:]:  # only try each pair once
                if unit_i.owner != unit_j.owner:

                    unit_i.owner, unit_j.owner = unit_j.owner, unit_i.owner
                    self.update_value_matrix_by_chapter({unit_i.owner, unit_j.owner},
                                                        min(unit_i.join_chapter, unit_j.join_chapter))

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
    def improve_allocation_rotate(self):
        # for each team member for each player (recursive for loops)
        # base case, try all rotations
        # don't need to immediately update team arrangements for calculations

        start = time.time()
        indices = [0]*len(self.players)
        teams = self.teams()

        current_score = self.get_score()
        rotated = False

        def recursive_rotate(p_i):
            nonlocal teams
            nonlocal current_score
            nonlocal rotated

            if p_i >= len(self.players):  # base case
                for rotation in self.rotations:

                    for p in range(len(self.players)):
                        teams[p][indices[p]].owner = rotation[p]  # p's unit goes to rotation[p]

                    if current_score < self.get_score():
                        current_score = self.get_score()

                        print('\nRotating:')
                        for p2 in range(len(self.players)):
                            if rotation[p2] != p2:
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

                for p in range(len(self.players)):
                    teams[p][indices[p]].owner = p  # unrotate, if teams were updated rotates to new teams

            else:
                for indices[p_i] in range(self.max_team_size):
                    if p_i == 0:
                        print()
                        print(time.time()-start)
                        print(indices[p_i], 'A\n')
                    if p_i == 1:
                        print('\n', indices[p_i], 'B')
                    if p_i == 2:
                        print(indices[p_i], end='c ')
                    recursive_rotate(p_i + 1)

        recursive_rotate(0)
        return rotated


