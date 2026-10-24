import json
import os
import unittest
from unittest import mock

from mtg import edhrec, scores

FIXTURE = os.path.join(os.path.dirname(__file__), 'fixtures', 'edhrec_commander_zur.json')


def zur_cards():
    page = json.load(open(FIXTURE))
    with mock.patch.object(edhrec, '_fetch', return_value=page):
        return edhrec.commander('Zur the Enchanter')['cards']


class GemsTest(unittest.TestCase):
    def setUp(self):
        self.cards = zur_cards()

    def test_page_keeps_lift_and_trend(self):
        field = next(c for c in self.cards if c['name'] == 'Energy Field')
        self.assertAlmostEqual(field['lift'], 21.23, places=2)
        self.assertAlmostEqual(field['trend_zscore'], 0.11, places=2)

    def test_ranked_by_lift_under_the_inclusion_cap(self):
        names = [c['name'] for c in scores.gems(self.cards)]
        # Energy Field 14.3%, Energy Flux 8.0%; Diplomatic Immunity (42.7%) and Vanishing (16.9%) are over 15%.
        self.assertEqual(names, ['Energy Field', 'Energy Flux'])

    def test_higher_cap_lets_more_in_still_by_lift(self):
        names = [c['name'] for c in scores.gems(self.cards, max_inclusion=20)]
        self.assertEqual(names, ['Energy Field', 'Vanishing', 'Energy Flux'])

    def test_min_decks_cuts_thinly_played_cards(self):
        names = [c['name'] for c in scores.gems(self.cards, min_decks=2000)]
        self.assertEqual(names, ['Energy Field'])   # Energy Flux is in 1403 decks

    def test_excludes_deck_cards_case_insensitively(self):
        names = [c['name'] for c in scores.gems(self.cards, exclude={'energy field'})]
        self.assertEqual(names, ['Energy Flux'])

    def test_ties_broken_by_synergy(self):
        cards = [{'name': 'A', 'inclusion': 5, 'num_decks': 50, 'lift': 2.0, 'synergy': 0.1},
                 {'name': 'B', 'inclusion': 5, 'num_decks': 50, 'lift': 2.0, 'synergy': 0.3}]
        self.assertEqual([c['name'] for c in scores.gems(cards)], ['B', 'A'])


if __name__ == '__main__':
    unittest.main()
