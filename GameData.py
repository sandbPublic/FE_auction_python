promo_KC = 0  # knight crest
promo_HC = 1  # hero crest
promo_OB = 2  # orion's bolt
promo_EW = 3  # elysian whip
promo_GR = 4  # guiding ring
promo_O8 = 5  # ocean seal in FE8
promo_ES = 6  # earth seal, item only, leave room to insert ocean seal in FE8
promo_OS = 7  # ocean seal
promo_FC = 8  # fell contract
promo_HS = 9  # heaven seal
promo_NO = 10  # can't promote

promo_strings = [
    'Nite ',
    'Hero ',
    'Bolt ',
    'Whip ',
    'Ring ',
    'Ocean',
    'Earth',
    'Ocean',
    'Fell ',
    'Heven',
    '     '
]

chapters_FE7 = [
    '11  Another Journey',
    '12  Birds of a Feather',
    '13  In Search of Truth',
    '13x The Peddler Merlinus',
    '14  False Friends',
    '15  Talons Alight',
    '16  Noble Lady of Caelin',
    '17  Whereabouts Unknown',
    '17x The Port of Badon',
    '18  Pirate Ship',
    '19  The Dread Isle',
    '19x Imprisoner of Magic',
    "20  Dragon's Gate",
    '21  New Resolve',
    "22  Kinship's Bond",
    '23  Living Legend',
    '23x Genesis',
    '24  Four-Fanged Offense',
    '25  Crazed Beast',
    '26  Unfulfilled Heart',
    '27  Pale Flower of Darkness',
    '28  Battle Before Dawn',
    '28x Night of Farewells',
    '29  Cog of Destiny',
    '30  The Berserker',
    '31  Sands of Time',
    '31x Battle Preparations',
    '32  Victory or Death',
    '32x The Value of Life',
    '33  Light'
]

chapters_FE8_Eirika = [
    'Prologue: The Fall of Renais',
    ' 1  Escape!',
    ' 2  The Protected',
    ' 3  The Bandits of Borgo',
    ' 4  Ancient Horrors',
    " 5  The Empire's Reach",
    ' 5x Unbroken Heart',
    ' 6  Victims of War',
    ' 7  Waterside Renvall',
    " 8  It's a Trap!",
    ' 9A Distant Blade',
    '10A Revolt at Carcino',
    '11A Creeping Darkness',
    '12A Village of Silence',
    "13A Hamill Canyon",
    '14A Queen of White Dunes',
    '15  Scorched Sand',
    '16  Ruled by Madness',
    '17  River of Regrets',
    '18  Two Faces of Evil',
    '19  Last Hope',
    '20  Darkling Woods',
    '21  Sacred Stone'
]

chapters_FE8_Ephraim = [
    'Prologue: The Fall of Renais',
    ' 1  Escape!',
    ' 2  The Protected',
    ' 3  The Bandits of Borgo',
    ' 4  Ancient Horrors',
    " 5  The Empire's Reach",
    ' 5x Unbroken Heart',
    ' 6  Victims of War',
    ' 7  Waterside Renvall',
    " 8  It's a Trap!",
    ' 9B Fort Rigwald',
    '10B Turning Traitor',
    '11B Phantom Ship',
    '12B Landing at Taizel',
    "13B Fluorspar's Oath",
    '14B Father and Son',
    '15  Scorched Sand',
    '16  Ruled by Madness',
    '17  River of Regrets',
    '18  Two Faces of Evil',
    '19  Last Hope',
    '20  Darkling Woods',
    '21  Sacred Stone'
]

chapters = chapters_FE8_Eirika

