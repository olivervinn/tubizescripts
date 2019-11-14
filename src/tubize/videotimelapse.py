"""
Create preview assets for a video file using FFMPEG.

Extracts a thumbnail, animated preview of interesting scenes
and a scrub sprite for video track scrubbing, along with VTT description.

"""
import os
import glob
import logging
import subprocess
import tempfile
import time
from .libraryasset import LibraryAsset
from .videometainfo import VideoMetaInfo
from . import Utils

logger = logging.getLogger(__name__)


def process(options):
    """Process the input arguments either a single file or a directory."""
    # Individual file or directory
    if os.path.isfile(options.entry_path):
        logger.debug(f"is a file")
        matching_files = [options.entry_path]
    else:
        logger.debug(f"is a directory")
        path = os.path.abspath(options.entry_path)
        matching_files = glob.glob(f"{path}/*.mp4")
        print(f"{path}/*.mp4 Found {len(matching_files)}")

    # Join all the files trimming off overlap
    matching_files = glob.glob(f"{path}{os.path.sep}*.mp4")
    temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    for f in matching_files:
        temp.write(f"file '{os.path.basename(f)}'\n", )
    temp.close()
    Utils.ffmpeg(pre_cmd="-ss 00:00:02 -f concat",
                 in_filename=temp.name,
                 args="-c copy joined.MP4")
    os.unlink(temp.name)

    # Hypelapse it
    args = f"-vf setpts=\"0.05*PTS\" -an timelapse.MP4"
    Utils.ffmpeg("joined.MP4", pre_cmd="", args=args, hw=True)
