import unittest
from unittest import mock

from mtg import archidekt, printings


def parsed(*cards, card_errors=()):
    """A massDeckEdit response: cards are (name as typed, id, oracle types)."""
    return {'syntaxErrors': [], 'cardErrors': list(card_errors), 'categories': [],
            'toAdd': [{'quantity': 1, 'name': n, 'categories': [],
                       'card': {'id': i, 'oracleCard': {'types': t}}} for n, i, t in cards],
            'toRemove': []}


class ResolveTest(unittest.TestCase):
    def setUp(self):  # no printing picks unless a test sets them: every card goes through massDeckEdit
        p = mock.patch.object(printings, 'best', return_value={})
        self.best = p.start()
        self.addCleanup(p.stop)

    def test_picked_printing_is_used_and_a_missing_pick_falls_back(self):
        self.best.return_value = {'Sol Ring': ['sr-best', 'sr-next'], 'Counterspell': ['cs-gone']}
        archidekt_has = {'sr-next': {'id': 22, 'uid': 'sr-next', 'oracleCard': {'types': ['Artifact']}}}

        def call(method, path, body=None):
            if method == 'GET':  # the uid lookup
                return {'results': [archidekt_has[u] for u in path.split('uids=')[1].split(',') if u in archidekt_has],
                        'next': None}
            self.assertEqual(body['edit'], '1 Counterspell\n')  # only the card with no usable pick
            return parsed(('Counterspell', 9, ['Instant']))

        with mock.patch.object(archidekt, 'call', side_effect=call):
            got = archidekt.resolve(['Sol Ring', 'Counterspell'])
        self.assertEqual(got, {'Sol Ring': (22, 'Artifact', True), 'Counterspell': (9, 'Instant', False)})

    def test_one_request_gives_ids_and_type_categories(self):
        reply = parsed(('Sol Ring', 1, ['Artifact']), ('Dryad Arbor', 2, ['Land', 'Creature']),
                       ('Brazen Borrower', 3, ['Creature']))
        with mock.patch.object(archidekt, 'call', return_value=reply) as call:
            got = archidekt.resolve(['Sol Ring', 'Dryad Arbor', 'Brazen Borrower', 'Sol Ring'])
        self.assertEqual(call.call_count, 1)
        self.assertEqual(call.call_args.args[2]['edit'], '1 Sol Ring\n1 Dryad Arbor\n1 Brazen Borrower\n')
        self.assertEqual(got, {'Sol Ring': (1, 'Artifact', False), 'Dryad Arbor': (2, 'Land', False),
                               'Brazen Borrower': (3, 'Creature', False)})

    def test_unknown_card_raises_naming_it(self):
        reply = parsed(card_errors=['Could not find a card matching Notacard'])
        with mock.patch.object(archidekt, 'call', return_value=reply):
            with self.assertRaisesRegex(KeyError, 'Notacard'):
                archidekt.resolve(['Notacard'])

    def test_no_names_makes_no_request(self):
        with mock.patch.object(archidekt, 'call') as call:
            self.assertEqual(archidekt.resolve([]), {})
        call.assert_not_called()


if __name__ == '__main__':
    unittest.main()
