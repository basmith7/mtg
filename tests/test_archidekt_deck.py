import unittest
from collections import Counter

from mtg import archidekt, quill


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


class DeckIdTest(unittest.TestCase):
    def test_deck_id_of(self):
        self.assertEqual(archidekt.deck_id_of('27632721'), 27632721)
        self.assertEqual(archidekt.deck_id_of('https://archidekt.com/decks/27632721/q_games'), 27632721)
        self.assertIsNone(archidekt.deck_id_of('https://moxfield.com/decks/abc'))


if __name__ == '__main__':
    unittest.main()
