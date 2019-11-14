import unittest
import tubize.libraryasset as T_VLA


class LibraryAssetTestCase(unittest.TestCase):
    def test_can_create_asset_from_video(self):
        vla_ = T_VLA.LibraryAsset("./test/examples/test.mp4")
        self.assertNotEqual(vla_, None)
        self.assertEqual(vla_.name, "test")
        self.assertNotEqual(vla_.attributes, None)
