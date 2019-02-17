import AuctionState
import Pricing
import cProfile


def main():
    test = AuctionState.AuctionState(['Alicia', 'Bob', 'Cedric', 'David', 'Ellie'])

    test.read_bids('FE7auction3.bids.txt')
    test.print_bids()

    test.create_max_chapter_values()
    test.max_sat_assign()

    test.print_teams()
    test.print_teams_detailed()
    test.print_value_matrix(test.value_matrix_by_chapter())
    print(Pricing.allocation_score(test.value_matrix_by_chapter()))
    print()

    while test.improve_allocation_swaps():
        pass

    #while test.improve_allocation_rotate():
    #    pass

    test.print_teams()
    test.print_teams_detailed()
    test.print_value_matrix(test.value_matrix_by_chapter())
    print(Pricing.allocation_score(test.value_matrix_by_chapter()))
    print()

# cProfile.run('main()')
main()
