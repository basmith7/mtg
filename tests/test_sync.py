import copy
import os
import tempfile
import unittest
from unittest import mock

from mtg import archidekt, decklist
from tests.test_archidekt_deck import DECK

SITE_VERSION = '2026-10-20T10:00:00Z'


class SyncTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.site = dict(copy.deepcopy(DECK), id=7, updatedAt=SITE_VERSION)
        self.writes, self.bodies = [], []

        def call(method, path, body=None, auth=True):
            if method == 'GET':
                return copy.deepcopy(self.site)
            self.writes.append(path)
            self.bodies.append(body)

        for target, value in [('call', call), ('resolve', lambda names: {n: (1, 'Creature', True) for n in names})]:
            p = mock.patch.object(archidekt, target, value)
            p.start()
            self.addCleanup(p.stop)
        p = mock.patch.dict(os.environ, {'XDG_CACHE_HOME': self.dir})  # backups
        p.start()
        self.addCleanup(p.stop)

    def deck_file(self, updated=SITE_VERSION, primer=None, cards=None):
        """A local copy of the site deck pulled at version `updated`, then edited by `cards` changes."""
        e = archidekt.export(self.site)
        cards = {c: q for c, q in {**e['cards'], **(cards or {})}.items() if q}
        path = os.path.join(self.dir, 'q.txt')
        with open(path, 'w') as f:
            f.write(decklist.render(e['name'], 'R', e['commanders'], cards,
                                    archidekt.url(7), updated))
        with open(os.path.join(self.dir, 'q.md'), 'w') as f:
            f.write(e['primer'] if primer is None else primer)
        return path

    def test_unchanged_copy_has_nothing_to_push(self):
        s = archidekt.sync(self.deck_file(), dry_run=True)
        self.assertEqual((s['removed'], s['added'], s['changed'], s['primer'], s['stale']), ([], [], [], False, False))

    def test_dry_run_reports_each_kind_of_change_and_writes_nothing(self):
        s = archidekt.sync(self.deck_file(primer='New.', cards={'Mountain': 29, 'Arcane Signet': 1, 'Sol Ring': 0}),
                           dry_run=True)
        self.assertEqual((s['removed'], s['added'], s['changed'], s['primer']),
                         (['Sol Ring'], ['1 Arcane Signet'], ['Mountain: 30 -> 29'], True))
        self.assertEqual(self.writes, [])

    def test_site_changed_since_pull_is_refused(self):
        for updated in ('2026-10-19T00:00:00Z', None):  # an older version, or none recorded
            with self.assertRaises(archidekt.Refused):
                archidekt.sync(self.deck_file(updated, cards={'Mountain': 29}))
        self.assertEqual(self.writes, [])
        self.assertTrue(archidekt.sync(self.deck_file(None), dry_run=True)['stale'])

    def test_push_writes_and_records_the_new_version(self):
        path = self.deck_file(cards={'Mountain': 29})
        self.site['cards'][2]['quantity'] = 29  # what the site holds after the write
        self.site['updatedAt'] = '2026-10-20T11:00:00Z'
        with mock.patch.object(archidekt, 'deck', side_effect=[dict(DECK, id=7, updatedAt=SITE_VERSION),
                                                               copy.deepcopy(self.site)]):
            s = archidekt.sync(path)
        self.assertTrue(s['match'])
        self.assertEqual(self.writes, ['/api/decks/7/modifyCards/v2/'])  # primer unchanged: not written
        self.assertEqual(decklist.meta(path, 'updated'), '2026-10-20T11:00:00Z')
        self.assertTrue(os.path.exists(s['backup']))

    def test_force_overrides_stale(self):
        archidekt.sync(self.deck_file(None, cards={'Mountain': 29}), force=True)
        self.assertTrue(self.writes)

    def test_changed_primer_over_rich_site_formatting_is_refused(self):
        self.site['description'] = '{"ops": [{"insert": "Old", "attributes": {"italic": true}}, {"insert": "\\n"}]}'
        with self.assertRaises(archidekt.Refused) as e:
            archidekt.sync(self.deck_file(primer='New primer.'))
        self.assertIn('italic', str(e.exception))
        self.assertEqual(self.writes, [])
        self.assertFalse(archidekt.sync(self.deck_file(primer='Old'))['primer'])  # same text: left alone

    def test_reprint_moves_only_cards_on_another_printing_and_keeps_their_categories(self):
        # Site has id 1 for everything; Sol Ring and Mountain have another printing, but Mountain's
        # is only the site's own pick (no allowed printing), so it stays.
        picked = lambda names: {n: {'Sol Ring': (5, 'Other', True), 'Mountain': (6, 'Land', False)}.get(n, (1, 'Other', True))
                                for n in names}
        with mock.patch.object(archidekt, 'resolve', picked):
            self.assertEqual(archidekt.sync(self.deck_file(), dry_run=True)['reprinted'], [])  # off by default
            self.assertEqual(archidekt.sync(self.deck_file(), dry_run=True, reprint=True)['reprinted'], ['Sol Ring'])
            archidekt.sync(self.deck_file(), reprint=True)
        cards = [c for b in self.bodies if b and 'cards' in b for c in b['cards']]
        self.assertEqual([(c['action'], c['cardid'], c['categories']) for c in cards],
                         [('remove', 1, ['Artifact']), ('add', 5, ['Artifact'])])


if __name__ == '__main__':
    unittest.main()
