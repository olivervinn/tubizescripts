#!/usr/bin/env python3

import os
import sys
import argparse
import logging

logger = logging.getLogger(__name__)

from tubize.options import Options
from tubize.videotomp4 import VideoToMP4


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
        self.parser.add_argument(
            '-x',
            '--ext',
            metavar='ext',
            type=str,
            required=False,
            default="avi",
            help=f'supported extension {VideoToMP4.SUPPORTED_EXTENSIONS}')


if __name__ == "__main__":
    converter = VideoToMP4()
    OPTIONS = ConvertOptions(
        "Converts input videos to mp4/h264 format").parse()
    if os.path.isfile(OPTIONS.entry_path):
        converter.file(OPTIONS.entry_path)
    else:
        converter.directory(OPTIONS.entry_path, OPTIONS.ext)
