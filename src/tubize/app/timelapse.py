#!/usr/bin/env python3

import sys
import os
import logging

from tubize.videotimelapse import VideoTimelapse

logger = logging.getLogger(__name__)


class Options(object):
    """Option to control preview creation."""
    def __init__(self):
        """Feature flags to control preview asset creation."""
        self.debug_enabled = False
        self.entry_path = None
        self.ext = None
        self._p = None
        self._parse()

    def _parse(self):
        """Construct argument parser."""
        import argparse
        if not self._p:
            self._p = argparse.ArgumentParser(description='Control options.')
            self._p.add_argument('-i',
                                 '--entry_path',
                                 metavar='entry_path',
                                 type=str,
                                 required=True,
                                 help='input file or directory to process')
            self._p.add_argument('-d',
                                 '--debug',
                                 dest='debug_enabled',
                                 action='store_true',
                                 default=False,
                                 required=False,
                                 help='turn on debug logging')

        args = self._p.parse_args()
        # Map args to this instance
        self.__dict__.update(args.__dict__)
        # Do option command logic
        # Configure logger
        logging.basicConfig(
            level=logging.DEBUG if self.debug_enabled else logging.ERROR)
        if not os.path.exists(self.entry_path):
            print("Invalid path given")
            sys.exit(1)


if __name__ == "__main__":
    timelapser = VideoTimelapse()
    timelapser.process()