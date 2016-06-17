# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola mod by mikostn
# License: GNU GPLv2, see LICENSE.txt
import logging, os
class rsyncDirectoryReader(object):

    def __init__(self, config):
        """Create an instance of a file reader that just reads a single
        directory on disk.
        """
        self._load_config(config)

    def _load_config(self, config):
        self._path = config.get('directory', 'path')
        self._sync_flag = self._path + '/' + '.sync'
        logging.debug('Media path: {0}'.format(self._path))

    def search_paths(self):
        """Return a list of paths to search for files."""
        return [self._path]

    def is_changed(self):
        """Return true if the file search paths have changed."""
        # For now just return false and assume the path never changes.  In the
        # future it might be interesting to watch for file changes and return
        # true if new files are added/removed from the directory.  This is
        # called in a tight loop of the main program so it needs to be fast and
        # not resource intensive.
        if os.path.isfile(self._sync_flag):
            os.remove(self._sync_flag)
            return True
        else:
            return False

    def idle_message(self):
        """Return a message to display when idle and no files are found."""
        msg = 'No files found'
        logging.warning(msg)
        return msg


def create_file_reader(config):
    """Create new file reader based on reading a directory on disk."""
    return rsyncDirectoryReader(config)
