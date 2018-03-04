from typing import Tuple

import numpy as np
import cv2


def get_inverted_color(color: Tuple[int]) -> Tuple[int]:
    """
    returns a contrasting color with the provided color. This is used for drawing. Color can be a 1,2,3 or 4 channel
    image.
    :param color: Color that will be converted.
    :return: Converted color.
    """
    color_ch = []
    for i in range(len(color)):
        if i == 3:  # alpha channel
            color_ch.append( 255 )
            break
        if color[i] > 128:
            color_ch.append(0)
        else:
            color_ch.append(255)
    return tuple(color_ch)


def combine_image_and_overlay(image: np.ndarray, overlay: np.ndarray):
    """
    combines a 4 channel alpha overlay image with a source image wicht might be grayscaled or 3 channeled. It returns
    an image that has 3 channels with the size of the 'image'
    :param image: image that should include the overlay
    :param overlay: overlay with alpha channel
    :return: 3 channel image with overlay
    """
    if len(overlay.shape) != 3 or overlay.shape[2] != 4:
        raise ValueError("Overlay size does not have the correct dimensions; should have 4 channels")

    if len(image.shape) != 3:
        # gray image, convert to bgr
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # rescale overlay to fit in image
    image_height, image_width, _ = image.shape
    overlay_height, overlay_width, _ = overlay.shape
    if image_height < overlay_height:
        overlay = overlay[:image_height, :, :]
    if image_width < overlay_width:
        overlay = overlay[:, :image_width, :]

    overlay_height, overlay_width, _ = overlay.shape

    # now copy overlay weighted to image
    mask = overlay[:, :, 3] / 255.0  # between 0-1
    mask_inverted = 1.0 - mask

    for i in range(3):
        image[:overlay_height,:overlay_width,i] = np.array(image[:overlay_height, :overlay_width, i] * mask_inverted + overlay[:, :, i] * mask,
                     dtype=np.uint8)
    return image


def enlarge_alpha_image(image, min_width, min_height, min_channel=4):
    """
    Adds padding to the image (0,0,0,0) to mnake the image as least as large as new_width and min_height. This function
    is used to enlarge the image before adding new objects to the overlay.
    :param image: image to enlarge
    :param min_width: the minimal required width
    :param min_height:  the minimal required height
    :return:
    """
    if len(image.shape) == 2:
        raise TypeError("Should provide function with an image of at least 2 channels.")
    image_height, image_width, image_ch = image.shape
    if image_height >= min_height and image_width >= min_width and image_ch >=min_channel:
        return image

    pad_x = 0
    pad_y = 0
    pad_ch = 0
    if image_height < min_height:
        pad_y = int(min_height - image_height)
    if image_width < min_width:
        pad_x = int(min_width - image_width)
    if image_ch < min_channel:
        pad_ch = int(min_channel - image_ch)

    return np.pad(image, ((0, pad_y), (0, pad_x), (0, pad_ch)), 'constant')
