import AuctionState
import cProfile

test = AuctionState.AuctionState(['-A-', '-B-', '-C-', '-D-'])
test.robust_factor = 0.25

def main():
    test.read_bids('FE8auction3.bids.txt')

    test.read_synergy('FE8auction3A.syn.txt')
    test.set_median_synergy()
    test.set_median_synergy()
    test.set_median_synergy()
    test.print_synergy(0)
    test.run()


# cProfile.run('main()')
main()
