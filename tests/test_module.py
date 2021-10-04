import unittest

import stactools.worldpop


class TestModule(unittest.TestCase):
    def test_version(self):
        self.assertIsNotNone(stactools.worldpop.__version__)