promo_item_acquire_times_FE7_HNM = [
    # Entries that appear with a line break between
    # their nominal acquire chapter indicate that they
    # are more likely to not be helpful in that chapter,
    # due to location or time they appear.

    # chapter
    # 11 / 0
    # 12 / 1
    # 13 / 2
    # 13x / 3
    # 14 / 4
    # 15 / 5
    # 16 / 6
    # 17 / 7

    {'chapter': 8, 'type': promo_KC, 'number': 1},  # Whereabouts Unknown, chest
    {'chapter': 8, 'type': promo_HC, 'number': 1},  # Whereabouts Unknown, chest
    # 17x / 8

    # 18 / 9

    {'chapter': 10, 'type': promo_GR, 'number': 1},  # Pirate Ship, shaman
    # 19 / 10

    {'chapter': 11, 'type': promo_OB, 'number': 1},  # The Dread Isle, Uhai
    # 19x / 11
    # 20 / 12

    {'chapter': 13, 'type': promo_HC, 'number': 1},  # New Resolve, chest
    # 21 / 13

    {'chapter': 14, 'type': promo_EW, 'number': 1},  # New Resolve, village
    {'chapter': 14, 'type': promo_HC, 'number': 1},  # New Resolve, Oleg (steal)
    # 22 / 14
    {'chapter': 14, 'type': promo_KC, 'number': 1},  # Kinship's Bond, cavalier

    # 23 / 15
    {'chapter': 15, 'type': promo_OS, 'number': 1},  # Living Legend, close sand
    # (can get from shops later but never need more than 1)

    {'chapter': 16, 'type': promo_HC, 'number': 1},  # Living Legend, far sand
    {'chapter': 16, 'type': promo_GR, 'number': 1},  # Living Legend, Jasmine (steal)
    # 23x / 16
    # 24 / 17

    {'chapter': 18, 'type': promo_ES, 'number': 1},  # Four-Fanged Offense, village
    {'chapter': 18, 'type': promo_OB, 'number': 1},  # Four-Fanged Offense, village A, Sniper B
    # {'chapter: 18, 'type': promo_OS, 'number': 9},  # Four-Fanged Offense A ONLY, secret shop
    # 25 / 18

    {'chapter': 19, 'type': promo_EW, 'number': 1},  # Crazed Beast, village
    # 26 / 19
    {'chapter': 19, 'type': promo_HS, 'number': 1},  # Unfulfilled Heart, auto at start

    # 27 / 20

    {'chapter': 21, 'type': promo_GR, 'number': 1},  # Pale Flower of Darkness A ONLY, chest
    {'chapter': 21, 'type': promo_HC, 'number': 1},  # Pale Flower of Darkness B ONLY, chest
    # 28 / 21

    {'chapter': 22, 'type': promo_EW, 'number': 1},  # Battle Before Dawn, bishop
    {'chapter': 22, 'type': promo_HS, 'number': 1},  # Battle Before Dawn, auto at chapter end
    # 28x / 22

    {'chapter': 23, 'type': promo_FC, 'number': 1},  # Night of Farewells, Sonia, free chapter
    # 29 / 23

    {'chapter': 24, 'type': promo_GR, 'number': 1},  # Cog of Destiny, sniper (steal)
    # 30 / 24
    # 31 / 25

    {'chapter': 26, 'type': promo_KC, 'number': 9},  # Sands of Time, secret shop, survive chapter
    {'chapter': 26, 'type': promo_HC, 'number': 9},
    {'chapter': 26, 'type': promo_OB, 'number': 9},
    {'chapter': 26, 'type': promo_EW, 'number': 9},
    {'chapter': 26, 'type': promo_GR, 'number': 9},
    # 31x / 26
    # 32 / 27
    {'chapter': 27, 'type': promo_ES, 'number': 1},  # Victory or Death, nils at start

    {'chapter': 28, 'type': promo_OS, 'number': 9},  # Victory or Death, secret shop at end
    {'chapter': 28, 'type': promo_FC, 'number': 9},
    {'chapter': 28, 'type': promo_ES, 'number': 9}
]

