import random
import unittest
from unittest import mock

from mtg import discovery, scryfall


def card(name, rank, ident='R'):
    return {'name': name, 'edhrec_rank': rank, 'color_identity': list(ident)}


GOAD = [card('Popular Goad', 100), card('Obscure Goad', 9000, 'BR'), card('Shared One', 5000)]
COIN = [card('Shared One', 5000), card('Unranked Coin', None, 'UR')]
LEGENDS = [card('Dragon Lord', 300), card('Wyrm King', 800), card('Old Drake', 2000)]


def fake_search(query, **_):
    if 'goad' in query:
        return iter(GOAD)
    if 'flip a coin' in query:
        return iter(COIN)
    return iter(LEGENDS)


class MechanicsTest(unittest.TestCase):
    def test_enjoys_bullets_map_to_mechanics_by_keyword(self):
        enjoys = ['Commanders that leave their owner\'s control and play for other people (Xantcha).']
        self.assertEqual(discovery.mechanics_for(enjoys), ['control-swap'])
        self.assertEqual(discovery.mechanics_for(['Goading the table and coin flips']), ['goad', 'coin'])
        self.assertEqual(discovery.mechanics_for(['Big creatures']), [])

    def test_every_query_is_bounded_to_commanders_and_monarch_reads_oracle_text(self):
        for m in discovery.MECHANICS:
            self.assertTrue(discovery.query(m).endswith('is:commander f:commander'), m)
        self.assertIn('o:monarch', discovery.query('monarch'))
        self.assertNotIn('kw:', ' '.join(discovery.MECHANICS.values()))
        self.assertEqual(discovery.query('goad', 'BR'), 'o:goad is:commander f:commander id<=BR')


@mock.patch.object(scryfall, 'search', side_effect=fake_search)
class CandidatesTest(unittest.TestCase):
    def test_least_played_first_and_unranked_before_all(self, _):
        rows = discovery.candidates(['goad', 'coin'])
        self.assertEqual([r[0] for r in rows], ['Unranked Coin', 'Obscure Goad', 'Shared One', 'Popular Goad'])

    def test_a_commander_with_two_mechanics_appears_once_with_both(self, _):
        rows = {r[0]: r for r in discovery.candidates(['goad', 'coin'])}
        self.assertEqual(rows['Shared One'][1], ['goad', 'coin'])
        self.assertEqual(rows['Obscure Goad'][2:], (9000, 'BR'))

    def test_excluded_names_are_skipped(self, _):
        rows = discovery.candidates(['goad'], exclude={'Obscure Goad', 'Popular Goad // Back Face'})
        self.assertEqual([r[0] for r in rows], ['Shared One'])


@mock.patch.object(scryfall, 'search', side_effect=fake_search)
class ChallengeTest(unittest.TestCase):
    def test_same_seed_same_challenge(self, _):
        for seed in range(20):
            self.assertEqual(discovery.challenge(random.Random(seed)), discovery.challenge(random.Random(seed)))

    def test_pool_queries_by_kind(self, _):
        art = discovery.challenge(random.Random(1), ['art'])
        self.assertRegex(art['query'], r'^atag:[a-z]+ f:commander$')
        self.assertIn(art['text'].split()[2], 'Dragon Lord Wyrm King Old Drake')
        self.assertRegex(discovery.challenge(random.Random(1), ['flavour'])['query'], r'^ft:[a-z]+ f:commander$')
        self.assertRegex(discovery.challenge(random.Random(1), ['year'])['query'], r'^year:\d{4} f:commander$')

    def test_commander_challenge_pools_by_its_colours(self, search):
        with mock.patch.object(discovery, 'MECHANICS', {'goad': 'o:goad'}):
            c = discovery.challenge(random.Random(0), ['commander'], exclude={'Popular Goad', 'Shared One'})
        self.assertEqual(c['query'], 'id<=BR f:commander')
        self.assertIn('Obscure Goad', c['text'])


class AvoidTest(unittest.TestCase):
    def test_dash_reads_names_from_stdin_skipping_comments(self):
        import importlib.util, io, os
        path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'discover.py')
        spec = importlib.util.spec_from_file_location('discover', path)
        discover = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(discover)
        with mock.patch('sys.stdin', io.StringIO('# from the meta\nZedruu the Greathearted\n\n  Xantcha, Sleeper Agent \n')):
            self.assertEqual(discover.read_names('-'), {'Zedruu the Greathearted', 'Xantcha, Sleeper Agent'})


if __name__ == '__main__':
    unittest.main()
