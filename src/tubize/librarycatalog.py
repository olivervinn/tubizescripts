import os
import json

from .libraryasset import LibraryAsset


class LibraryCatalog(dict):
    """Simple group of video assets under same root directory."""
    def __init__(self):
        """Poor wrapper around list."""
        super().__init__()
        self.groups = {}
        self.total_file_size = 0
        self.total_duration = 0

    @classmethod
    def is_hidden_folder(cls, file_path):
        """Check name matches hidden format e.g. _<name>"""
        ignore_path = "\\_" in file_path or "/_" in file_path
        ignore_name = " " in file_path
        return ignore_name or ignore_path

    def append(self, asset: LibraryAsset):
        """Add video asset to grouping."""
        hide = self.is_hidden_folder(asset.filename)
        if not hide:
            group = asset.group
            if group not in self.groups:
                self.groups[group] = {'assets': [], 'time': 0}
            group = self.groups[group]
            group['assets'].append(asset)
            group['thumbnail'] = ''
            group['time'] += asset.attributes.duration
            self.total_file_size += os.path.getsize(asset.filename)
            self.total_duration += asset.attributes.duration
        return not hide

    def update_group_thumbnails(self, tile_function, output_filename):
        """Create group thumbnail."""
        for name, g in self.groups.items():
            files = [f.tile_image_filename for f in g['assets']]
            g['thumbnail'] = f"{output_filename}.{name}.jpeg"
            tile_function(files, g['thumbnail'])

    def to_json(self):
        """Emit a JSON description of structure."""
        def serialize(obj):
            """Serialize data."""
            if isinstance(obj, LibraryAsset):
                return {
                    '_': obj.uri,
                    'title': obj.attributes.title,
                    'description': obj.attributes.description,
                    'tags': obj.attributes.keywords,
                    'duration': obj.attributes.duration
                }
            return obj.__dict__

        return json.dumps(self.groups, default=serialize, indent=2)
