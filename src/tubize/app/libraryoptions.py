import os
import sys
import argparse
import logging

from tubize.options import Options


class LibraryOptions(Options):
    """Option to control preview creation."""
    def build(self):
        """Construct argument parser."""
        self.parser.add_argument('-i',
                                 '--entry-path',
                                 metavar='entry_path',
                                 type=str,
                                 required=True,
                                 help='input file or directory')
        self.parser.add_argument('-scene',
                                 '--default-scene-detection',
                                 metavar='default_scene_detection',
                                 type=int,
                                 default=400,
                                 required=False,
                                 help='initial detection value (400=40.0%)')
        self.parser.add_argument('-w',
                                 '--preview-width',
                                 metavar='preview_width',
                                 type=int,
                                 default=160,
                                 required=False,
                                 help='video preview tile pixel width')
        self.parser.add_argument('-force',
                                 '--force',
                                 dest='force',
                                 default=False,
                                 required=False,
                                 action='store_true',
                                 help='force create even if file exists')
        self.parser.add_argument('-nt',
                                 '--no-thumbnail',
                                 dest='thumb',
                                 default=True,
                                 required=False,
                                 action='store_false',
                                 help='don\'t create tile thumbnail')
        self.parser.add_argument('-na',
                                 '--no-animated-preview',
                                 dest='preview',
                                 default=True,
                                 required=False,
                                 action='store_false',
                                 help='don\'t create webp animated preview')
        self.parser.add_argument('-ns',
                                 '--no-video-timeline-scrub',
                                 dest='scrub',
                                 default=True,
                                 required=False,
                                 action='store_false',
                                 help='don\'t create video timeline tile')
