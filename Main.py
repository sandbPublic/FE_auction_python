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

    #test.improve_allocation_rotate()
    test.print_teams()
    test.print_teams_detailed()

    #test.update_value_matrix_by_chapter(set(), 20)

    #test.update_value_matrix_by_chapter({0, 1, 2, 3}, 20)

    test.print_value_matrix(test.value_matrix_by_chapter_fn())


    #print(Pricing.allocation_score(test.value_matrix_by_chapter_fn()))
    print()


cProfile.run('main()')
