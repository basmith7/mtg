import random
import unittest

from mtg import goldfish

# 99 cards: 36 lands, 12 ramp pieces, 51 other spells.
LIBRARY = ([('land', 0, 0)] * 36 + [('rock', 2, 1)] * 6 + [('dork', 1, 1)] * 3 + [('lramp', 3, 1)] * 3
           + [('other', 3, 0)] * 51)


class SimulateTest(unittest.TestCase):
    def test_seeded_run_is_reproducible(self):
        # Golden values pinned when the simulation moved out of scripts/deck_stats.py, so a refactor that
        # changes the model shows up here. Update them only for an intended model change.
        cast, lands4, drops4, ramp2, mulls = goldfish.simulate(LIBRARY, 4, 500, random.Random(7))
        self.assertEqual(sum(t <= 4 for t in cast), 464)
        self.assertEqual(sum(t <= 3 for t in cast), 267)
        self.assertAlmostEqual(lands4, 4.296)
        self.assertAlmostEqual(drops4, 0.728)
        self.assertAlmostEqual(ramp2, 0.584)
        self.assertEqual(dict(mulls), {0: 394, 1: 86, 2: 15, 3: 5})

    def test_no_lands_never_casts(self):
        cast, *_ = goldfish.simulate([('other', 2, 0)] * 99, 2, 50, random.Random(1))
        self.assertEqual(set(cast), {99})


if __name__ == '__main__':
    unittest.main()
