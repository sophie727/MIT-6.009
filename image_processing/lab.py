#!/usr/bin/env python3

"""
6.101 Lab 1:
Image Processing
"""

import math

from PIL import Image

# NO ADDITIONAL IMPORTS ALLOWED!

def get_index(image, row, col):
    """
    INPUT: image (dict), row (int), col (int), boundary_behavior (None or str)
    OUTPUT: the index of the pixel of the image at the given row and column
    """
    height = image["height"]
    width = image["width"]
    if (row < 0) or (col < 0) or (row >= height) or (col >= width):
        # note that the first row is row 0 and first column is column 0
        return None
    else:
        return row * width + col

def get_pixel(image, row, col, boundary_behavior=None):
    """
    INPUT: image (dict), row (int), col (int)
    OUTPUT: the pixel of the image at the given row and column
    """
    height = image["height"]
    width = image["width"]

    if (row < 0) or (col < 0) or (row >= height) or (col >= width):
        # note that the first row is row 0 and first column is column 0
        if boundary_behavior == "zero":
            return 0
        elif boundary_behavior == "extend":
            return get_pixel_extend(image, row, col)
        elif boundary_behavior == "wrap":
            return get_pixel_wrap(image, row, col)
        else:
            return None
    else:
        return image["pixels"][get_index(image, row, col)]

def set_pixel(image, row, col, color):
    """
    INPUT: image (dict), row (int), col (int)
    OUTPUT: None
    Sets the pixel at the given row and column to the given color.
    """
    image["pixels"][get_index(image, row, col)] = color

def apply_per_pixel(image, func):
    """
    INPUT: image (dict) and func (function)
    OUTPUT: a new image (dict) such that every pixel has been acted on by func
    """
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": image["pixels"].copy(),
    }
    for row in range(image["height"]):
        for col in range(image["width"]):
            color = get_pixel(image, row, col)
            new_color = func(color)
            set_pixel(result, row, col, new_color)
    return result

def inverted(image):
    """
    INPUT: image (dict)
    OUTPUT: an inverted version of the image, where the color at each pixel
    is changed to 255 - color.
    """
    return apply_per_pixel(image, lambda color: 255 - color)

# edge effect
def get_pixel_extend(image, row, col):
    """
    INPUT: image (dict), row (int), col (int)
    OUTPUT: the pixel at the given row and column of the image, where
    we treat out of bound row and col values by extending the image.
    
    In other words, if one were to draw out the image and then extend it
    infinitely in all directions, this function returns the pixel at the
    given row and column in this imaginary image.
    """
    crop_row = min(max(0, row),image["height"]-1)
    crop_col = min(max(0, col),image["width"]-1)
    return image["pixels"][get_index(image,crop_row,crop_col)]

def get_pixel_wrap(image, row, col):
    """
    INPUT: image (dict), row (int), col (int)
    OUTPUT: the pixel at the given row and column of the image, where
    we treat out of bound row and col values by wrapping the image.
    
    In other words, if one were to tile an infinite plane with this
    image, this function returns the pixel on that imaginary image.
    """
    return image["pixels"][get_index(image, row%image["height"], col%image["width"])]


# HELPER FUNCTIONS

def apply_kernel(image, row, col, kernel, boundary_behavior):
    """
    Compute the application of a kernel (dict) on the pixel in the position
    at the row and column given.
    """
    result = 0
    for kern_row in range(kernel["height"]):
        for kern_col in range(kernel["width"]):
            kern_radius = int((kernel["height"] - 1)/2)
            kern_element = kernel["pixels"][get_index(kernel,kern_row,kern_col)]

            img_row = row - kern_radius + kern_row
            img_col = col - kern_radius + kern_col
            img_element = get_pixel(image, img_row, img_col, boundary_behavior)

            result += kern_element * img_element
    return result

def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will be one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    For consistency's sake, we will represent the kernel similarly to the way we
    represent images: as a dictionary containing information on the height, width,
    and a Python list ("values") of the values in the kernel, stored in row-major order
    (listing the top row left-to-right, then the next row, and so on).
    """
    if boundary_behavior not in ("zero", "extend", "wrap"):
        return None
    else:
        result = {
            "height": image["height"],
            "width": image["width"],
            "pixels": [],
        }
        for row in range(image["height"]):
            for col in range(image["width"]):
                val = apply_kernel(image, row, col, kernel, boundary_behavior)
                result["pixels"].append(val)
        return result

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    return apply_per_pixel(image, lambda color: round(min(max(0, color),255)))

# FILTERS

def blurred(image, kernel_size):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    n = kernel_size
    kernel = {
        "height": n,
        "width": n,
        "pixels": [1/(n * n)] * (n * n)
    }

    # then compute the correlation of the input image with that kernel
    result = correlate(image, kernel, "extend")

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.

    return round_and_clip_image(result)

def sharpened(image, n):
    """
    Return a new image representing the result of sharpening the image (where
    the given n is the kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # This function will be implemented by doing a single correlation.
    kernel = {
        "height": n,
        "width": n,
        "pixels": [-1/(n * n)] * (n * n)
    }
    center_index = int((n-1)/2)
    kernel["pixels"][get_index(kernel, center_index, center_index)] += 2

    return round_and_clip_image(correlate(image, kernel, "extend"))

def edges(image):
    """
    Return a new image representing the result of emphasizing the edges in
    the image via the Sobel operator.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """

    kernel1 = {
        "height": 3,
        "width": 3,
        "pixels": [-1, -2, -1,
                    0,  0,  0,
                    1,  2,  1,]
    }

    kernel2 = {
        "height": 3,
        "width": 3,
        "pixels": [-1, 0, 1,
                   -2, 0, 2,
                   -1, 0, 1,]
    }

    result1 = correlate(image, kernel1, "extend")
    result2 = correlate(image, kernel2, "extend")

    final_result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [0] * (image["height"] * image["width"])
    }

    for i in range(image["height"] * image["width"]):
        radicand = result1["pixels"][i]**2 + result2["pixels"][i]**2
        final_result["pixels"][i] = math.sqrt(radicand)

    return round_and_clip_image(final_result)

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the "mode" parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.

    # bluegill = load_greyscale_image("test_images/bluegill.png")
    # save_greyscale_image(inverted(bluegill), "inverted_bluegill.png")

    # im = {
    #     "height": 1,
    #     "width": 4,
    #     "pixels": [11, 82, 128, 202],
    # }

    # expected = {
    #     "height": 1,
    #     "width": 4,
    #     "pixels": [244,173,127,53],
    # }
    # test_result = inverted(im)
    # print(test_result)
    # print(expected)

    # pig_kernel = {
    #     "height": 13,
    #     "width": 13,
    #     "pixels": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #                1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
    # }
    # pig = load_greyscale_image("test_images/pigbird.png")
    # save_greyscale_image(correlate(pig, pig_kernel, "wrap"), "wrap_pigbird.png")

    # cat = load_greyscale_image("test_images/cat.png")
    # save_greyscale_image(blurred(cat, 13), "blurred_cat.png")

    # python = load_greyscale_image("test_images/python.png")
    # save_greyscale_image(sharpened(python, 11), "sharpened_python.png")

    construct = load_greyscale_image("test_images/construct.png")
    save_greyscale_image(edges(construct), "edges_construct.png")
