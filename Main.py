import AuctionState
import Pricing
import cProfile

test = AuctionState.AuctionState(['-A-', '-B-', '-C-', '-D-'])


def main():
    test.read_bids('FE8auction3one.bids.txt')
    test.print_bids()

    test.read_synergy('FE8auction3A.syn.txt')
    # test.read_synergy('FE8auction3Adouble.syn.txt')
    # test.read_synergy('FE8auction3zeros.syn.txt')
    test.set_median_synergy()
    test.set_median_synergy()
    test.set_median_synergy()
    test.print_synergy(0)
    test.print_synergy(1)
    test.print_synergy(2)
    test.print_synergy(3)

    test.max_sat_assign()

    while test.improve_allocation_swaps():
        pass

    while test.improve_allocation_rotate():
        pass

    test.print_teams()
    test.print_teams_detailed()
    test.print_value_matrices()


test.robust_factor = 0.125
# cProfile.run('main()')
main()
