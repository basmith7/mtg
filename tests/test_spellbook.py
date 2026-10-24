import json
import os
import unittest
import urllib.error
from unittest import mock

from mtg import spellbook

FIXTURE = os.path.join(os.path.dirname(__file__), 'fixtures', 'spellbook_estimate_thoracle.json')


class EstimateBracketTest(unittest.TestCase):
    def test_parses_a_real_reply(self):
        reply = json.load(open(FIXTURE))
        with mock.patch.object(spellbook.http, 'request', return_value=reply) as req:
            est = spellbook.estimate_bracket(['Tymna the Weaver'], ["Thassa's Oracle", 'Demonic Consultation'])
        self.assertTrue(req.call_args.args[1].endswith('/estimate-bracket'))
        self.assertEqual((est['tag'], est['name']), ('R', 'Ruthless'))
        flags = {c['name']: c for c in est['cards']}
        self.assertTrue(flags['Armageddon']['mass_land_denial'])
        self.assertTrue(flags['Time Warp']['extra_turn'])
        self.assertTrue(flags["Thassa's Oracle"]['game_changer'])
        thoracle = est['combos'][0]
        self.assertTrue(thoracle['two_card'])
        self.assertEqual(sorted(thoracle['cards']), ['Demonic Consultation', "Thassa's Oracle"])
        self.assertEqual(thoracle['bracket'], 'Ruthless')

    def test_http_error_gives_none(self):
        err = urllib.error.HTTPError('u', 500, 'boom', {}, None)
        with mock.patch.object(spellbook.http, 'request', side_effect=err):
            self.assertIsNone(spellbook.estimate_bracket([], ['Sol Ring']))


if __name__ == '__main__':
    unittest.main()
