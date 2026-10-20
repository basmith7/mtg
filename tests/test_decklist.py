import os
import tempfile
import unittest
from collections import Counter

from mtg import decklist


class RenderTest(unittest.TestCase):
    def round_trip(self, *args):
        fd, path = tempfile.mkstemp(suffix='.txt')
        os.write(fd, decklist.render(*args).encode())
        os.close(fd)
        self.addCleanup(os.remove, path)
        return decklist.parse(path), decklist.commanders(path)

    def test_commander_list(self):
        cards = Counter({'Q, Stacking the Deck': 1, 'Sol Ring': 1, 'Mountain': 30})
        (name, colors, got), cmdrs = self.round_trip('Q – Games (B3.75)', 'R', ['Q, Stacking the Deck'],
                                                     cards, 'https://archidekt.com/decks/1')
        self.assertEqual((name, colors, got, cmdrs), ('Q – Games (B3.75)', 'R', cards, ['Q, Stacking the Deck']))

    def test_sixty_card_list(self):
        cards = Counter({'Legion Warboss': 4, 'Fire // Ice': 2})
        (name, colors, got), cmdrs = self.round_trip('Boros Legion', 'RW', [], cards)
        self.assertEqual((name, colors, got, cmdrs), ('Boros Legion', 'RW', cards, []))

    def test_meta_lines_are_replaced_or_added_after_the_header(self):
        fd, path = tempfile.mkstemp(suffix='.txt')
        os.write(fd, decklist.render('Boros Legion', 'RW', [], Counter({'Shock': 4}), 'https://archidekt.com/decks/1').encode())
        os.close(fd)
        self.addCleanup(os.remove, path)
        decklist.set_meta(path, 'updated', 'v1')
        decklist.set_meta(path, 'updated', 'v2')
        decklist.set_meta(path, 'source', 'https://archidekt.com/decks/2')
        self.assertEqual(open(path).read(), '# Boros Legion | RW\n# updated: v2\n# source: https://archidekt.com/decks/2\n4 Shock\n')
        self.assertEqual(decklist.parse(path), ('Boros Legion', 'RW', Counter({'Shock': 4})))


if __name__ == '__main__':
    unittest.main()
