# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
import os
import subprocess
import time

import logging
logging.basicConfig(filename='player.log', level=logging.DEBUG)

# logging.debug('This message should go to the log file')
logging.info('This is fbiOMXplayer')
# logging.warning('And this, too')


class fbiOMXplayer(object):

    def __init__(self, config):
        """Create an instance of a video player that runs omxplayer in the
        background.
        """
        self._process = None
        self._load_config(config)

    def _load_config(self, config):

        self.omxplayer_extensions = config.get('fbi_image_omxplayer', 'video_extensions') \
            .translate(None, ' \t\r\n.') \
            .split(',')

        self.fbi_extensions = config.get('fbi_image_omxplayer', 'image_extensions') \
            .translate(None, ' \t\r\n.') \
            .split(',')
        # Merge extensions for playlist creator
        self._extensions = list(set(self.omxplayer_extensions + self.fbi_extensions))

        self._image_display_time = config.getint(
            'fbi_image_omxplayer', 'image_display_time')

        self._omx_extra_args = config.get('fbi_image_omxplayer', 'omx_extra_args').split()

        self._fbi_extra_args = config.get('fbi_image_omxplayer', 'fbi_extra_args').split()

        self._sound = config.get('fbi_image_omxplayer', 'sound').lower()
        assert self._sound in (
            'hdmi', 'local', 'both'), 'Unknown omxplayer sound configuration value: {0} Expected hdmi, local, or both.'.format(self._sound)

    def supported_extensions(self):
        """Return list of supported file extensions."""
        return self._extensions

    def _print(self, message):
        """Print message to standard output if console output is enabled."""
        logging.debug(message)

    def play(self, media_file, loop=False, vol=0):
        self.stop(3)  # Up to 3 second delay to let the old player stop.

        if media_file.lower().endswith(".jpg") or media_file.lower().endswith(".gif"):
            self._print('Display image: {0}'.format(media_file))
            self._display_image(media_file, loop=False)
        else:
            self._print('Display video: {0}'.format(media_file))
            self._display_video(media_file, loop=False, vol=0)

    def _display_image(self, imagefile, loop=False):
        os.system("killall fbi")
        """View the provided image file, optionally looping it repeatedly."""

        # Assemble list of arguments.
        args = ['fbi']

        args.extend(['--noverbose', '-a'])    # Add sound arguments.
        # args.extend(['--noverbose', '-a', '-d', '/dev/fb0', '-T', '1'])  # Add sound arguments.

        args.extend(['-1', '-t', str(self._image_display_time)])     # display time

        args.extend(self._fbi_extra_args)     # Add extra arguments from config.
        # if loop:
            # args.append('-t ' + str(self._image_display_time))         # Add loop parameter if necessary.
        args.append(imagefile)                # Add movie file path.

        logging.debug(args)

        # Run fbi process and direct standard output to /dev/null.
        shutup = open("/dev/null","w")
        self._process = subprocess.Popen(args,
                                        #  stdout=open(os.devnull, 'wb'),
                                        #  close_fds=True)
                                        stdout=shutup,
                                        stderr=shutup,
                                        shell=True
                                        )
        # time.sleep(self._image_display_time)  # pause
        logging.debug("stop")
        # os.system("killall fbi")
        # self.stop(3)

    def _display_video(self, movie, loop=False, vol=0):
        """Play the provided movied file, optionally looping it repeatedly."""
        # Assemble list of arguments.
        args = ['omxplayer']
        args.extend(['-o', self._sound])  # Add sound arguments.
        args.extend(self._omx_extra_args)     # Add extra arguments from config.
        if vol is not 0:
            args.extend(['--vol', str(vol)])
        if loop:
            args.append('--loop')         # Add loop parameter if necessary.
        args.append(movie)                # Add movie file path.

        logging.debug(args)

        # Run omxplayer process and direct standard output to /dev/null.
        self._process = subprocess.Popen(args,
                                         stdout=open(os.devnull, 'wb'),
                                         close_fds=True)

    def is_playing(self):
        """Return true if the video player is running, false otherwise."""
        if self._process is None:
            return False
        self._process.poll()
        return self._process.returncode is None

    def stop(self, block_timeout_sec=None):
        """
        Stop the video player.  block_timeout_sec is how many seconds to
        block waiting for the player to stop before moving on.
        """
        logging.debug("in stop")
        # Stop the player if it's running.
        if self._process is not None and self._process.returncode is None:
            # There are a couple processes used by omxplayer, so kill both
            # with a pkill command.
            # subprocess.call(['pkill', '-9', 'fbi'])
            # subprocess.call(['killall' 'fbi'])
            subprocess.call(['pkill', '-9', 'omxplayer'])
        # If a blocking timeout was specified, wait up to that amount of time
        # for the process to stop.
        start = time.time()
        while self._process is not None and self._process.returncode is None:
            if (time.time() - start) >= block_timeout_sec:
                break
            time.sleep(0)
        # Let the process be garbage collected.
        self._process = None


def create_player(config):
    """Create new video player based on omxplayer."""
    return fbiOMXplayer(config)
