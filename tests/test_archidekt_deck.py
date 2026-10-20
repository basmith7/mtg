import json
import os
import tempfile
import unittest
from collections import Counter

from mtg import archidekt, decklist, quill


def entry(name, qty=1, cats=('Creature',), deleted=False):
    return {'id': abs(hash(name)) % 10**6, 'quantity': qty, 'categories': list(cats), 'modifier': 'Normal',
            'deletedAt': '2026-01-01' if deleted else None, 'card': {'id': 1, 'oracleCard': {'name': name}}}


DECK = {
    'name': 'Q – Games (B3.75)',
    'description': quill.to_delta('## How it wins\nCopy **big** spells.'),
    'categories': [{'name': 'Tokens', 'includedInDeck': True}, {'name': 'Considering', 'includedInDeck': False}],
    'cards': [
        entry('Q, Stacking the Deck', cats=['Commander']),
        entry('Sol Ring', cats=['Artifact']),
        entry('Mountain', 30, ['Land']),
        entry('Treasure', cats=['Tokens']),          # in-deck category: counts
        entry('Lightning Bolt', cats=['maybeboard']),  # side boards compare case-insensitively
        entry('Shock', cats=['Considering']),         # category not included in the deck
        entry('Opt', deleted=True),
    ],
}


class ExportTest(unittest.TestCase):
    def test_export(self):
        e = archidekt.export(DECK)
        self.assertEqual(e['commanders'], ['Q, Stacking the Deck'])
        self.assertEqual(e['cards'], Counter({'Q, Stacking the Deck': 1, 'Sol Ring': 1, 'Mountain': 30, 'Treasure': 1}))
        self.assertEqual(e['primer'], '## How it wins\nCopy **big** spells.')
        self.assertEqual(e['dropped'], [])


class CompareTest(unittest.TestCase):
    def write(self, cards, primer=None):
        d = tempfile.mkdtemp()
        path = os.path.join(d, 'q.txt')
        with open(path, 'w') as f:
            f.write(decklist.render('Q – Games (B3.75)', 'R', ['Q, Stacking the Deck'], Counter(cards)))
        if primer is not None:
            with open(os.path.join(d, 'q.md'), 'w') as f:
                f.write(primer)
        return path

    def test_matching_deck(self):
        e = archidekt.export(DECK)
        c = archidekt.compare(self.write(e['cards'], e['primer'] + '\n'), DECK)
        self.assertEqual(c, {'missing_on_site': [], 'extra_on_site': [], 'qty_diffs': [],
                             'commanders_match': True, 'primer': 'same'})

    def test_differences(self):
        cards = dict(archidekt.export(DECK)['cards'], **{'Mountain': 29, 'Arcane Signet': 1})
        del cards['Sol Ring']
        c = archidekt.compare(self.write(cards, 'Something else.'), DECK)
        self.assertEqual(c['missing_on_site'], ['Arcane Signet'])
        self.assertEqual(c['extra_on_site'], ['Sol Ring'])
        self.assertEqual(c['qty_diffs'], ['Mountain: 29 here, 30 on site'])
        self.assertEqual(c['primer'], 'differs')
        self.assertEqual(archidekt.compare(self.write(cards), DECK)['primer'], 'site only')


class DeckIdTest(unittest.TestCase):
    def test_deck_id(self):
        self.assertEqual(archidekt.deck_id('27632721'), 27632721)
        self.assertEqual(archidekt.deck_id('https://archidekt.com/decks/27632721/q_games'), 27632721)
        self.assertIsNone(archidekt.deck_id('https://moxfield.com/decks/abc'))


if __name__ == '__main__':
    unittest.main()
