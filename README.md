 gmg\_localfiles, plugin for GNU MediaGoblin
============================================
Plugin for importing files from your filesystem without duplication.

This plugin lets you have all your original files in one folder on your file
system, and it will stop MediaGoblin from copying those files to its own
locations.

It will try to make mediagoblin not touch/ruin your files (no guarantees!), but
it will make a `mg_cache` folder in the directory.

If transcoding is required for videos, they will be made within the `mg_cache` folder. See [the wiki](https://wiki.mediagoblin.org/Configure_MediaGoblin#Disable_transcoding) for an example of how to configure this to minimise the amount of transcoding required.

The plugin has currently been tested on what will become MediaGoblin 0.8.

Installation
------------
Clone `gmg_localfiles` into `mediagoblin/plugins/gmg_localfiles` in your mediagoblin directory.

Configuration
-------------
Example setup in `mediagoblin.ini`:

    [storage:queuestore]
    base_dir = /srv/media/Pictures
    storage_class = gmg_localfiles.storage:PersistentFileStorage

    [storage:publicstore]
    base_dir = /srv/media/Pictures
    base_url = /mgoblin_media/
    storage_class = gmg_localfiles.storage:PersistentFileStorage

    [plugins]
    [[mediagoblin.plugins.gmg_localfiles]]

You will also need to serve the files, so in `paste.ini`:

    [app:publicstore_serve]
    use = egg:Paste#static
    document_root = %(here)s/user_dev/media/public/


Running
-------
From the mediagoblin root folder run `python -m mediagoblin.plugins.gmg_localfiles.import_files`.
