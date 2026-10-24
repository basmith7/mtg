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
        # Golden values re-pinned in slice 06, when the model learnt colours and commander tax.
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
    def test_monotonic_in_pips(self):
        for mv in range(3, 8):
            needs = [goldfish.sources_needed(p, mv) for p in (1, 2, 3)]
            self.assertEqual(needs, sorted(needs), mv)
            self.assertLess(needs[0], needs[1])

    def test_matches_karstens_published_99_card_numbers_from_mv_4(self):
        # His 2022 table (TCGplayer, 2022-08-02). Below MV 4 his free mulligan lowers his numbers; we model none.
        for (p, mv), want in {(1, 4): 16, (2, 4): 26, (3, 4): 33, (2, 5): 23, (3, 6): 28, (2, 7): 20}.items():
            self.assertLessEqual(abs(goldfish.sources_needed(p, mv) - want), 1, (p, mv))


GOLDEN = {'keep7': 0.644, 'cast5': 0.718, 'recast8': 0.594}

if __name__ == '__main__':
    unittest.main()
