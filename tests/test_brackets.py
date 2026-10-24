import unittest

from mtg import brackets

MV = {'Thassa\'s Oracle': 2, 'Demonic Consultation': 1, 'Big A': 4, 'Big B': 3}.get


def combo(cards, bracket='Powerful'):
    return {'cards': cards, 'bracket': bracket}


class FastTest(unittest.TestCase):
    def test_cheap_pieces_are_fast(self):
        self.assertTrue(brackets.is_fast(combo(["Thassa's Oracle", 'Demonic Consultation']), MV))

    def test_seven_mana_powerful_combo_is_not_fast(self):
        self.assertFalse(brackets.is_fast(combo(['Big A', 'Big B']), MV))

    def test_ruthless_is_fast_whatever_it_costs(self):
        self.assertTrue(brackets.is_fast(combo(['Big A', 'Big B'], 'Ruthless'), MV))

    def test_unknown_mana_value_counts_as_fast(self):
        self.assertTrue(brackets.is_fast(combo(['Big A', 'Mystery Card']), MV))
        self.assertIsNone(brackets.total_mv(combo(['Big A', 'Mystery Card']), MV))


if __name__ == '__main__':
    unittest.main()