promo_item_acquire_times_FE8 = [
    # P/ 1
    # 1/ 2
    # 2/ 3
    # 3/ 4
    # 4/ 5
    # 5/ 6

    { 8, promo_GR, 1},  # if all villages visited, only usable on ch6
    #5x/ 7
    # 6/ 8

    { 9, promo_OB, 1},  # if civs survive
    # 7/ 9

    {10, promo_KC, 1},  # Murray
    # 8/10

    {11, promo_EW, 1},  # chest
    # 9/11
    {11, promo_O8, 1},  # a pirate, b chest

    #10/12
    #{12, promo_HC, 1}, # b ONLY, village
    {12, promo_HC, 1},  # 10a or 13b, Gerik

    {13, promo_GR, 1},  # a ONLY, Pablo
    #{13, promo_KC, 1}, # b ONLY, if all npc cavs survive
    #11/13
    #12/14
    #{14, promo_GR, 1}, # b ONLY, shaman

    #13/15
    {15, promo_EW, 1},  # 13a or 10b, Cormag

    {16, promo_KC, 1},  # a ONLY, Aias
    #14/16
    {16, promo_GR, 1},  # chest

    {16, promo_HC, 1},  # a ONLY, myrmidon

    #{17, promo_KC, 1}, # b ONLY, Vigarde
    #15/17
    {17, promo_ES, 1},  # village
    {17, promo_GR, 1},  # steal shaman

    #16/18
    {18, promo_KC, 1},  # chest
    {18, promo_HC, 1},  # enemy

    {19, promo_HS, 2},
    #17/19
    {19, promo_GR, 1}  # mage

    #18/20
    #19/21
    #20/22
    #21/23
]

# chapter x item_types running total of available items
promo_item_count = []
for c in range(len(chapters)):
    promo_item_count.append([0] * len(promo_strings))

# assume that no more than 1 earth seal will be used,
# add to count for all items it can substitute for
for entry in promo_item_acquire_times_FE7_HNM:
    for row in promo_item_count[entry['chapter']:]:
        row[entry['type']] += entry['number']

        if entry['type'] == promo_ES:
            for t in range(promo_ES):
                row[t] += entry['number']

unit_data_FE7_HNM_split_Marcus = [
    # chapter
    # 11 / 0
    # 12 / 1
    ['Matthew', 1, promo_FC],  # free for 11 / 1
    ['Serra', 1, promo_GR],
    ['Oswin', 1, promo_KC], # Will Oswin or Lowen be promoted first?
    ['Eliwood', 1, promo_HS],
    ['Lowen', 1, promo_KC],
    ['Rebecca', 1, promo_OB],
    ['Dorcas', 1, promo_HC],
    ['Bartre&Karla', 1, promo_HC],
    ['Marcus<=19x', 1, promo_NO],
    # 13 / 2
    ['Guy', 2, promo_HC],
    # 13x / 3
    # 14 / 4
    ['Erk', 4, promo_GR],
    ['Priscilla', 5, promo_GR],  # unlikely to contribute in join chapter
    # 15 / 5
    # 16 / 6
    ['Florina', 6, promo_EW],
    ['Lyn', 7, promo_HS],  # free during join chapter
    ['Sain', 7, promo_KC],
    ['Kent', 7, promo_KC],
    ['Wil', 7, promo_OB],
    # 17 / 7
    ['Raven', 7, promo_HC],
    ['Lucius', 8, promo_GR],  # unlikely to contribute in join chapter
    # 17x / 8
    ['Canas', 8, promo_GR],
    # 18 / 9
    # 19 / 10
    ['Dart', 10, promo_OS],
    ['Fiora', 10, promo_EW],
    # 19x / 11
    # 20 / 12
    ['Marcus>=20', 12, promo_NO],
    ['Legault', 12, promo_FC],  # unlikely to contribute in join chapter
    # 21 / 13
    # 22 / 14
    ['Isadora', 14, promo_NO],
    ['Heath', 15, promo_EW],
    ['Rath', 15, promo_OB],
    # 23 / 15
    ['Hawkeye', 15, promo_NO],
    # 23x / 16
    # 24 / 17
    # ['Wallace/Geitz', 17, promo_NO],
    # 25 / 18
    ['Farina', 18, promo_EW],
    # 26 / 19
    ['Pent', 19, promo_NO],
    ['Louise', 19, promo_NO],
    # 27 / 20
    # ['Harken', 20, promo_NO],
    # ['Karel', 20, promo_NO],
    # 28 / 21
    ['Nino', 21, promo_GR],
    # 28x / 22
    ['Jaffar', 22, promo_NO],
    # 29 / 23
    ['Vaida', 23, promo_NO],
    # 30 / 24
    # 31 / 25
    # 31x / 26
    # 32 / 27
    ['Renault', 27, promo_NO]
    # 32x / 28
    # 33 / 29
    # ['Athos', 29, promo_NO]
]

