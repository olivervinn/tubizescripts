#!/usr/bin/env python3

import sys
import os
import logging

from tubize.videojoiner import VideoJoiner
from tubize.options import Options

logger = logging.getLogger(__name__)


class ConvertOptions(Options):
    """Option to control preview creation."""
    def build(self):
        """Construct argument parser."""
        self.parser.add_argument(
            '-i',
            '--entry_path',
            metavar='entry_path',
            type=str,
            required=True,
            help='input file to process or directory to find files to process')


if __name__ == "__main__":
    converter = VideoJoiner()
    OPTIONS = ConvertOptions("Join input avi videos").parse()
    if os.path.isfile(OPTIONS.entry_path):
        converter.file(OPTIONS.entry_path)
    else:
        converter.directory(OPTIONS.entry_path, OPTIONS.ext)
