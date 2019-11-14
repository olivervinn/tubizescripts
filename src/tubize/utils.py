import os
import sys
from pathlib import Path
import time
import shlex
import subprocess
import logging

log = logging.getLogger(__name__)


def ffmpeg(args: str) -> (str, int):
    """Invoke ffmpeg system command."""
    stout, _, delta = call(
        f'ffmpeg -hwaccel auto -hide_banner -loglevel error -y {args}')
    return stout, delta


def call(args: str, cwd=os.path.curdir) -> (str, str, int):
    """
    Executes a system command returning stdout and stderr
    text plus time to complete the operation.
    """
    try:
        args = shlex.split(args)
        log.debug("Exec -> %s", args)
        start = time.time()
        p_handle = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=cwd)
        std_out, std_err = p_handle.communicate()
        lapsed_time = time.time() - start
        std_out = std_out.decode('utf-8')
        log.debug("Exec Result -> %s", std_out)
        return std_out, std_err, lapsed_time
    except Exception:
        log.critical("unable to invoke !")
        sys.exit(404)


def find_files(path: str, ext: str) -> []:
    """Find files in directory matching pattern."""
    path = os.path.normpath(path)
    ext = str(ext).lower()
    print(f"Searching {path} for *.{ext} ...")
    matching_files = sorted(Path(path).glob(f"**/*.{ext}"))
    for x in matching_files:
        if x.parent.name[0] == "." or x.name[0] == ".":
            log.debug("Ignoring hidden file %s", x)
    matching_files = [
        str(x) for x in matching_files
        if x.parent.name[0] != "." and x.name[0] != "."
    ]
    return matching_files


def check_dependencies(command_map: {}) -> None:
    """Calls each dependency command and exits if any fail"""
    for name, command in command_map.items():
        try:
            _, _, _ = call(f"{command}")
        except FileNotFoundError:
            print(f"Missing dependency {name}")
            sys.exit(404)


def sizeof_fmt(num, suffix='B'):
    """Format bytes into human friendly units."""
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def time_fmt(seconds):
    """Format bytes into human friendly units."""
    hours = int(seconds / 3600)
    minutes = int((seconds - (hours * 3600)) / 60)
    sec = int(seconds - ((hours * 3600) + (minutes * 60)))
    return f"{hours}:{minutes:02d}:{sec:02d}"
