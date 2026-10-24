import random
import unittest

from mtg import goldfish
from mtg.goldfish import Card, Cost

R, B, C = frozenset('R'), frozenset('B'), frozenset('C')
RR5 = Cost(5, {'B': 1, 'R': 2})


def library(red=18, black=18, colourless=0):
    """99 cards: 36 lands split by colour, 9 ramp pieces, the rest 3-drops."""
    lands = [Card('land', 0, 1, R, {})] * red + [Card('land', 0, 1, B, {})] * black
    lands += [Card('land', 0, 1, C, {})] * colourless
    ramp = [Card('rock', 2, 1, C, {})] * 6 + [Card('dork', 1, 1, R, {'R': 1})] * 3
    return lands + ramp + [Card('other', 3, 0, frozenset(), {'B': 1})] * (99 - len(lands) - len(ramp))


class SimulateTest(unittest.TestCase):
    def test_seeded_run_is_reproducible(self):
        # Golden values: re-pin them only when the simulation model deliberately changes.
        r = goldfish.simulate(library(), RR5, 500, random.Random(7))
        self.assertEqual(r, goldfish.simulate(library(), RR5, 500, random.Random(7)))
        self.assertAlmostEqual(r['keep7'], GOLDEN['keep7'])
        self.assertAlmostEqual(r['cast_by'][5], GOLDEN['cast5'])
        self.assertAlmostEqual(r['recast_by'][8], GOLDEN['recast8'])

    def test_no_red_sources_never_casts_a_red_commander(self):
        r = goldfish.simulate(library(red=0, black=18, colourless=18), RR5, 200, random.Random(1))
        self.assertEqual(r['cast_by'][goldfish.TURNS], 0)

    def test_more_sources_never_lowers_cast_by(self):
        few = goldfish.simulate(library(red=8, black=8, colourless=20), RR5, 2000, random.Random(3))
        many = goldfish.simulate(library(red=16, black=16, colourless=4), RR5, 2000, random.Random(3))
        for t in range(1, goldfish.TURNS + 1):
            self.assertGreaterEqual(many['cast_by'][t], few['cast_by'][t] - 0.01, t)

    def test_recast_is_at_least_a_turn_after_the_first_cast(self):
        r = goldfish.simulate(library(), RR5, 1000, random.Random(5))
        for t in range(2, goldfish.TURNS + 1):
            self.assertLessEqual(r['recast_by'][t], r['cast_by'][t - 1])
        self.assertEqual(r['recast_by'][1], 0)

    def test_no_lands_never_casts(self):
        r = goldfish.simulate([Card('other', 2, 0, frozenset(), {})] * 99, Cost(2, {}), 50, random.Random(1))
        self.assertEqual(r['cast_by'][goldfish.TURNS], 0)


class CanPayTest(unittest.TestCase):
    def test_hall_condition_on_dual_sources(self):
        rb = frozenset('RB')
        self.assertTrue(goldfish.can_pay(Cost(3, {'R': 1, 'B': 1}), [rb, rb, C]))
        self.assertFalse(goldfish.can_pay(Cost(3, {'R': 2, 'B': 1}), [rb, rb, C]))


class SourcesNeededTest(unittest.TestCase):
    def test_karstens_published_cells(self):
        self.assertEqual(goldfish.sources_needed(1, 1), 19)
        self.assertEqual(goldfish.sources_needed(2, 4), 26)
        self.assertEqual(goldfish.sources_needed(3, 3), 36)

    def test_unpublished_cells_take_the_nearest_mv(self):
        self.assertEqual(goldfish.sources_needed(1, 10), 14)
        self.assertEqual(goldfish.sources_needed(2, 1), 30)
        self.assertEqual(goldfish.sources_needed(5, 9), 36)

    def test_more_pips_never_want_fewer_sources(self):
        for mv in range(1, 11):
            needs = [goldfish.sources_needed(p, mv) for p in (1, 2, 3, 4)]
            self.assertEqual(needs, sorted(needs), mv)

    def test_higher_mv_never_wants_more_sources(self):
        for p in (1, 2, 3, 4):
            needs = [goldfish.sources_needed(p, mv) for mv in range(1, 11)]
            self.assertEqual(needs, sorted(needs, reverse=True), p)


def land(text, produced=None):
    return {'type_line': 'Land', 'oracle_text': text, 'produced_mana': produced}


class LandProducesTest(unittest.TestCase):
    def test_typed_fetch_finds_its_types(self):
        delta = land('{T}, Pay 1 life, Sacrifice Polluted Delta: Search your library for an Island or Swamp card, '
                     'put it onto the battlefield, then shuffle.')
        self.assertEqual(goldfish.land_produces(delta, 'WUBR'), {'U', 'B'})

    def test_basic_land_fetch_finds_the_identity(self):
        vista = land('{T}: Add {C}.\n{T}, Pay 1 life, Sacrifice Prismatic Vista: Search your library for a basic '
                     'land card, put it onto the battlefield, then shuffle.', ['C'])
        self.assertEqual(goldfish.land_produces(vista, 'RG'), {'C', 'R', 'G'})

    def test_plain_land_is_its_produced_mana(self):
        self.assertEqual(goldfish.land_produces(land('({T}: Add {R}.)', ['R']), 'RG'), {'R'})


class MulliganTest(unittest.TestCase):
    def test_first_mulligan_is_free(self):
        # An all-land deck never keeps, so it mulligans to the cap of four and bottoms only three: four
        # cards kept plus four draws are the lands seen by turn 4 (seven if every mulligan cost a card).
        r = goldfish.simulate([Card('land', 0, 1, R, {})] * 99, None, 20, random.Random(1))
        self.assertEqual(dict(r['mulls']), {4: 20})
        self.assertEqual(r['lands4'], 8)


GOLDEN = {'keep7': 0.646, 'cast5': 0.724, 'recast8': 0.62}

if __name__ == '__main__':
    unittest.main()
