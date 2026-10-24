import os
import tempfile
import unittest

from mtg import profile

PROFILE = """# Tester

## Play log
Newest first, one block per game or session:
```
### YYYY-MM-DD — Deck name
- Result: won / lost / how the game ended
```

### 2026-01-01 — Old Deck
- Result: lost

## Later section
"""


class EntryTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, 'tester.md')
        with open(self.path, 'w') as f:
            f.write(PROFILE)
        self.addCleanup(lambda: (os.remove(self.path), os.rmdir(self.dir)))

    def test_render_fills_every_field(self):
        entry = profile.render_entry('2026-02-02', 'New Deck', result='won, 1st of 4', flopped='Sol Ring')
        self.assertEqual(entry, '### 2026-02-02 — New Deck\n- Result: won, 1st of 4\n- Fun: not given\n'
                                '- Flopped: Sol Ring\n- Change: not given\n')

    def test_add_puts_the_entry_first_below_the_template(self):
        profile.add_entry('tester', profile.render_entry('2026-02-02', 'New Deck', result='won'), self.dir)
        text = open(self.path).read()
        self.assertLess(text.index('```\n\n### 2026-02-02 — New Deck'), text.index('### 2026-01-01'))
        self.assertIn('- Change: not given\n\n### 2026-01-01 — Old Deck', text)
        self.assertEqual(text.count('### YYYY-MM-DD'), 1)

    def test_a_backfilled_older_game_goes_below_newer_entries(self):
        profile.add_entry('tester', profile.render_entry('2025-11-01 to 2025-12-24', 'Older Deck'), self.dir)
        text = open(self.path).read()
        self.assertLess(text.index('### 2026-01-01 — Old Deck'), text.index('### 2025-11-01 to 2025-12-24'))

    def test_add_without_a_play_log_raises(self):
        with open(self.path, 'w') as f:
            f.write('# Tester\n')
        with self.assertRaises(ValueError):
            profile.add_entry('tester', 'x', self.dir)


if __name__ == '__main__':
    unittest.main()
