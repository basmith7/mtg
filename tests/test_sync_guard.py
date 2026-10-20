import copy
import os
import tempfile
import unittest
from unittest import mock

from mtg import archidekt
from tests.test_archidekt_deck import DECK


class SyncGuardTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.site = dict(copy.deepcopy(DECK), id=7, updatedAt='2026-10-20T10:00:00Z')
        self.writes = []

        def call(method, path, body=None, auth=True):
            if method == 'GET':
                return copy.deepcopy(self.site)
            self.writes.append((method, path, body))

        for target, value in [('call', call), ('SEEN', os.path.join(self.dir, 'seen.json')),
                              ('resolve', lambda names: {n: (1, 'Creature') for n in names})]:
            p = mock.patch.object(archidekt, target, value)
            p.start()
            self.addCleanup(p.stop)
        p = mock.patch.dict(os.environ, {'HOME': self.dir})  # backups go to ~/.cache/mtg-backups
        p.start()
        self.addCleanup(p.stop)

    def deck_file(self, primer):
        path = os.path.join(self.dir, 'q.txt')
        with open(path, 'w') as f:
            f.write('# Q – Games (B3.75) | R\nCommander: Q, Stacking the Deck\n1 Q, Stacking the Deck\n'
                    '1 Sol Ring\n1 Treasure\n29 Mountain\n')
        with open(os.path.join(self.dir, 'q.md'), 'w') as f:
            f.write(primer)
        return path

    def sync(self, primer=None, **kw):
        primer = archidekt.export(self.site)['primer'] if primer is None else primer
        return archidekt.sync(7, self.deck_file(primer), os.path.join(self.dir, 'q.md'), **kw)

    def test_never_seen_is_stale_and_refused(self):
        with self.assertRaises(archidekt.Refused):
            self.sync()
        self.assertEqual(self.writes, [])

    def test_site_changed_since_pull_is_refused(self):
        archidekt.mark_seen(dict(self.site, updatedAt='2026-10-19T00:00:00Z'))
        with self.assertRaises(archidekt.Refused):
            self.sync()
        self.assertEqual(self.writes, [])
        self.assertTrue(self.sync(dry_run=True)['stale'])

    def test_fresh_deck_syncs_and_unchanged_primer_is_not_written(self):
        archidekt.mark_seen(self.site)
        s = self.sync()
        self.assertFalse(s['primer'])
        self.assertEqual([p for _, p, _ in self.writes], ['/api/decks/7/modifyCards/v2/'])  # Mountain 30 -> 29

    def test_force_overrides_stale(self):
        self.sync(force=True)
        self.assertTrue(self.writes)

    def test_changed_primer_over_rich_site_formatting_is_refused(self):
        self.site['description'] = '{"ops": [{"insert": "Old", "attributes": {"italic": true}}, {"insert": "\\n"}]}'
        archidekt.mark_seen(self.site)
        with self.assertRaises(archidekt.Refused) as e:
            self.sync(primer='New primer.')
        self.assertIn('italic', str(e.exception))
        self.assertEqual(self.writes, [])
        self.assertEqual(self.sync(primer='Old')['primer'], False)  # same text: left alone, no refusal


if __name__ == '__main__':
    unittest.main()
