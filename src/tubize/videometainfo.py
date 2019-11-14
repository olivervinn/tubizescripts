"""
Extracts video file meta data from files.
"""
import os
import sys
import math
import json
import logging
from .utils import time_fmt, call

log = logging.getLogger(__name__)


class VideoMetaInfo(object):
    """Container for video properties."""
    def __init__(self, filename):
        """Uninitialized instance of container."""
        self.fps = 1
        self.frames = 0
        self.height = 0
        self.width = 0
        self.aspect_ratio = 0
        self.original_date = None
        self.filename = str(filename)
        self._get_video_info()

    def _get_video_info(self):
        """Extract video properties."""
        stdout, _, _ = call(
            f'ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate,nb_frames,height,width,display_aspect_ratio \
             -of default=nokey=1:noprint_wrappers=1 "{self.filename}"')
        try:
            s = stdout.split('\n')
            self.width = int(s[0])
            self.height = int(s[1])
            self.aspect_ratio = s[2]
            self.fps = int(int(s[3].split("/")[0]) / int(s[3].split("/")[1]))
            self.frames = int(s[4])
        except (ValueError, IndexError):
            log.error("parse failed inspecting response '%s'", s)
        log.debug("attributes: %sx%s@%d", self.width, self.height, self.fps)
        stdout, _, _ = call(f'mediainfo "{self.filename}"')
        if "Recorded date" in stdout:
            s = stdout.split("Recorded date")[1]
            self.original_date = s.strip().split()[1]
        log.info("recorded date: %s", self.original_date)

    @property
    def name(self) -> str:
        """Get name from filename."""
        name = os.path.basename(self.filename)
        name = os.path.splitext(name)[0]
        return name

    @property
    def keywords(self) -> []:
        """Get keywords from filename."""
        name = self.name.lower()
        name = name.replace('-', '_')
        words = name.split('_')
        words = [
            i for i in words if len(i) > 2 and i not in ["the", "day", "out"]
        ]
        return words

    @property
    def title(self) -> str:
        """Get title from keywords."""
        max_length = 30
        title = " ".join(str(i).capitalize() for i in self.keywords)
        title = title[0:max_length] + \
            ".." if len(title) > (max_length - 2) else title
        return title

    @property
    def description(self) -> str:
        """Get description from keywords."""
        description = " ".join(self.keywords)
        description = description.capitalize()
        return description

    @property
    def duration(self) -> int:
        """Get duration in seconds."""
        return int(self.frames / self.fps)

    def print(self):
        """Print meta properties."""
        print(f"- File: {self.filename}...")
        print(f"    Time: {time_fmt(self.duration)}")
        print(f"    FPS: {self.fps}")
        print(f"    Frames: {self.frames}")
        print(f"    Aspect: {self.aspect_ratio}")
        print(f"    Original date: {self.original_date}")

    def to_json(self) -> str:
        """Create json meta format."""
        meta = {
            "title": self.title,
            "duration": self.duration,
            "originaldate": self.original_date,
            "description": self.description,
            "tags": self.keywords
        }
        return json.dumps(meta, indent=2)

    def calc_scrub_image_properties(self, width) -> (int, int, int):
        """Calculate snapshot interval, column and row count."""
        # Bypass shot clips
        if int(self.frames / self.fps) < 2:
            frame_interval, col_cnt, row_cnt = int(self.frames / 2), 1, 1
        else:
            # % of max jpeg supported for this image width
            max_supported = int((65500 / width) * 0.95)
            # Scale proportional to duration
            col_cnt = max_supported
            if self.duration < 40 * 60:
                col_cnt = max_supported * 0.80
            elif self.duration < 20 * 60:
                col_cnt = max_supported * 0.50
            elif self.duration < 10 * 60:
                col_cnt = max_supported * 0.25
            # Get inter-frames for this many snapshots
            frame_interval = int(self.frames / col_cnt)
            col_cnt = int(col_cnt)
            # Hack: Every second
            frame_interval = 1
            dim = math.sqrt(self.duration / frame_interval)
            dim = math.ceil(dim)
            col_cnt = dim
            row_cnt = dim
        # Capture
        self.scrub_scene_count = col_cnt
        self.scrub_interval = frame_interval
        log.debug("desired snapshots = %ss, %s cols, %s rows", self.duration,
                  self.scrub_interval, col_cnt)
        return frame_interval, col_cnt, row_cnt
