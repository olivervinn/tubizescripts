import unittest
from unittest.mock import patch
import os
import sys
from tubize.app import library


class LibraryTestCase(unittest.TestCase):
    def test_can_create_library_example(self):
        testargs = ["-d", "-force", "-i", "./test/examples"]
        with patch.object(sys, 'argv', testargs):
            videos = library.main()
        self.assertEqual(len(videos),1)
