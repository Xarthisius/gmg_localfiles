import os
import pyexiv2

class Metadata(object):
    def __init__(self, path):
        self.path = path
        self.md = pyexiv2.ImageMetadata(path)
        self.dirty = False
        self.read()

    def read(self):
        self.md.read()

    def save(self):
        if self.dirty:
            self.md.write()
            self.dirty = False

    def _get_metadata_item(self, lookup):
        existing_keys = self.md.keys()
        for key in self.lookups[lookup]:
            if key in existing_keys:
                return self.md.get(key)

    @classmethod
    def from_potential_sidecar(self, filepath):
        xmp_filepath = u'{}.xmp'.format(filepath)
        if os.path.exists(xmp_filepath):
            return Metadata(xmp_filepath)
        return Metadata(filepath)
