import AuctionState
from PIL import Image, ImageDraw
import random
# import cProfile

class AuctionStateVisuals(AuctionState.AuctionState):
    PLAYER_COLORS = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,255,255),(255,0,255)]

    def draw_teams(self, portrait_x=96, portrait_y=80, margin=20, back_color=(0,0,0)):
        im = Image.new('RGB', ((portrait_x + 2 * margin) * len(self.players) - 2 * margin,
                               (portrait_y + margin) * self.max_team_size + 2 * margin), back_color)
        drawer = ImageDraw.Draw(im)

        teams = self.teams()
        handicaps = self.handicaps()
        colors = [self.PLAYER_COLORS[j % len(self.PLAYER_COLORS)] for j in range(len(self.players))]

        for i in range(len(self.players)):
            col_start = i * (portrait_x + 2 * margin)
            drawer.text((col_start + margin, 0), self.players[i], colors[i])

            for j in range(self.max_team_size):
                filename = f'{self.game_dir}portraits/{teams[i][j].name}.png'
                try:
                    portrait = Image.open(filename)
                except FileNotFoundError as error:
                    print(error)
                    print(filename)
                else:
                    im.paste(portrait, (col_start, j * (portrait_y + margin) + margin))

                drawer.text((col_start + margin, (j+1) * (portrait_y + margin)),
                            teams[i][j].name, colors[i])

            drawer.text((col_start + margin,
                         (portrait_y + margin) * self.max_team_size + margin),
                        f'{handicaps[i]:7.4}', colors[i])

        im.save(f'{self.auct_dir}output_teams.png')

    def draw_bids(self, portrait_x=96, portrait_y=80, margin=20, back_color=(0,0,0)):
        self.units.sort(key=lambda unit: -sum(unit.bids))

        x_step = portrait_x + margin
        bar_max_height = (x_step * len(self.units)) // 2
        bar_width = portrait_x // len(self.players)

        im = Image.new('RGB', (x_step * len(self.units) - margin, portrait_y + bar_max_height + 20), back_color)
        drawer = ImageDraw.Draw(im)

        max_bid = 0
        for unit in self.units:
            if max_bid < max(unit.bids):
                max_bid = max(unit.bids)

        colors = [self.PLAYER_COLORS[j % len(self.PLAYER_COLORS)] for j in range(len(self.players))]

        for i, unit in enumerate(self.units):
            x_start = i*x_step

            filename = f'{self.game_dir}portraits/{unit.name}.png'
            try:
                portrait = Image.open(filename)
            except FileNotFoundError as error:
                print(error)
                print(filename)
            else:
                im.paste(portrait, (x_start, bar_max_height))
                drawer.text((x_start + 5, bar_max_height + portrait_y + 5), unit.name, colors[unit.owner])

            for j in range(len(self.players)):
                drawer.rectangle([(x_start + bar_width * j, int(bar_max_height * (1 - unit.bids[j]/max_bid))),
                                  (x_start + bar_width * (j+1),bar_max_height)],
                                 colors[j], colors[j])

        im.save(f'{self.auct_dir}output_bids.png')


if __name__ == '__main__':
    test = AuctionStateVisuals()
    # cProfile.run('test.run()', sort='cumulative')
    test.run()
    test.draw_teams()
    test.draw_bids()
