"""
Convert video format x to MP4/H.264.
"""

import os
import sys
import logging

from .videometainfo import VideoMetaInfo
from .utils import sizeof_fmt, time_fmt, find_files, check_dependencies, call, ffmpeg

logger = logging.getLogger(__name__)


class VideoToMP4:
    """To Mp4"""
    SUPPORTED_EXTENSIONS = ".wmv, .avi, .mkv, .mov, .flv"
    RULES = {
            ".wmv": "-c:v libx264 -crf 19 ",
            ".avi":
            "-vf yadif=1 -c:v h264_nvenc -preset slow -tune film -crf 17",
            ".mkv": "-c copy",
            ".mov": "-vcodec h264 -acodec aac -strict -2 -crf 19 ",
            ".flv": " -r 20 ",
        }

    def process(self, video_file: str):
        """Convert video files to MP4 container format."""

        name = os.path.splitext(video_file)[0]
        ext = os.path.splitext(video_file)[1]
        new_name = f"{name}.mp4"
        if os.path.exists(new_name):
            logger.info(f"Skipping file {new_name} already exists!")
        elif ext not in VideoToMP4.RULES:
            logger.error(f"Skipping unsupported type {ext}!")
        else:
            print(f'Convert {ext} to MP4 {new_name} ... ')
            meta_info = VideoMetaInfo(video_file)
            rule = VideoToMP4.RULES[ext]
            flags = "-movflags +faststart -pix_fmt yuv420p"
            ffmpeg(
                f'-i "{video_file}" {flags} {rule} -metadata date="{meta_info.original_date}" "{new_name}"'
            )

    def file(self, filename: str) -> None:
        logger.debug(f"converting file {filename}")
        self.process(filename)

    def directory(self, path: str, extension: str) -> int:
        files = find_files(path, extension)
        if len(files) < 1:
            print("No matching files found in directory!", file=sys.stderr)
        else:
            for f in files:
                self.file(f)
