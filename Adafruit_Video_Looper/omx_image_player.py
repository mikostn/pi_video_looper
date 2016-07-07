# Copyright 2015 Adafruit Industries.
# Author: Tony DiCola
# License: GNU GPLv2, see LICENSE.txt
from pygame import display, image, time, transform, FULLSCREEN
pygame_time = time
pygame_transform = transform
del time, transform

import os
import subprocess
import time
import logging

# logging.debug('This message should go to the log file')
# logging.info('So should this')
# logging.warning('And this, too')


class OMXImagePlayer(object):

    def __init__(self, config):
        """Create an instance of a video player that runs omxplayer in the
        background.
        """
        self._process = None
        self._load_config(config)

    def _init_image_viewer(self):
        if self._image_viewer == 'fbi':
            return self._display_with_fbi
        # else

        # Init pygame display
        display.init()
        # Hide mouse - unnecessary, since it's already
        # done by looper (?)
        # pygame.mouse.set_visible(False)
        # Prepare screen
        size = (display.Info().current_w,
                display.Info().current_h)
        self._screen = display.set_mode(size, FULLSCREEN)
        self.screenW, self.screenH = self._screen.get_size()
        # set screen to black
        self._blank_screen()
        logging.debug('Init configs')
        logging.debug(display.Info())

        return self._display_with_pygame

    def _load_config(self, config):
        section = 'fbi_image_omxplayer'

        # self._extensions = config.get('omxplayer', 'extensions') \
        #                          .translate(None, ' \t\r\n.') \
        #                          .split(',')

        self.omxplayer_extensions = config.get(section, 'video_extensions') \
            .translate(None, ' \t\r\n.') \
            .split(',')

        self.image_extensions = config.get(section, 'image_extensions') \
            .translate(None, ' \t\r\n.') \
            .split(',')
        # Merge extensions for playlist creator
        self._extensions = list(
            set(self.omxplayer_extensions + self.image_extensions))

        self._omx_extra_args = config.get(section, 'omx_extra_args').split()

        self._sound = config.get(section, 'sound').lower()
        assert self._sound in (
            'hdmi', 'local', 'both'), 'Unknown omxplayer sound configuration value: {0} Expected hdmi, local, or both.'.format(self._sound)

        self._image_viewer = config.get(section, 'image_viewer').lower()
        assert self._image_viewer in (
            'fbi', 'pygame'), 'Unknown image viewer configuration value: {0} Expected fbi (for FrameBuffer Image viewer), or pygame.'.format(self._sound)

        # Set selected image viewer
        self._display_image = self._init_image_viewer()

        self._image_display_time = config.getint(section, 'image_display_time')

        self._fbi_extra_args = config.get(section, 'fbi_extra_args').split()

    def supported_extensions(self):
        """Return list of supported file extensions."""
        return self._extensions

    def _print(self, message):
        """Print message to standard output if console output is enabled."""
        logging.debug(message)

    def _blank_screen(self):
        """Render a blank screen filled with the background color."""
        self._screen.fill((0, 0, 0))
        display.update()

    def scale_image(self, img):
        imgW, imgH = img.get_size()

        ratio = float(imgW) / float(imgH)

        # v_fact and h_fact are the factor by which the original vertical / horizontal
        # image sizes should be multiplied to get the image to your target
        # size.
        h_fact = float(self.screenW) / float(imgW)
        v_fact = float(self.screenH) / float(imgH)

        # you want to resize the image by the same factor in both vertical
        # and horizontal direction, so you need to pick the correct factor from
        # v_fact / h_fact so that the largest (relative to target) of the new height/width
        # equals the target height/width and the smallest is lower than the target.
        # this is the lowest of the two factors
        im_fact = min(v_fact, h_fact)

        displayedW = int(imgW * im_fact)
        displayedH = int(imgH * im_fact)

        offset_x = int((self.screenW - displayedW) / 2)
        offset_y = int((self.screenH - displayedH) / 2)

        # pygame.transform.smoothscale()

        return [pygame_transform.scale(img, (displayedW, displayedH)), offset_x, offset_y]

    def play(self, media_file, loop=False, vol=0):
        t1 = time.time()
        self.stop(3)  # Up to 3 second delay to let the old player stop.
        logging.debug('Time player stoped: {0}'.format(time.time() - t1))

        if media_file.lower().endswith(".jpg") or media_file.lower().endswith(".gif"):
            self._print('Display image: {0}'.format(media_file))
            self._display_image(media_file)
            logging.debug('Time image done: {0}'.format(time.time() - t1))
        else:
            self._print('Display video: {0}'.format(media_file))
            self._display_video(media_file, loop=False, vol=0)
            logging.debug(
                'Time video displayed: {0}'.format(time.time() - t1))

    def _display_with_pygame(self, imagefile):
        try:
            t1 = time.time()
            # Clear the screen
            self._blank_screen()
            logging.debug('Time: {0}'.format(time.time() - t1))
            img = image.load(imagefile)
#            img = pygame.image.load(imagefile).convert()
            logging.debug(time.time() - t1)
            img, offset_x, offset_y = self.scale_image(img)
            logging.debug(time.time() - t1)
            self._screen.blit(img, (offset_x, offset_y))
            logging.debug(time.time() - t1)

            # update the display
            display.update()
            logging.debug('Time image displayed: {0}'.format(time.time() - t1))
            ''' fadeIn? from black '''
            # pygame.display.flip()
            # pause
            pygame_time.wait(self._image_display_time * 1000)

            # time.sleep(self._image_display_time)
            ''' fadeOut? to black '''

        except Exception, e:
            logging.error('Error: ' + str(e))

    def _display_with_fbi(self, imagefile):
        os.system("killall fbi")
        """View the provided image file, optionally looping it repeatedly."""

        # Assemble list of arguments.
        args = ['fbi']
        args.extend(['--noverbose', '-a'])
        # args.extend(['--noverbose', '-a', '-d', '/dev/fb0', '-T', '1'])  #

        # Add extra arguments from config.
        args.extend(self._fbi_extra_args)
        if loop:
            # Add loop parameter if necessary.
            args.append('-t ' + str(self._image_display_time))
        else:
            # display time
            args.extend(['-1', '-t', str(self._image_display_time)])

        args.append(imagefile)                # Add movie file path.

        logging.debug(args)

        # Run fbi process and direct standard output to /dev/null.
        shutup = open("/dev/null", "w")
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
        # Add extra arguments from config.
        args.extend(self._omx_extra_args)
        if vol is not 0:
            args.extend(['--vol', str(vol)])
        if loop:
            args.append('--loop')         # Add loop parameter if necessary.
        args.append(movie)                # Add movie file path.
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
        """Stop the video player.  block_timeout_sec is how many seconds to
        block waiting for the player to stop before moving on.
        """
        t1 = time.time()
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
        # Clear the screen
        self._blank_screen()


def create_player(config):
    """Create new video player based on omxplayer."""
    return OMXImagePlayer(config)
