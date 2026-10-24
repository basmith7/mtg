import unittest

from mtg import patterns


def card(name, text):
    return {'name': name, 'oracle_text': text}


class ClassifyTest(unittest.TestCase):
    def test_armageddon_is_mld(self):
        self.assertEqual(patterns.classify(card('Armageddon', 'Destroy all lands.')), {'mld'})

    def test_jokulhaups_is_mld(self):
        text = 'Destroy all artifacts, creatures, and lands. They can\'t be regenerated.'
        self.assertIn('mld', patterns.classify(card('Jokulhaups', text)))

    def test_time_warp_is_extra_turn(self):
        text = 'Target player takes an extra turn after this one.'
        self.assertEqual(patterns.classify(card('Time Warp', text)), {'extra-turn'})

    def test_sol_ring_is_nothing(self):
        self.assertEqual(patterns.classify(card('Sol Ring', '{T}: Add {C}{C}.')), frozenset())


if __name__ == '__main__':
    unittest.main()
