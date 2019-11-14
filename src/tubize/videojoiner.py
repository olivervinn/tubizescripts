"""
Script to join AVI files into a single AVI file.

Joins multiple AVI files, sorted on filename and video timecode. If
timecode indicates change in day then a new AVI segment output is created.
"""

import os
import sys
import glob
import tempfile
import logging

from .videometainfo import VideoMetaInfo
from . import Utils

log = logging.getLogger(__name__)


class AVIJoiner:
    def create_segment(self, file_group, out_basename):
        """Concat a collection of video files in a group into one video file."""
        with tempfile.TemporaryFile(mode="w", delete=False) as tmp_file_handle:
            for group_item_filename in file_group:
                tmp_file_handle.write(f"file '{group_item_filename}'\n")
            tmp_file_handle.close()
            out = f'{out_basename}.avi'
            print(f"Creating {out} - from {len(file_group)} files")
            Utils.call(f'ffmpeg -v error -y -f concat -safe 0 -i {tmp_file_handle.name} -c copy "{out}"')
            os.remove(tmp_file_handle.name)

    def create_sorted_input(self, target_directory):
        """Get list of files matching pattern and sort them for concat."""
        avi_files = glob.glob(os.path.abspath(target_directory) + "/*.avi")
        if not avi_files:
            print(f'No matching files found {target_directory:s}')
            sys.exit(99)
        print(f'Found files {len(avi_files)}')
        avi_files.sort()
        log.debug(avi_files)
        return avi_files

    def process_files(self, directory, prefix=""):
        """Extract video info and group files for segment concaternation."""
        segment_id = 0
        aspect = ""
        old_aspect = None
        old_date = None
        group = []
        files = self.create_sorted_input(directory)
        for filename in files:
            m_info = VideoMetaInfo(filename)
            # Recorded date
            date = m_info.original_date
            if not date:
                date = old_date
                log.warning("No meta date found. Reusing previous.")
            log.info("Video Meta Date: %s - %s", filename, date)
            if not old_date:
                old_date = date
            # Detect aspect ratio change
            aspect = m_info.aspect_ratio
            print(f"{filename} - {date} - {aspect}")
            if (old_aspect and aspect != old_aspect) or (old_date != date):
                self.create_segment(group, f'{prefix}_{old_date}_{segment_id}')
                group = []
                segment_id += 1
            # Add to group
            old_aspect = aspect
            old_date = date
            group.append(filename)

        # Process any in final group
        if group:
            self.create_segment(group, f'{prefix}_{old_date}_{segment_id}')
