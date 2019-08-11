import AuctionState
import Pricing
import cProfile

test = AuctionState.AuctionState(['Akira', 'Bob', 'Cedric', 'David', 'Eddie'])
test.read_bids('FE7auction3.bids.txt')
test.print_bids()
test.create_max_chapter_values()
test.max_sat_assign()

test.read_synergy('FE7auction3.bids.txt')
test.manual_synergy[0][1][0] = 0.0
test.manual_synergy[1][0][0] = 0.0

test.set_synergy_ratios()
test.print_synergy_ratios()


def main():
    while test.improve_allocation_swaps():
        pass

    ##while test.improve_allocation_rotate():
    ##   pass

    test.print_teams()
    test.print_teams_detailed()
    test.print_value_matrix(test.value_matrix_by_chapter())
    print(Pricing.allocation_score(test.value_matrix_by_chapter(), test.robust_factor))
    print()


# cProfile.run('main()')

test.robust_factor = 0.125
main()
