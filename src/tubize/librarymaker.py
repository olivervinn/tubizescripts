"""
Create preview assets for a video file using FFMPEG.

Extracts a thumbnail, animated preview of interesting scenes
and a scrub sprite for video track scrubbing, along with VTT description.
"""
import os
import collections
import logging
import tempfile
import time
import math
import numpy as np
import imutils
import cv2

from .options import Options
from .libraryasset import LibraryAsset
from .librarycatalog import LibraryCatalog
from .utils import sizeof_fmt, time_fmt, find_files, check_dependencies, call, ffmpeg

log = logging.getLogger(__name__)


class LibraryMaker:
    """Coordinates the aggregation of videos and creation of preview artifacts"""
    def __init__(self, options: Options):
        self.options = options
        self.preview_width = self.options.preview_width
        external_deps = {
            "ffmpeg": "ffmpeg -version",
            "mediainfo": "mediainfo --version",
            "img2webp": "img2webp -version"
        }
        check_dependencies(external_deps)

    def _step(self, cur_state, count: int) -> bool:
        """Seek to next scene change factor to get desired frame count."""
        limit_min, limit_max, limit_restrict = 60, 200, 230
        cur_state.steps.append(cur_state.step)
        cur_state.values.append(count)
        if count > limit_min and count < limit_restrict:
            return False
        else:
            if count > limit_max:
                cur_state.step += 5
            else:
                cur_state.step -= 50 if cur_state.step > 60 else 10
            if cur_state.step <= 0:
                return False
            return True

    def _time_code(self, duration: int) -> str:
        """Create timecode for a given duration in milliseconds."""
        milliseconds = int((duration % 1000) / 100)
        seconds = math.floor((duration / 1000) % 60)
        minutes = math.floor((duration / (1000 * 60)) % 60)
        hours = math.floor((duration / (1000 * 60 * 60)) % 24)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

    def _get_scenes(self, asset: LibraryAsset, step: int, tmp) -> ([], int):
        """Extract scenes from video file into `tmp` directory."""
        step = 0.001 * float(step)
        print(f"    - Find scenes @ {step:.3f}", end=' ... ', flush=True)
        _, took = ffmpeg(
            f'-ss 00:00:04 -i "{asset.filename}" -filter_complex  \
             "yadif=1,select=\'gt(scene,{step:.3f})\',setpts=N/(25*TB),scale={self.preview_width}:-1"  \
             -vsync vfr "{tmp}{os.path.sep}%03d.png"'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      )
        files = os.listdir(tmp)
        count = len(files)
        print(f"Found {count} in {took:.2f}s")
        return files, count

    def _uniform_image_check(self, output_filename: str) -> int:
        """
        Detect image features, determining if flat.
        True if flat (feature-less) otherwise False
        """
        l_array = np.array([0, 0, 0])
        u_array = np.array([50, 50, 50])
        # pylint: disable=no-member
        image = cv2.imdecode(np.fromfile(output_filename, dtype=np.uint8),
                             cv2.IMREAD_UNCHANGED)
        shape_mask = cv2.inRange(image, l_array, u_array)
        contour_map = cv2.findContours(shape_mask.copy(), cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        # pylint: enable=no-member
        contours = imutils.grab_contours(contour_map)
        contours_count = len(contours)
        log.debug("Found %s black shapes", contours_count)
        return contours_count < 20

    def generate_tile_thumbnail_file(self, files: [], output_filename):
        """Creates a mosaic of input files."""
        count = len(files)
        dim = 5
        while count < dim * dim:
            dim -= 1
        log.debug("tile - %s %dx%s - %d", output_filename, dim, dim, count)
        gw = int(350 / dim)
        gh = int(200 / dim)
        files = ' '.join('"{0}"'.format(f) for f in files[:dim*dim])
        call(
            f'montage {files} -geometry {gw}x{gh}+0+0 -tile {dim}x{dim} -gravity center -background black "{output_filename}"'
        )

    def generate_thumbnail_file(self, asset: LibraryAsset) -> None:
        """Create a poster image from the first 2sec video mark."""
        output_filename = asset.tile_image_filename
        offset = 1
        while True:
            ffmpeg(
                f'-i "{asset.filename}" -ss 00:{int(offset / 60):02d}:{offset % 60:02d} -vframes 1 -q:v 5 \
                    -vf "scale={self.preview_width*2}:-1" "{output_filename}"'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    )
            if offset > 500 and not os.path.exists(output_filename):
                print("Unable to find thumbnail!")
                break
            elif self._uniform_image_check(output_filename):
                offset += 4
            else:
                size = sizeof_fmt(os.path.getsize(output_filename))
                print(f"    Thumbnail size {size}")
                break

    def generate_vtt_file(self, asset: LibraryAsset) -> None:
        """ Create a VTT description for the scrub image sprite."""
        name = asset.scrub_image_uri
        attributes = asset.attributes
        width = self.preview_width
        height = int((width / attributes.width) * attributes.height)
        interval, snaps, rows = attributes.calc_scrub_image_properties(width)
        total_time, x_off, y_off, i = 0, 0, 0, 1
        with open(asset.vtt_filename, "w") as vtt_file:
            vtt_file.write("WEBVTT\n\n")
            while i < snaps * rows:
                vtt_file.write(f"{i}\n")
                vtt_file.write(f"{self._time_code(total_time)} ")
                vtt_file.write(
                    f"--> {self._time_code(total_time + interval * 1000)}\n")
                vtt_file.write(
                    f"{name}#xywh={x_off},{y_off},{width},{height}\n")
                vtt_file.write(f"\n")
                total_time += (interval * 1000)
                x_off += width
                i += 1
                if i % snaps == 0:
                    x_off = 0
                    y_off += height

    def generate_video_scrub_file(self, asset: LibraryAsset):
        """Generate a XxY jpeg tile for scrubbing video timeline."""
        width = self.preview_width
        attributes = asset.attributes
        _, cols, rows = attributes.calc_scrub_image_properties(width)
        ffmpeg(f'-ss 00:00:04 -i "{asset.filename}" -frames 1 -q:v 2 -vf \
             "yadif=1,select=\'not(mod(n\\,{attributes.fps * 2}))\',scale={width}:-1,tile={cols}x{rows}" \
             "{asset.scrub_image_filename}"'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        )
        size = sizeof_fmt(os.path.getsize(asset.scrub_image_filename))
        print(f"    Timeline size {size} for {cols}x{rows}")

    def generate_animated_webp_file(self, asset):
        """Generate an animated preview for input video."""
        output_filename = asset.webp_filename
        if os.path.exists(output_filename + ".ignore"):
            return False, 0
        state = collections.namedtuple('State', ['values', 'steps', 'step'])
        state.values = []
        state.steps = []
        state.step = self.options.default_scene_detection
        start_time = time.time()
        count = 0
        attributes = asset.attributes
        while not os.path.exists(output_filename + ".ignore"):
            with tempfile.TemporaryDirectory(prefix="preview") as tmp_basename:
                files, count = self._get_scenes(asset, state.step,
                                                tmp_basename)
                if self._step(state, count):
                    continue
                elif count > 0:
                    attributes.preview_delay = 210
                    attributes.step_v_values = list(
                        map(list, zip(state.steps, state.values)))
                    files = " ".join(files)
                    call(
                        f'img2webp -min_size -lossy -d {attributes.preview_delay} {files} -o "{os.path.abspath(output_filename)}"',
                        cwd=tmp_basename)
                    size = os.path.getsize(output_filename)
                    print(f"    Webp size: {sizeof_fmt(size)} from {count}")
                    break
                else:
                    print(f"    Webp creation failed!")
                    with open(output_filename + ".ignore", "w") as ignore:
                        ignore.write("Ignore")
                    break
        end_time = time.time()
        log.debug("Time to find %2fs", end_time - start_time)
        return count > 0, state.step

    def generate_meta_file(self, asset: LibraryAsset) -> None:
        """Create the preview meta file."""
        log.debug("Write meta file %s", asset.meta_filename)
        with open(asset.meta_filename, "w") as meta_file:
            meta_file.write(asset.attributes.to_json())

    @classmethod
    def is_hidden_folder(cls, file_path):
        """Check name matches hidden format e.g. .<name>"""
        folders = os.path.normcase(file_path).split(os.path.sep)
        for f in folders:
            if f.startswith("."):
                log.debug("Ignore hidden %s", file_path)
                return True
        return False

    def add_video(self, filename: str) -> LibraryAsset:
        """Create the preview artifacts for the input video."""
        asset = LibraryAsset(filename)
        os.makedirs(asset.preview_basedir, exist_ok=True)
        options = self.options
        if options.thumb:
            if not os.path.exists(asset.tile_image_filename) or options.force:
                self.generate_thumbnail_file(asset)
                asset.updated = True
        if options.preview:
            if not os.path.exists(asset.webp_filename) or options.force:
                self.generate_animated_webp_file(asset)
                asset.updated = True
        if options.scrub:
            if not (os.path.exists(asset.scrub_image_filename)
                    and os.path.exists(asset.vtt_filename)) or options.force:
                self.generate_video_scrub_file(asset)
                self.generate_vtt_file(asset)
                asset.updated = True
        if not os.path.exists(asset.meta_filename):
            self.generate_meta_file(asset)
            asset.updated = True
        return asset

    def add_directory(self, path: str) -> []:
        """
        Process directory `path` adding mp4 files to the in
        memory library catalog.
        """
        print("Finding videos in directory ... ")
        matching_files = find_files(path, "mp4")
        meta_infos = []
        for filename in matching_files:
            if not LibraryMaker.is_hidden_folder(filename):
                m_info = self.add_video(filename)
                meta_infos.append(m_info)
        return meta_infos

    def create_catalog(self, output_filename: str, assets: []):
        """
        Create a catalog file `output_filename` from the
        asset objects `assets`.
        """
        any_updated = False
        catalog = LibraryCatalog()
        for asset in assets:
            if not catalog.append(asset):
                any_updated = any_updated or asset.updated
                continue

        catalog.update_group_thumbnails(self.generate_tile_thumbnail_file,
                                        output_filename, any_updated)
        if any_updated:
            if not os.path.exists(output_filename):
                print("Building catalog ... ")
                data = catalog.to_json()
                with open(output_filename, "w") as cat_file:
                    cat_file.write(data)
                print(f"Wrote catalog {output_filename}")
                print(
                    f"Total Data Size: {sizeof_fmt(catalog.total_file_size)}")
                print(f"Total Duration: {time_fmt(catalog.total_duration)}")
            else:
                print(f"No updates!")