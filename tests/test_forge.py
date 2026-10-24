import os
import unittest
from collections import Counter

from mtg import forge

FIXTURE = os.path.join(os.path.dirname(__file__), 'fixtures', 'forge_sim_4pod.txt')


class ToDck(unittest.TestCase):
    def test_partners_and_double_faced_names(self):
        cards = Counter({'Krark, the Thumbless': 1, 'Sakashima of a Thousand Faces': 1, 'Fire // Ice': 1,
                         'Jwari Disruption // Jwari Ruins': 1, 'Island': 30})
        dck = forge.to_dck('Krark – Heads I Win (B3.75)', ['Krark, the Thumbless', 'Sakashima of a Thousand Faces'],
                           cards, split={'Fire // Ice'})
        self.assertEqual(dck, '\n'.join([
            '[metadata]',
            'Name=Krark Heads I Win B3 75',
            '[Commander]',
            '1 Krark, the Thumbless',
            '1 Sakashima of a Thousand Faces',
            '[Main]',
            '1 Fire // Ice',
            '30 Island',
            '1 Jwari Disruption',
        ]) + '\n')


class Parse(unittest.TestCase):
    def test_real_four_player_pod(self):
        with open(FIXTURE) as f:
            result = forge.parse(f.read())
        self.assertEqual(result['games'], sum(result['wins'].values()) + result['draws'])
        self.assertEqual(result['games'], 5)
        self.assertIn('Talrand Counter Target Dan', result['wins'])
        self.assertIn('Jwari Disruption // Jwari Ruins', result['unsupported'])

    def test_draw_and_win_lines(self):
        text = ('Stopping slow match as draw\n\nGame Result: Game 1 ended in a Draw! Took 600012 ms.\n'
                '\nGame Result: Game 2 ended in 41000 ms. Ai(3)-Phage Voltron has won!\n')
        self.assertEqual(forge.parse(text), {'games': 2, 'wins': Counter({'Phage Voltron': 1}), 'draws': 1,
                                             'unsupported': []})


if __name__ == '__main__':
    unittest.main()
