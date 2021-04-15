import AuctionState
from PIL import Image, ImageDraw
# import cProfile


class AuctionStateVisuals(AuctionState.AuctionState):
    def __init__(self):
        super().__init__()
        self.colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,255,255),(255,0,255),(255,255,255)]
        self.portraits = {}
        self.portrait_x = 1
        self.portrait_y = 1
        self.margin = 20
        self.x_step = self.portrait_x + self.margin
        self.y_step = self.portrait_y + self.margin
        self.bar_width = 1
        self.max_bid = 10
        self.bar_max_height = self.portrait_y * self.max_bid  # one portrait height = 1 turncount

    def load(self):
        super().load()
        while len(self.colors) < len(self.players):
            self.colors.append(self.colors[len(self.colors) - 7])

        for unit in self.units:
            filename = f'{self.game_dir}portraits/{unit.name}.png'
            try:
                self.portraits[unit.name] = Image.open(filename)
                self.portrait_x = max(self.portrait_x, self.portraits[unit.name].size[0])
                self.portrait_y = max(self.portrait_y, self.portraits[unit.name].size[1])
            except FileNotFoundError as error:
                print(error)
                print(filename)
                self.portraits[unit.name] = Image.new('RGB', (self.portrait_x, self.portrait_y), (255,0,0))

        self.x_step = self.portrait_x + self.margin
        self.y_step = self.portrait_y + self.margin
        self.bar_width = self.portrait_x // len(self.players)
        self.max_bid = 0
        for unit in self.units:
            if self.max_bid < max(unit.bids):
                self.max_bid = max(unit.bids)
        self.bar_max_height = int(self.portrait_y * self.max_bid)

    def paste_portrait(self, im, unit, coord):
        im.paste(self.portraits[unit.name], coord)
        drawer = ImageDraw.Draw(im)
        drawer.text((coord[0] + self.margin, coord[1] + self.portrait_y + 5), unit.name, self.colors[unit.owner])

    def draw_teams(self, back_color=(0,0,0)):
        x_step = self.x_step + self.margin  # increased x margin

        im = Image.new('RGB', (x_step * len(self.players) - 2 * self.margin,
                               self.y_step * self.max_team_size + 2 * self.margin), back_color)
        drawer = ImageDraw.Draw(im)

        teams = self.teams()
        handicaps = self.handicaps()

        for i in range(len(self.players)):
            col_start = i * x_step
            drawer.text((col_start + self.margin, 0), self.players[i], self.colors[i])

            for j in range(self.max_team_size):
                self.paste_portrait(im, teams[i][j], (col_start, j * self.y_step + self.margin))

            drawer.text((col_start + self.margin, self.y_step * self.max_team_size + self.margin),
                        f'{handicaps[i]:7.4}', self.colors[i])

        im.save(f'{self.auct_dir}output/teams.png')

    def y_at_bid(self, bid):
        return int(self.bar_max_height * (1 - bid/self.max_bid))

    def draw_bids(self, back_color=(0,0,0)):
        self.units.sort(key=lambda unit: -sum(unit.bids))

        im = Image.new('RGB', (self.x_step * len(self.units) - self.margin,
                               self.y_step + self.bar_max_height), back_color)
        drawer = ImageDraw.Draw(im)
        for i in range(int(self.max_bid) + 1):
            drawer.line(((0, self.y_at_bid(i)), (im.size[0], self.y_at_bid(i))), (255,255,255))

        for i, unit in enumerate(self.units):
            x_start = i * self.x_step

            self.paste_portrait(im, unit, (x_start, self.bar_max_height))

            for j in range(len(self.players)):
                drawer.rectangle([(x_start + self.bar_width * j, self.y_at_bid(unit.bids[j])),
                                  (x_start + self.bar_width * (j+1), self.bar_max_height)],
                                 self.colors[j], self.colors[j])

        im.save(f'{self.auct_dir}output/bids.png')

        self.units.sort(key=lambda unit: unit.recruit_order)

    # if next unit's bars can fit beneath bottom-left most portrait, start a new row
    def draw_bids_compact(self, back_color=(0,0,0)):
        self.units.sort(key=lambda unit: -sum(unit.bids))

        # highest bar must fit under min_clearance_pixel to be eligible
        min_clearance_pixel = [-1] * len(self.units)
        columns_used = 0

        im = Image.new('RGB', (self.x_step * len(self.units) - self.margin,
                               self.y_step + self.bar_max_height), back_color)
        drawer = ImageDraw.Draw(im)
        for i in range(int(self.max_bid) + 1):
            drawer.line(((0, self.y_at_bid(i)), (im.size[0], self.y_at_bid(i))), (255,255,255))

        for i, unit in enumerate(self.units):
            bar_heights = [self.y_at_bid(unit.bids[j]) for j in range(len(self.players))]
            highest_bar = min(bar_heights)
            lowest_bar = max(bar_heights)

            x_start = 0
            for j in range(len(min_clearance_pixel)):
                if highest_bar > min_clearance_pixel[j]:
                    x_start = j * self.x_step
                    min_clearance_pixel[j] = lowest_bar + self.y_step
                    if columns_used < j + 1:
                        columns_used = j + 1
                    break

            self.paste_portrait(im, unit, (x_start, lowest_bar))

            for j in range(len(self.players)):
                drawer.rectangle([(x_start + self.bar_width * j, bar_heights[j]),
                                  (x_start + self.bar_width * (j+1), lowest_bar)],
                                 self.colors[j], self.colors[j])

        im = im.crop((0, 0, self.x_step * columns_used - self.margin, self.y_step + self.bar_max_height))
        im.save(f'{self.auct_dir}output/bids_compact.png')

        self.units.sort(key=lambda unit: unit.recruit_order)


if __name__ == '__main__':
    test = AuctionStateVisuals()
    # cProfile.run('test.run()', sort='cumulative')
    test.run()
    test.draw_teams()
    test.draw_bids()
    test.draw_bids_compact()
