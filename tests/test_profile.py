import os
import tempfile
import unittest

from mtg import profile

PROFILE = """# Sam

## Preferences
- Likes green.

## What Sam enjoys (distilled)
Keep this short.

- Commanders that play for other people (Xantcha, 2026-10-16). Sam loved
  the mechanic itself.
- Coin flips.

## Play log
- Not an enjoys line.
"""


class EnjoysTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def write(self, text):
        with open(os.path.join(self.dir.name, 'sam.md'), 'w') as f:
            f.write(text)

    def test_reads_only_the_enjoys_bullets_joining_wrapped_lines(self):
        self.write(PROFILE)
        self.assertEqual(profile.enjoys('sam', self.dir.name), [
            'Commanders that play for other people (Xantcha, 2026-10-16). Sam loved the mechanic itself.',
            'Coin flips.'])

    def test_profile_without_the_section_enjoys_nothing(self):
        self.write('# Sam\n\n## Play log\n- A game.\n')
        self.assertEqual(profile.enjoys('sam', self.dir.name), [])


if __name__ == '__main__':
    unittest.main()
