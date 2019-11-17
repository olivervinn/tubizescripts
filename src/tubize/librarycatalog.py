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

    def append(self, asset: LibraryAsset):
        """Add video asset to grouping."""
        group = asset.group
        if group not in self.groups:
            self.groups[group] = {'assets': [], 'time': 0}
        group = self.groups[group]
        group['assets'].append(asset)

    def update_group_thumbnails(self, tile_function, output_filename, updates):
        """Create group thumbnail."""
        for name, g in self.groups.items():
            fname = f'{os.path.dirname(output_filename)}/{name}.jpg'
            if not os.path.exists(fname) or updates:
                files = [f.tile_image_filename for f in g['assets']]
                tile_function(files, fname)
                g['thumbnail'] = fname

    def to_json(self):
        """Emit a JSON description of structure."""
        for group in self.groups.values():
            for asset in group['assets']:
                group['time'] += asset.attributes.duration
                self.total_file_size += os.path.getsize(asset.filename)
                self.total_duration += asset.attributes.duration

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
