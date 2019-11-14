"""Tests for attrs library in attr_overlay.py."""

import unittest
import tubize.libraryasset as T_LA
import tubize.videometainfo as T_VMI


class VideoMetaInfoTestCase(unittest.TestCase):
    """Test can get properties from video file."""
    def test_can_get_meta_info(self):
        filename = "./test/examples/videos/test.mp4"
        obj_ = T_VMI.VideoMetaInfo(filename)
        self.assertNotEqual(obj_, None)
        self.assertEqual(obj_.fps, 30)
        self.assertEqual(obj_.width, 1920)
        self.assertEqual(obj_.height, 1080)