unit_data_FE7_HNM = [
    # chapter
    # 11 / 0
    # 12 / 1
    ['Matthew', 1, promo_FC],  # free for 11 / 1
    ['Serra', 1, promo_GR],
    ['Oswin', 1, promo_KC], # Will Oswin or Lowen be promoted first?
    ['Eliwood', 1, promo_HS],
    ['Lowen', 1, promo_KC],
    ['Rebecca', 1, promo_OB],
    ['Dorcas', 1, promo_HC],
    ['Bartre&Karla', 1, promo_HC],
    # 13 / 2
    ['Guy', 2, promo_HC],
    # 13x / 3
    # 14 / 4
    ['Erk', 4, promo_GR],
    ['Priscilla', 5, promo_GR],  # unlikely to contribute in join chapter
    # 15 / 5
    # 16 / 6
    ['Florina', 6, promo_EW],
    ['Lyn', 6, promo_HS],  # no longer free, restricted to box
    ['Sain', 6, promo_KC],
    ['Kent', 6, promo_KC],
    ['Wil', 6, promo_OB],
    # 17 / 7
    ['Raven', 7, promo_HC],
    ['Lucius', 8, promo_GR],  # unlikely to contribute in join chapter
    # 17x / 8
    ['Marcus>=17x', 8, promo_NO],
    ['Canas', 8, promo_GR],
    # 18 / 9
    # 19 / 10
    ['Dart', 10, promo_OS],
    ['Fiora', 10, promo_EW],
    # 19x / 11
    # 20 / 12
    ['Legault', 12, promo_FC],  # unlikely to contribute in join chapter
    # 21 / 13
    # 22 / 14
    ['Isadora', 14, promo_NO],
    ['Heath', 15, promo_EW],
    ['Rath', 15, promo_OB],
    # 23 / 15
    ['Hawkeye', 15, promo_NO],
    # 23x / 16
    # 24 / 17
    # ['Wallace/Geitz', 17, promo_NO],
    # 25 / 18
    ['Farina', 18, promo_EW],
    # 26 / 19
    ['Pent', 19, promo_NO],
    ['Louise', 19, promo_NO],
    # 27 / 20
    # ['Harken', 20, promo_NO],
    # ['Karel', 20, promo_NO],
    # 28 / 21
    ['Nino', 21, promo_GR],
    # 28x / 22
    ['Jaffar', 22, promo_NO],
    # 29 / 23
    ['Vaida', 23, promo_NO],
    # 30 / 24
    # 31 / 25
    # 31x / 26
    # 32 / 27
    ['Renault', 27, promo_NO],
    # 32x / 28
    # 33 / 29
    # ['Athos', 29, promo_NO]
    ['--none--', 29, promo_NO]
]

