import os
import sys
import argparse
import logging


class Options(object):
    """Option to control preview creation."""
    def __init__(self, description: str):
        """Argument properties."""
        self.loglevel = False
        self.parser = argparse.ArgumentParser(description=description)
        self._build()

    def _build(self):
        """Construct argument parser."""
        self.parser.add_argument('-d',
                                 '--debug',
                                 dest='loglevel',
                                 action='store_const',
                                 default=logging.WARNING,
                                 const=logging.DEBUG,
                                 required=False,
                                 help='turn on debug logging')
        self.parser.add_argument('-v',
                                 '--verbose',
                                 dest='loglevel',
                                 action='store_const',
                                 const=logging.INFO,
                                 required=False,
                                 help='turn on debug logging')
        self.build()

    def build(self):
        """Sub class adds."""
        pass

    def parse(self):
        """Extract options from the command line."""
        args = self.parser.parse_args()
        self.__dict__.update(args.__dict__)
        logging.basicConfig(level=args.loglevel)
        if not os.path.exists(self.entry_path):
            raise ValueError("input is not a valid path")
        return self
