import AuctionState
import cProfile

test = AuctionState.AuctionState(['-A-', '-B-', '-C-', '-D-'])


def main():
    test.read_units('FE8data/units.txt')
    test.read_bids('FE8data/auction3.bids.txt')
    test.read_synergy('FE8data/auction3A.syn.txt')
    test.set_median_synergy()
    test.set_median_synergy()
    test.set_median_synergy()
    test.print_synergy(0)
    test.run()


# cProfile.run('main()')
main()
