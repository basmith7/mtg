import unittest
from unittest import mock

from mtg import edhrec, scores


class SaltSummaryTest(unittest.TestCase):
    def test_average_top_and_over_two(self):
        salt = {'Cyclonic Rift': 2.4, 'Propaganda': 2.05, 'Sol Ring': 1.6, 'Llanowar Elves': 0.2}
        s = scores.salt_summary(['Cyclonic Rift', 'Propaganda', 'Sol Ring', 'Llanowar Elves', 'Unscored'], salt)
        self.assertAlmostEqual(s['avg'], (2.4 + 2.05 + 1.6 + 0.2) / 4)
        self.assertEqual(s['top'][0], ('Cyclonic Rift', 2.4))
        self.assertEqual(len(s['top']), scores.TOP_SALT)
        self.assertEqual(s['over2'], ['Cyclonic Rift', 'Propaganda'])

    def test_no_scores(self):
        self.assertIsNone(scores.salt_summary(['A'], {})['avg'])


class TableShareTest(unittest.TestCase):
    def test_share_of_table_touching_spells(self):
        deck = {'Treachery': frozenset({'theft'}), 'Sol Ring': frozenset(), 'Time Warp': frozenset({'extra-turn'}),
                'Propaganda': frozenset({'stax'})}
        self.assertEqual(scores.table_share(deck), 0.5)  # extra turns alone don't touch other players
        self.assertEqual(scores.table_share({}), 0.0)


class SaltSourceTest(unittest.TestCase):
    def test_salt_reads_names_from_the_table(self):
        with mock.patch.object(edhrec, '_salt_table', return_value={'Sol Ring': 1.59, 'Fire': 0.3}):
            self.assertEqual(edhrec.salt(['Sol Ring', 'Fire', 'Nope']), {'Sol Ring': 1.59, 'Fire': 0.3})


if __name__ == '__main__':
    unittest.main()
