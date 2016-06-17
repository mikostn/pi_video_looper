import time
import pygame

import logging

logging.basicConfig(filename='example.log',level=logging.DEBUG)

logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')

try:
    # Initialize pygame and display a blank screen.
    pygame.init()
    pygame.display.init()
    pygame.font.init()
    pygame.mouse.set_visible(False)

    size = (pygame.display.Info().current_w,
            pygame.display.Info().current_h)
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

    font = pygame.font.Font(None, 40)

    pygame.display.set_caption('Photo Booth Pics')
    pygame.mouse.set_visible(False)  # hide the mouse cursor

    screenW, screenH = screen.get_size()

    filename = '/home/pi/Media/lg_g3_smoke_colors-1024x768.jpg'
    img = pygame.image.load(filename)


    transform_x = 600  # 648 #how wide to scale the jpg when replaying
    transfrom_y = 486  # how high to scale the jpg when replaying

    offset_x = 0  # 20  # how far off to left corner to display photos
    offset_y = 0  # 10  # how far off to left corner to display photos

    imgW, imgH = img.get_size()

    logging.debug('imgW: ' + str(imgW))
    logging.debug('imgH: ' + str(imgH))

    ratio = float(imgW)/float(imgH)

    logging.debug('ratio: ' + str(ratio))

    target_width = screenW
    target_height = screenH

    logging.debug('target_width: ' + str(target_width))
    logging.debug('target_height: ' + str(target_height))


    # v_fact and h_fact are the factor by which the original vertical / horizontal
    # image sizes should be multiplied to get the image to your target size.
    h_fact = float(target_width) / float(imgW)
    v_fact = float(target_height) / float(imgH)

    logging.debug('h_fact: ' + str(h_fact))
    logging.debug('v_fact: ' + str(v_fact))


    # you want to resize the image by the same factor in both vertical
    # and horizontal direction, so you need to pick the correct factor from
    # v_fact / h_fact so that the largest (relative to target) of the new height/width
    # equals the target height/width and the smallest is lower than the target.
    # this is the lowest of the two factors
    im_fact = min(v_fact, h_fact)
    logging.debug('im_fact: ' + str(im_fact))

    transform_x = int(imgW * im_fact)
    transfrom_y = int(imgH * im_fact)

    logging.debug('transform_x: ' + str(transform_x))
    logging.debug('transfrom_y: ' + str(transfrom_y))

    offset_x = int((screenW - transform_x) / 2)
    offset_y = int((screenH - transfrom_y) / 2)

    logging.debug('offset_x: ' + str(offset_x))
    logging.debug('offset_y: ' + str(offset_y))

    # txt = "im_fact: " + str(im_fact) + "v_fact: " + str(v_fact) + "h_fact: " + str(h_fact) + "target_height: " + str(target_height) + "target_width: " + str(target_width) + "ratio: " + str(ratio)
    # message = font.render(txt, True, (255, 255, 255), (0,0,0))
    # screen.blit(message, (offset_x, offset_y))
    #
    #
    # time.sleep(150)  # pause

    img = pygame.transform.scale(img, (transform_x, transfrom_y))
    screen.blit(img, (offset_x, offset_y))
    pygame.display.update()
#    pygame.display.flip()  # update the display
    time.sleep(3)  # pause
finally:
    pygame.quit()
