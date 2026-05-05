import imageio
import numpy as np
from math import sqrt
import sys
import argparse
import os
import cv2


def resize_image(imgobj: np.ndarray, max_width_or_height: int = 1200) -> np.ndarray:
    """ Resize images to max pixels width or height to avoid processing too many pixels as this is a naive implementation of a Fish-Eye algorithm.
    """
    h, w = imgobj.shape[:2]

    if w > max_width_or_height or h > max_width_or_height:
        factor = max(w / max_width_or_height, h / max_width_or_height)
        new_w = int(w / factor)
        new_h = int(h / factor)
        imgobj = cv2.resize(imgobj, (new_w, new_h))
    return imgobj


def get_fish_xn_yn(source_x_norm: float, source_y_norm: float, distortion: float) -> tuple[float, float]:
    """
    Return normalized x, y pixel coordinates in the destination image based on the source coordinates and distortion.
    :param distortion: Amount in which to move pixels from/to center.
    As distortion grows, pixels will be moved further from the center, and vice versa.
    """

    # get x_norm and y_norm distance from normalized center
    # A^2 + B^2 = C^2
    radius = sqrt(source_x_norm**2 + source_y_norm**2)

    denom = 1.0 - (distortion * (radius**2))

    # Fix division by zero and negative denominator (which causes image flipping).
    # If the denominator is zero or negative, it indicates a singularity or
    # an area where the distortion is too strong, causing coordinates to
    # flip or become undefined. By setting it to a small positive epsilon,
    # the resulting source coordinates will be pushed far outside the image bounds,
    # effectively making these pixels transparent or black in the output,
    # which is a common and safe way to handle such cases in naive implementations.
    if denom <= 0:
        # A small positive number to avoid division by zero or negative results.
        denom = 1e-6

    return source_x_norm / denom, source_y_norm / denom


def fish(img: np.ndarray, distortion_coefficient: float) -> np.ndarray:
    """
    Apply Fish-Eye (or reverse fish-eye) effect to an image
    based on the given distortion_coefficient.
    This is a naive implementation that moves pixel by pixel.
    It uses a 'backward mapping' - for each pixel in the destination image - a pixel from the source image is calculated and moved to its new location. A backward mapping is used to ensure that every pixel in the destination image is filled.
    :type img: numpy.ndarray
    :param distortion_coefficient: The amount of distortion to apply.
    :return: numpy.ndarray - the image with applied effect.
    """

    # If input image is only BW or RGB convert it to RGBA
    # So that output 'frame' can be transparent.
    height, width = img.shape[:2]

    if len(img.shape) == 2:  # Grayscale image
        print("Converting B&W photo to RGBA")
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGBA)
    elif len(img.shape) == 3 and img.shape[2] == 3:  # RGB image
        print("Converting RGB photo to RGBA")
        img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
    # If the image is already RGBA or has a different number of channels, it's left as is.

    print("Applying Fish-Eye. Calculating... This may take some time.")
    # prepare array for dst image
    dstimg = np.zeros_like(img)

    # Traverse over pixels
    for row_idx in range(height):
        for col_idx in range(width):

            # normalize x and y to be in interval of [-1, 1]
            x_norm = (2.0 * col_idx - width) / width
            y_norm = (2.0 * row_idx - height) / height

            # new normalized pixel coordinates
            x_distorted_norm, y_distorted_norm = get_fish_xn_yn(
                x_norm, y_norm, distortion_coefficient)

            # convert the normalized distorted xdn and ydn back to image pixels
            source_col = int(((x_distorted_norm + 1.0) * width) / 2.0)
            source_row = int(((y_distorted_norm + 1.0) * height) / 2.0)

            # if new pixel is in bounds copy from source pixel to destination pixel
            if 0 <= source_row < height and 0 <= source_col < width:
                dstimg[row_idx][col_idx] = img[source_row][source_col]

    return dstimg.astype(np.uint8)


def parse_args() -> argparse.Namespace:
    """Parse arguments."""

    parser = argparse.ArgumentParser(
        description="Apply fish-eye effect to images.\nA naive implementation that moves pixels from/to the center based on a given distortion parameter.",
        prog="Cmdline: python fish.py\nLocal web app: streamlit run streamlit_app.py")

    parser.add_argument("-i", "--image", help="path to image file."
                        " If no input is given, the supplied example 'grid.jpg' will be used.",
                        type=str, default="grid.jpg")

    parser.add_argument("-o", "--outpath", help="file path to write output to."
                        " format: <path>.<format(jpg,png,etc..)>",
                        type=str, required=False)

    parser.add_argument("-d", "--distortion",
                        help="The distortion coefficient. How much the move pixels from/to the center."
                        " Recommended values are between -1 and 1."
                        " The bigger the distortion, the further pixels will be moved outwars from the center (fisheye)."
                        " The Smaller the distortion, the closer pixels will be move inwards toward the center (rectilinear)."
                        " For example, to reverse the fisheye effect with --distoration 0.5,"
                        " You can run with --distortion -0.3."
                        " Note that due to double processing the result will be somewhat distorted.",
                        type=float, default=0.5)

    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args()
    try:
        imgobj = imageio.imread(args.image)
        imgobj = resize_image(imgobj)
    except Exception as e:
        print(e)
        sys.exit(1)
    if not args.outpath:
        args.outpath = os.path.splitext(args.image)
        args.outpath = args.outpath[0] + "_fish.png"
    if os.path.exists(args.outpath):
        ans = input(
            args.outpath + " exists. File will be overridden. Continue? y/n: ")
        if ans.lower() != 'y':
            print("exiting")
            sys.exit(0)

    output_img = fish(imgobj, args.distortion)
    imageio.imwrite(args.outpath, output_img, format='png')
