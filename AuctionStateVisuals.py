import AuctionState
import PIL
# import cProfile

class AuctionStateVisuals(AuctionState.AuctionState):
    def draw_bids(self):
        ...

    def draw_teams(self):
        ...


if __name__ == '__main__':
    test = AuctionStateVisuals()
    # cProfile.run('test.run()', sort='cumulative')
    test.run()
