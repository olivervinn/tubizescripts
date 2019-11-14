# !/usr/bin/env python3
"""
"""

import os
import sys

from tubize.librarymaker import LibraryMaker
from tubize.app.libraryoptions import LibraryOptions


def main() -> []:
    """
    builds preview and viewing assets for videos in given path
    """
    options = LibraryOptions("Library creation options").parse()
    maker = LibraryMaker(options)
    if os.path.isdir(options.entry_path):
        videos = maker.add_directory(options.entry_path)
        catalog_file = os.path.join(options.entry_path, "catalog.json")
        maker.create_catalog(catalog_file, videos)
        return videos
    else:
        print("Expected directory path!", sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
