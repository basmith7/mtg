import os
import tempfile
import unittest
from unittest import mock

from mtg import config


class ConfigTest(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp()
        os.write(fd, b'# comment\nMTG_TEST_A="from file"\nMTG_TEST_B=\'quoted\'\n')
        os.close(fd)
        self.addCleanup(os.remove, self.path)
        patcher = mock.patch.object(config, 'env_file', return_value=self.path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_reads_file_and_strips_quotes(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('MTG_TEST_A', None)
            self.assertEqual(config.get('MTG_TEST_A'), 'from file')
            self.assertEqual(config.get('MTG_TEST_B'), 'quoted')

    def test_environment_wins(self):
        with mock.patch.dict(os.environ, {'MTG_TEST_A': 'from env'}):
            self.assertEqual(config.get('MTG_TEST_A'), 'from env')

    def test_missing_key(self):
        self.assertIsNone(config.get('MTG_TEST_MISSING', required=False))
        with self.assertRaises(KeyError) as e:
            config.get('MTG_TEST_MISSING')
        self.assertIn('MTG_TEST_MISSING', str(e.exception))
        self.assertIn('.env.example', str(e.exception))


if __name__ == '__main__':
    unittest.main()
