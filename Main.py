import AuctionState
import Pricing
import cProfile


def main():
    test = AuctionState.AuctionState(['Wargrave', 'Athena', 'Sturm', 'amg', 'GentleWind'])

    test.read_bids('FE7auction2.bids.txt')
    #test.print_bids()

    test.create_max_chapter_values()
    #test.print_max_chapter_values()

    test.max_sat_assign()
    #test.print_teams()
    #test.print_teams_detailed()

    while test.improve_allocation_swaps():
       pass

    test.improve_allocation_rotate()
    test.print_teams()
    test.print_teams_detailed()

    test.print_value_matrix(test.value_matrix_by_chapter())
    print(Pricing.allocation_score(test.value_matrix_by_chapter()))

    print()


cProfile.run('main()')
