import imageio
import numpy as np
from math import sqrt
import sys
import argparse
import os
import PIL
import cv2


def resize_image(imgobj, max_width_or_height: int = 1200):
    h, w = imgobj.shape[:2]

    if w > max_width_or_height or h > max_width_or_height:
        factor = max(w / max_width_or_height, h / max_width_or_height)
        new_w = int(w / factor)
        new_h = int(h / factor)
        imgobj = cv2.resize(imgobj, (new_w, new_h))
    return imgobj


# def get_fish_xn_yn(dst_x_nd, dst_y_nd, distortion):
    """
    The input to this function is normalized x, y pixel coordinates from the destination image.
    The function should return normalized x, y pixel coordination in the source image (the x, y pixel that should be copied to the given destination).
    If distortion is > 0, The image should 'buldge' - meaning, for x, y, the source x, y should be closer to the center - i.e. smaller.
    if distortion is < 0, the image should be 'pinched' - i.e for the dst x, y, the source x, y should be further from the center, i.e. larger.
    :param distortion: Amount in which to move pixels from/to center.
    As distortion grows, pixels will be moved further from the center, and vice versa.
    """

    if distortion == 0:
        return dst_x_nd, dst_y_nd

    # get xn and yn distance from normalized center
    radius = r = sqrt(dst_x_nd**2 + dst_y_nd**2)
    if radius == 0:
        return dst_x_nd, dst_y_nd

    R_MAX = sqrt(2.0)
    rn = r / R_MAX

    if distortion > 0:
        scale = r / (1.0 + distortion * r)
        return dst_x_nd * scale / r, dst_y_nd * scale / r
    else:
        denom = 1 - distortion * radius
        if denom == 0:
            return dst_x_nd, dst_y_nd
        return dst_x_nd / denom, dst_y_nd / denom

def get_fish_xn_yn(dst_x_nd, dst_y_nd, distortion):
    """
    Inputs:
      dst_x_nd, dst_y_nd : normalized destination coords (center=0, edges ~= -1..1)
      distortion          : scalar; >0 -> bulge (source coords closer to center),
                                       <0 -> pinch (source coords further from center)
    Returns:
      src_x_nd, src_y_nd : normalized source coords to sample from.
    Notes:
      - This normalizes radius so the corner maps to 1.0 (robust across image shapes).
      - Very large negative distortion can blow the denominator to <=0; we clamp for safety.
    """
    if distortion == 0.0:
        return dst_x_nd, dst_y_nd

    r = sqrt(dst_x_nd * dst_x_nd + dst_y_nd * dst_y_nd)
    if r == 0.0:
        return dst_x_nd, dst_y_nd

    # normalize radius into [0,1] (corners of [-1,1] box -> sqrt(2)/sqrt(2) == 1)
    R_MAX = sqrt(2.0)
    rn = r / R_MAX

    # simple monotonic mapping on normalized radius:
    # rn' = rn / (1 + distortion * rn)
    #   -> distortion > 0  => rn' < rn  (shrink => bulge)
    #   -> distortion < 0  => rn' > rn  (expand => pinch)
    denom = 1.0 + distortion * rn

    # safety clamp to avoid sign flips or division-by-zero for extreme distortion
    if denom <= 1e-6:
        denom = 1e-6

    rns = rn / denom
    rs = rns * R_MAX

    scale = rs / r
    return dst_x_nd * scale, dst_y_nd * scale


def fish(img, distortion_coefficient: float):
    """
    :type img: numpy.ndarray
    :param distortion_coefficient: The amount of distortion to apply.
    :return: numpy.ndarray - the image with applied effect.
    """

    # If input image is only BW or RGB convert it to RGBA
    # So that output 'frame' can be transparent.
    h, w = img.shape[:2]
    if len(img.shape) == 2:
        # Duplicate the one BW channel twice to create Black and White
        # RGB image (For each pixel, the 3 channels have the same value)
        print("Converting B&W photo to RGB")
        bw_channel = np.copy(img)
        img = np.dstack((img, bw_channel))
        img = np.dstack((img, bw_channel))
    if len(img.shape) == 3 and img.shape[2] == 3:
        print("Converting RGB photo to RGBA")
        img = np.dstack((img, np.full((h, w), 255)))

    print("Applying Fish-Eye. Calculating... This may take some time.")
    # prepare array for dst image
    dstimg = np.zeros_like(img)

    # floats for calculations
    w_float, h_float = float(w), float(h)

    # easier calculation if we traverse x, y in dst image
    for y in range(h):

        # normalize x and y to be in interval of [-1, 1]
        ynd = (2.0*y - h_float)/h_float

        for x in range(w):

            # normalize x and y to be in interval of [-1, 1]
            xnd = (2.0*x - w_float)/w_float

            # new normalized pixel coordinates
            xdu, ydu = get_fish_xn_yn(xnd, ynd, distortion_coefficient)

            # map back to pixel space
            xu = int(((xdu + 1) * w) / 2.0)
            yu = int(((ydu + 1) * h) / 2.0)

            if 0 <= xu < w and 0 <= yu < h:
                dstimg[y, x] = img[yu, xu]
            # # convert the normalized distorted xdn and ydn back to image pixels
            # xu, yu = int(((xdu + 1)*w_float)/2), int(((ydu + 1)*h_float)/2)

            # # # if new pixel is in bounds copy from source pixel to destination pixel
            # if 0 <= xu and xu < img.shape[1] and 0 <= yu and yu < img.shape[0]:
            #     dstimg[y][x] = img[yu][xu]

    return dstimg.astype(np.uint8)


def parse_args(args=sys.argv[1:]):
    """Parse arguments."""

    parser = argparse.ArgumentParser(
        description="Apply fish-eye effect to images.",
        prog='python3 fish.py')

    parser.add_argument("-i", "--image", help="path to image file."
                        " If no input is given, the supplied example 'grid.jpg' will be used.",
                        type=str, default="grid.jpg")

    parser.add_argument("-o", "--outpath", help="file path to write output to."
                        " format: <path>.<format(jpg,png,etc..)>",
                        type=str, required=False)

    parser.add_argument("-d", "--distortion",
                        help="The distortion coefficient. How much the move pixels from/to the center."
                        " Recommended values are between -1 and 1."
                        " The bigger the distortion, the further pixels will be moved outward from the center (fisheye)."
                        " The Smaller the distortion, the closer pixels will be move inwards toward the center (rectilinear)."
                        " For example, to reverse the fisheye effect with --distortion 0.5,"
                        " You can run with --distortion -0.3."
                        " Note that due to double processing the result will be somewhat distorted.",
                        type=float, default=0.5)
    parser.add_argument('-wacky', action='store_true', help="Make result a bit wacky when distortion is smaller than -1 or larger than 1.")

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
    # if os.path.exists(args.outpath):
    #     ans = input(
    #         args.outpath + " exists. File will be overridden. Continue? y/n: ")
    #     if ans.lower() != 'y':
    #         print("exiting")
    #         sys.exit(0)

    output_img = fish(imgobj, args.distortion)
    imageio.imwrite(args.outpath, output_img, format='png')
