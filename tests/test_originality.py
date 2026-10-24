import os
import tempfile
import unittest
from unittest import mock

from mtg import decklist, roles, scores
from tests.test_gems import zur_cards


def card(name, type_line, text='', keywords=()):
    return {'name': name, 'type_line': type_line, 'oracle_text': text, 'keywords': list(keywords)}


class StapleShareTest(unittest.TestCase):
    def test_share_counts_cards_at_or_over_the_threshold(self):
        # Path to Exile 43.8%, Grand Abolisher 33.6%, Energy Flux 8.0%; the made-up card isn't on the page.
        deck = ['Path to Exile', 'Grand Abolisher', 'Energy Flux', 'Homebrew Thing']
        share, staples = scores.staple_share(deck, zur_cards())
        self.assertEqual(staples, ['Path to Exile'])
        self.assertEqual(share, 0.25)
        self.assertEqual(scores.staple_share(deck, zur_cards(), threshold=30)[1],
                         ['Path to Exile', 'Grand Abolisher'])


class OverlapTest(unittest.TestCase):
    def deck(self, d, name, cards):
        path = os.path.join(d, name)
        with open(path, 'w') as f:
            f.write('\n'.join(f'1 {c}' for c in cards))
        return path

    def test_jaccard_ignores_basics_and_sorts_by_shared(self):
        with tempfile.TemporaryDirectory() as d:
            mine = decklist.parse(self.deck(d, 'a.txt', ['Sol Ring', 'Counterspell', 'Opt', 'Island']))[2]
            near = decklist.parse(self.deck(d, 'b.txt', ['Sol Ring', 'Counterspell', 'Brainstorm', 'Island']))[2]
            far = decklist.parse(self.deck(d, 'c.txt', ['Sol Ring', 'Llanowar Elves', 'Forest']))[2]
            out = scores.overlap(mine, {'c.txt': set(far), 'b.txt': set(near)})
        self.assertEqual(out[0], ('b.txt', 2, 0.5))     # {Sol Ring, Counterspell} of 4 non-basics
        self.assertEqual(out[1][:2], ('c.txt', 1))
        self.assertAlmostEqual(out[1][2], 0.25)


class DensityTest(unittest.TestCase):
    data = {
        'Llanowar Elves': card('Llanowar Elves', 'Creature — Elf Druid', '{T}: Add {G}.'),
        'Elvish Mystic': card('Elvish Mystic', 'Creature — Elf Druid', '{T}: Add {G}.'),
        'Elvish Archdruid': card('Elvish Archdruid', 'Creature — Elf Druid',
                                 'Other Elf creatures you control get +1/+1.\n{T}: Add {G} for each Elf you control.'),
        'Sol Ring': card('Sol Ring', 'Artifact', '{T}: Add {C}{C}.'),
        'Island': card('Island', 'Basic Land — Island', '({T}: Add {U}.)'),
    }

    def test_elves_and_their_lord_interact(self):
        # Pairs: lord+elf, lord+elf interact; the two plain elves don't: 2 of 3.
        self.assertAlmostEqual(scores.density(['Llanowar Elves', 'Elvish Mystic', 'Elvish Archdruid'], self.data), 2 / 3)

    def test_sol_ring_and_island_dont(self):
        self.assertEqual(scores.density(['Sol Ring', 'Island', 'Llanowar Elves'], self.data), 0.0)

    def test_tokens_counters_and_keywords(self):
        data = {
            'Maker': card('Maker', 'Sorcery', 'Create two 1/1 white Soldier creature tokens.'),
            'Anthem': card('Anthem', 'Enchantment', 'Tokens you control get +1/+1.'),
            'Grower': card('Grower', 'Creature — Ooze', 'Put a +1/+1 counter on target creature.'),
            'Payoff': card('Payoff', 'Creature — Beast', 'Whenever one or more +1/+1 counters are put on a creature you control, draw a card.'),
            'Flier': card('Flier', 'Creature — Bird', 'Flying', ['Flying']),
            'Flier2': card('Flier2', 'Creature — Bird', 'Flying', ['Flying']),
        }
        self.assertEqual(scores.density(['Maker', 'Anthem'], data), 1.0)
        self.assertEqual(scores.density(['Grower', 'Payoff'], data), 1.0)
        self.assertEqual(scores.density(['Flier', 'Flier2'], data), 0.0)   # sharing a keyword isn't naming it


class AlternativesTest(unittest.TestCase):
    def test_same_role_minus_excluded_and_format_staples_most_played_first(self):
        found = [{'name': n, 'edhrec_rank': r} for n, r in (
            ('Swords to Plowshares', 5), ('Chaos Warp', 40), ('Path to Exile', 1200), ('Generous Gift', 1500),
            ('Stroke of Midnight', 2100), ('Fateful Absence', 2500), ('Sundering Eruption', 3000))]
        with mock.patch.object(roles, 'role_hits', return_value={r: ({'Swords to Plowshares'} if r == 'removal' else set())
                                                                 for r in roles.ROLES}), \
                mock.patch.object(roles.scryfall, 'search', return_value=iter(found)) as search:
            alts = roles.alternatives('Swords to Plowshares', 'WR', exclude={'Path to Exile'})
        self.assertEqual(alts, ['Generous Gift', 'Stroke of Midnight', 'Fateful Absence'])  # Chaos Warp: top 1000
        q = search.call_args[0][0]
        self.assertIn('otag:removal', q)
        self.assertIn('id<=WR', q)
        self.assertIn('-is:gamechanger', q)
        self.assertEqual(search.call_args[1], {'order': 'edhrec', 'dir': 'asc'})

    def test_no_role_no_search(self):
        with mock.patch.object(roles, 'role_hits', return_value={r: set() for r in roles.ROLES}), \
                mock.patch.object(roles.scryfall, 'search') as search:
            self.assertEqual(roles.alternatives('Island', 'U'), [])
        search.assert_not_called()


if __name__ == '__main__':
    unittest.main()
