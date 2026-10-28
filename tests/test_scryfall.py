import unittest
import urllib.error
from unittest import mock

from mtg import scryfall


class MatchingTest(unittest.TestCase):
    def test_names_match_by_full_name_or_front_face_across_chunks(self):
        names = [f'Card {i:03}' for i in range(120)] + ['Fire // Ice']
        hits = {'Card 007', 'Card 110', 'Fire // Ice'}

        def search(q, unique="cards"):
            return iter([{'name': n} for n in hits if f'!"{scryfall.front(n)}"' in q])

        with mock.patch.object(scryfall, 'search', side_effect=search) as s:
            self.assertEqual(scryfall.matching(names, 'otag:ramp'), ['Card 007', 'Card 110', 'Fire // Ice'])
        self.assertGreater(s.call_count, 1)  # long name lists are split
        self.assertTrue(all(len(c.args[0]) < 1000 for c in s.call_args_list))  # Scryfall truncates longer

    def test_a_chunk_with_no_match_is_empty_not_an_error(self):
        err = urllib.error.HTTPError('u', 404, 'none', {}, None)
        with mock.patch.object(scryfall, 'search', side_effect=err):
            self.assertEqual(scryfall.matching(['Sol Ring'], 'not:universesbeyond'), [])
            self.assertEqual(scryfall.ub_only(['Sol Ring']), ['Sol Ring'])


if __name__ == '__main__':
    unittest.main()
