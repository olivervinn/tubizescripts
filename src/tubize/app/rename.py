#!/usr/bin/env python3

import os
import logging
import sys
import json
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

#::for i in **/*\'* ; do mv -v "$i" "${i//\'/}" ; done


def find_files(path: str, substring: str) -> []:
    """Find files in directory matching pattern."""
    print(f"Searching {path} ...")
    #matching_files = sorted(Path(path).rglob(f"**/*{substring}"))
    matching_files = sorted(Path(path).rglob(f"{substring}"))
    print(f"Done {len(matching_files)}")
    return matching_files


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "r":
        path = sys.argv[2]
        pattern = sys.argv[3]
        replace = sys.argv[4]
        matched_files_list = find_files(path, f"*{pattern}*")
        for matched_filename in matched_files_list:
            matched_filename_base = os.path.splitext(matched_filename)[0]
            new_filename = str(matched_filename).replace(pattern, replace)
            new_filename_base = os.path.splitext(new_filename)[0]
            print(f"{matched_filename} --> {new_filename}")
            file_extension = os.path.splitext(matched_filename)[1]
            if file_extension == ".vtt" or file_extension == ".json":
                with open(matched_filename, "rt") as fin:
                    with open(f"{new_filename_base}{file_extension}",
                              "wt") as fout:
                        for line in fin:
                            fout.write(line.replace(pattern, replace))
                logger.debug(f"Updated {matched_filename} contents")
                os.remove(matched_filename)
            else:
                os.rename(matched_filename, new_filename)
            logger.debug(f"Renamed {matched_filename} to {new_filename}")

        catalog_existing = os.path.join(path, "catalog.json")
        with open(catalog_existing, "rt") as catalog:
            with open(catalog_existing + "_", "wt") as fout:
                for line in catalog:
                    fout.write(line.replace(pattern, replace))

        os.remove(catalog_existing)
        os.rename(catalog_existing + "_", catalog_existing)
        logger.debug(f"Updated {catalog_existing} contents")
    if mode == "p":
        source = sys.argv[2]
        preview = source + "/../preview"
        if not os.path.exists(preview):
            logger.debug(f"preveiw folder not found. stopping! {preview}")
            sys.exit(1)
        matched_files_list = find_files(source, "*.mp4")
        matched_files_list_set = set(
            [os.path.basename(x) for x in matched_files_list])
        preview_files = find_files(preview, "*")
        for p in preview_files:
            if os.path.isfile(p):
                name = p.name[:p.name.rfind(".mp4") + 4]
                if name not in matched_files_list_set:
                    os.remove(p)
                    logger.debug(f"Removed {p}")
    else:
        print("prune -- rename.py p [video_source_path]")
        print("rename -- rename.py r [video_root] [match] [replace]")
