"""
Container for each video asset being processed.
"""

import os
import sys

from .videometainfo import VideoMetaInfo


class LibraryAsset:
    """Collection of files."""
    def __init__(self, filename):
        """Given a path extra meta information."""
        self.filename = os.path.normpath(filename)
        self.attributes = None
        self.acquire_attributes()

    def acquire_attributes(self):
        """Process video to get meta data attributes from stream."""
        self.attributes = VideoMetaInfo(self.filename)

    @property
    def name(self):
        """Get filename without extension."""
        name = os.path.basename(self.filename)
        name = os.path.splitext(name)[0]
        return name

    @property
    def preview_basedir(self):
        """Get basename for preview files."""
        bits = os.path.dirname(self.filename).split(os.path.sep)
        bit_root = bits[-1]
        bits[-1] = ".preview"
        bits.append(bit_root)
        return os.path.sep.join(bits)

    @property
    def preview_basename(self):
        """Get basename for preview files."""
        return os.path.join(self.preview_basedir,
                            os.path.basename(self.filename))

    @property
    def preview_basename_uri(self):
        """Get basename for preview files."""
        return self.preview_basedir_uri + "/" + os.path.basename(self.filename)

    @property
    def webp_filename(self):
        """Get basename for preview files."""
        return self.preview_basename + ".webp"

    @property
    def tile_image_filename(self):
        """Get basename for preview files."""
        return self.preview_basename + ".thumb.jpg"

    @property
    def scrub_image_filename(self):
        """Get basename for preview files."""
        return self.preview_basename + ".jpg"

    @property
    def scrub_image_uri(self):
        """Get uri path for scrub image."""
        return os.path.basename(self.scrub_image_filename)

    @property
    def meta_filename(self):
        """Get meta for file."""
        return self.preview_basename + ".json"

    @property
    def vtt_filename(self):
        """Get meta for file."""
        return self.preview_basename + ".vtt"

    @property
    def group(self):
        """Extract group from filename."""
        return os.path.split(os.path.split(self.filename)[0])[1]

    @property
    def uri(self):
        """Get uri for web access."""
        return f"{self.group}/{self.name}"


if __name__ == "__main__":
    TEST_FILE = sys.argv[1]
    VID = LibraryAsset(TEST_FILE)
    print(VID.basedir)
    print(VID.attributes.print())
