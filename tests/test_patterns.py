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

    def test_table_tags_on_real_oracle_text(self):
        cases = {
            'stax': ('Propaganda', "Creatures can't attack you unless their controller pays {2} for each creature "
                                   "they control that's attacking you."),
            'theft': ('Treachery', 'Enchant creature\nWhen this Aura enters, untap up to five lands.\n'
                                   'You control enchanted creature.'),
            'donate': ('Xantcha, Sleeper Agent', 'Xantcha enters under the control of an opponent of your choice.'),
            'goad': ('Kardur, Doomscourge', 'When Kardur enters, until your next turn, creatures your opponents '
                                            'control attack each combat if able and attack a player other than you if able.'),
            'vote': ("Council's Judgment", 'Will of the council — Starting with you, each player votes for a nonland '
                                           "permanent you don't control."),
            'coin': ("Krark's Thumb", 'If you would flip a coin, instead flip two coins and ignore one.'),
            'monarch': ('Queen Marchesa', 'When Queen Marchesa enters, you become the monarch.'),
        }
        for tag, (name, text) in cases.items():
            self.assertIn(tag, patterns.classify(card(name, text)), name)

    def test_own_cost_increase_is_not_stax(self):
        text = 'This spell costs {1} more to cast for each creature you control.'
        self.assertNotIn('stax', patterns.classify(card('X', text)))
        self.assertIn('stax', patterns.classify(card('Thalia', 'Noncreature spells cost {1} more to cast.')))

    def test_donate_is_not_theft(self):
        tags = patterns.classify(card('Donate', 'Target player gains control of target permanent you control.'))
        self.assertIn('donate', tags)
        self.assertNotIn('theft', tags)

    def test_sol_ring_is_nothing(self):
        self.assertEqual(patterns.classify(card('Sol Ring', '{T}: Add {C}{C}.')), frozenset())


if __name__ == '__main__':
    unittest.main()