unit_data_FE8 = [
    # P/ 0
    # ['Eirika',	0, promo_HS],
    # 1
    ['Franz', 1, promo_KC],
    ['Gilliam', 1, promo_KC],
    # 2
    ['Vanessa', 2, promo_EW],
    ['Moulder', 2, promo_GR],
    ['Ross', 2, promo_O8],  # can promo_HC
    ['Garcia', 3, promo_HC],
    # 3
    ['Neimi', 3, promo_OB],
    ['Colm', 3, promo_O8],
    # 4
    ['Artur', 4, promo_GR],
    ['Lute', 4, promo_GR],
    # 5
    ['Natasha', 5, promo_GR],
    ['Joshua', 5, promo_HC],
    # 5x/ 6
    # ['Orson',		6, promo_NO],
    # 6/ 7
    ['Seth>=6', 7, promo_NO],
    # 7/ 8
    # 8/ 9
    ['Forde', 9, promo_KC],
    ['Kyle', 9, promo_KC],
    # 9/10
    ['Tana', 10, promo_EW],  # same in both routes, mostly unuseable in eph9
    ['Amelia', 10, promo_KC],  # returns in eir 13
    # 10/11
    ['Gerik', 11, promo_HC],  # 13/15 +3 eph
    # ['Tethys',	11, promo_NO], # 13/15 +3 eph
    ['Innes', 11, promo_NO],  # 15/17 +5 eph
    ['Marisa', 11, promo_HC],  # 12/14 +2 eph
    # 11/12
    ['Dozla', 12, promo_NO],
    ["L'Arachel",	12, promo_GR],
    # 12/13
    ['Saleh', 13, promo_NO],  # 15/17 +3 eph
    ['Ewan', 13, promo_GR],
    # 13/14
    ['Cormag', 14, promo_EW],  # 10/12 -3 eph
    # 14/15
    ['Rennac', 15, promo_NO],
    # 15/16
    ['Duessel', 16, promo_NO],  # 10/12 -5 eph
    ['Knoll', 16, promo_GR],
    # 16/17
    ['2nd Lord', 17, promo_HS],
    ['Myrrh', 17, promo_NO],
    # 17/18
    ['Syrene', 18, promo_NO],
    # 18/19
    # 19/20
    # 20/21
    # 21/22
    ['Bonus Units', 22, promo_NO]
]

unit_data = unit_data_FE8


class Unit:
    def __init__(self, ID, data_i):
        self.ID = ID
        self.name = data_i[0]
        self.join_chapter = data_i[1]
        self.promo_type = data_i[2]
        self.owner = -1
        self.late_promo_factors = []  # same_promo_priors x chapters
        self.earliest_promo = -1
        self.competitors = set()
        self.current_competitors = 0

    def set_current_competitors(self):
        self.current_competitors = 0
        for comp in self.competitors:
            if self.owner == comp.owner:
                self.current_competitors += 1

    def get_late_promo_factor(self, chapter):
        return self.late_promo_factors[self.current_competitors-1][chapter]


units_with_competitors = set()

units = [Unit(ID, data) for ID, data in enumerate(unit_data)]
for u, unit_prior in enumerate(units):
    for c, row in enumerate(promo_item_count):
        if row[unit_prior.promo_type] > 0:
            unit_prior.earliest_promo = max(unit_prior.join_chapter, c)
            break

    # add an entry for each prior unit in same promotion class
    for unit_post in units[u + 1:]:
        if unit_prior.promo_type == unit_post.promo_type and unit_prior.promo_type != promo_NO:
            units_with_competitors.add(unit_post)
            unit_post.competitors.add(unit_prior)
            unit_post.late_promo_factors.append([1] * len(chapters))

# reduce late_promo_factor for competition
for unit in units:
    for prior_competitors in range(1, len(unit.late_promo_factors) + 1):
        factor = 1

        # start from first promotable chapter
        for c in range(unit.earliest_promo, len(chapters)):
            if promo_item_count[c][unit.promo_type] <= prior_competitors:
                factor = max(factor - 0.125, 0)
                unit.late_promo_factors[prior_competitors - 1][c] = factor
            else:
                break  # gained item or already had it, other factors in row remain 1

    # print(unit.name)
    # for row in unit.late_promo_factors:
    #     print(row)


