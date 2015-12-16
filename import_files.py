#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# GMG localfiles plugin -- local file import
# Copyright (C) 2012 Odin Hørthe Omdal
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import codecs
import os
import sys
import uuid

# This is here early because of a race
import mediagoblin
from mediagoblin.app import MediaGoblinApp
from mediagoblin import mg_globals


if __name__ == "__main__":
    mg_dir = os.path.dirname(mediagoblin.__path__[0])
    if mg_dir == "":
        mg_dir = "./"
    if os.path.exists(mg_dir + "/mediagoblin_local.ini"):
        config_file = mg_dir + "/mediagoblin_local.ini"
    elif os.path.exists(mg_dir + "/mediagoblin.ini"):
        config_file = mg_dir + "/mediagoblin.ini"
    else:
        raise Exception("Couldn't find mediagoblin.ini")

    mg_app = MediaGoblinApp(config_file, setup_celery=True)

    from mediagoblin.init.celery import setup_celery_app
    setup_celery_app(
        mg_globals.app_config,
        mg_globals.global_config,
        force_celery_always_eager=True)

from mediagoblin.db.base import Session
from mediagoblin.media_types import FileTypeNotSupported
from mediagoblin.media_types import get_media_type_and_manager
from mediagoblin.submit.lib import run_process_media
from mediagoblin.tools.text import convert_to_tag_list_of_dicts
from mediagoblin.user_pages.lib import add_media_to_collection

import logging
mediagoblin.media_types._log.setLevel(logging.INFO)


class MockMedia():

    filename = ""
    name = ""
    stream = None

    def __init__(self, filename, stream):
        self.filename = filename
        self.name = os.path.abspath(filename)
        self.stream = stream

    def read(self, *args, **kwargs):
        return self.stream.read(*args, **kwargs)


class ImportCommand(object):
    help = 'Find new photos and add to database'

    def __init__(self, db, base_dir, **kwargs):
        self.db = db
        self.base_dir = base_dir

    def handle(self, filename):
        entry_id = None
        filepath = os.path.join(self.base_dir, filename)
        try:
            entry_id = self.import_file(MockMedia(
                filename=filename.decode('utf8'), stream=open(filepath, 'r')))
        except Exception as exc:
            print(u"[imp] Exception while importing "
                  "file '{0}': {1}.".format(filepath, repr(exc)))

        if entry_id is not None:
            self.add_to_collection(u'roll:fido', entry_id)

    def add_to_collection(self, collection_title, entry_id):
        collection = (self.db.Collection.query
                      .filter_by(actor=1, title=collection_title)
                      .first())
        if not collection:
            collection = self.db.Collection()
            collection.title = collection_title
            collection.actor = 1
            collection.type = "myfancytype"
            collection.generate_slug()
            collection.save()
            Session.commit()
        entry = self.db.MediaEntry.query.filter_by(id=entry_id).first()
        add_media_to_collection(collection, entry, commit=False)
        try:
            Session.commit()
        except Exception as exc:
            print (u"Could add media to collection {}: {}"
                   "".format(collection_title, exc))
            Session.rollback()

    def import_file(self, media):
        try:
            media_type, media_manager = (
                get_media_type_and_manager(media.filename))
        except FileTypeNotSupported:
            print u"File type not supported: {0}".format(media.filename)
            return

        fname = unicode(os.path.basename(media.name))

        if self.db.MediaEntry.query.filter_by(title=fname).first():
            print("Skipping {0} - file exists".format(fname))
            return
        entry = self.db.MediaEntry()
        entry.media_type = unicode(media_type)
        entry.title = unicode(os.path.basename(media.name))

        entry.actor = 1
        entry.uploader = 1
        # Process the user's folksonomy "tags"
        entry.tags = convert_to_tag_list_of_dicts("")
        # Generate a slug from the title
        entry.generate_slug()

        task_id = unicode(uuid.uuid4())
        entry.queued_media_file = media.filename.split("/")
        entry.queued_task_id = task_id

        try:
            entry.save()
            entry_id = entry.id
            run_process_media(entry)
            Session.commit()
            return entry_id
        except Exception:
            Session.rollback()
            raise


if __name__ == "__main__":
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    ic = ImportCommand(
        mg_app.db,
        mg_globals.global_config['storage:publicstore']['base_dir'])
    ic.handle()

    print
    print "Import finished"
