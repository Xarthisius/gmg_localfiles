#from sqlalchemy import event
#
#from mediagoblin.db.models import MediaEntry
#
#@event.listens_for(MediaEntry.collections, 'append')
#def test(target, value, initiator):
#    print "RECV event"
#    import ipdb; ipdb.set_trace()

import re
import os

from mediagoblin import mg_globals as mgg
from mediagoblin.media_types.image import ACCEPTED_EXTENSIONS

from .metadata import Metadata

def media_added_to_collection(collection, media_entry, note):
    m = re.match(r'rating:(\d+)', collection.title)
    if not m:
        return
    rating_number = int(m.group(1))
    set_rating_from_media_entry(media_entry, rating_number)


def set_rating_from_media_entry(media_entry, rating):
    filepath = (mgg.public_store
                ._cachefile_to_original_filepath(
                    media_entry.media_files['original']))
    path = mgg.public_store._resolve_filepath(filepath)
    set_rating(path)


def set_rating(path, rating):
    fn, ext = os.path.splitext(new_filename)
    if ext.lower() not in ACCEPTED_EXTENSIONS:
        return

    md = Metadata.from_potential_sidecar(path)
    md.rating = rating
    md.save()


def get_rating(path):
    fn, ext = os.path.splitext(new_filename)
    if ext.lower() not in ACCEPTED_EXTENSIONS:
        return None

    md = Metadata.from_potential_sidecar(path)
    return md.rating
