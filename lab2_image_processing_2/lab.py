#!/usr/bin/env python3

"""
6.101 Lab 2:
Image Processing 2
"""

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image

# Functions from image processing lab 1 for greyscale images (lines 13-267)

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
    INPUT: image (dict), row (int), col (int), boundary_behavior (str)
    OUTPUT: the pixel of the image at the given row and column
    boundary_behavior can be "zero", "extend", or "wrap"
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

# edge effects

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

# Image processing lab 2

# Helper functions

def split_image_into_three(image):
    """
    Input a color image and returns a list of three separate
    greyscale images (one for each color component).
    """
    images = []
    for _ in range(3):
        im = {
            "height": image["height"],
            "width": image["width"],
            "pixels": [],
        }
        images.append(im)

    for (r,g,b) in image["pixels"]:
        images[0]["pixels"].append(r)
        images[1]["pixels"].append(g)
        images[2]["pixels"].append(b)

    return images

def combine_three_into_one(images):
    """
    Input a list of three separate greyscale images (one for each
    color component) and returns a color image.
    """
    result = {
        "height": images[0]["height"],
        "width": images[0]["width"],
        "pixels": []
    }
    for i in range(len(images[0]["pixels"])):
        a,b,c = images[0]["pixels"][i], images[1]["pixels"][i], images[2]["pixels"][i]
        result["pixels"].append((a,b,c))
    return result

# VARIOUS FILTERS

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def color_filter(image):
        images = split_image_into_three(image)
        result = []
        for im in images:
            result.append(filt(im))
        return combine_three_into_one(result)
    return color_filter

def make_blur_filter(kernel_size):
    """
    Given a kernel_size (int), returns a function that takes in a greyscale image
    and returns a blurred image, blurred to the extent of the kernel_size.
    """
    def greyscale_blurred_filter(image):
        return blurred(image, kernel_size)
    return greyscale_blurred_filter

def make_sharpen_filter(kernel_size):
    """
    Given a kernel_size (int), returns a function that takes in a greyscale image
    and returns a sharpened image, sharpened to the extent of the kernel_size.
    """
    def greyscale_sharpened_filter(image):
        return sharpened(image, kernel_size)
    return greyscale_sharpened_filter

def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def cascade(image):
        result = image
        for f in filters:
            result = f(result)
        return result
    return cascade

# SEAM CARVING

# Main Seam Carving Implementation

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image. Returns a new image.
    """
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": image["pixels"].copy(),
    }
    for _ in range(ncols):
        grey = greyscale_image_from_color_image(result)
        energy = compute_energy(grey)
        cem = cumulative_energy_map(energy)
        min_seam = minimum_energy_seam(cem)
        result = image_without_seam(result, min_seam)
    return result

# Optional Helper Functions for Seam Carving

def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [],
    }
    for (r,g,b) in image["pixels"]:
        v = round(.299*r + .587*g + .114*b)
        result["pixels"].append(v)
    return result

def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)

def get_smallest_neighbor(cem, row, col):
    """
    Given an energy map (dict), a row (int), and a column (int), returns the
    index and value of the smallest nearest upstairs neighbor to the pixel at 
    the given row and column, where "upstairs neighbors" are defined as the up 
    to three pixels directly above or diagonally above the pixel in question.
    """
    if row == 0:
        return (None, 0)

    neighbor_index = get_index(cem, row - 1, col)
    neighbor = get_pixel(cem, row - 1, col)
    if col < cem["width"] - 1:
        right_neighbor = get_pixel(cem, row - 1, col + 1)
        if right_neighbor < neighbor:
            neighbor_index = get_index(cem, row - 1, col + 1)
            neighbor = right_neighbor
    if col > 0:
        left_neighbor = get_pixel(cem, row - 1, col - 1)
        if left_neighbor <= neighbor:
            neighbor_index = get_index(cem, row - 1, col - 1)
            neighbor = left_neighbor

    return (neighbor_index, neighbor)

def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    cem = {
        "height": energy["height"],
        "width": energy["width"],
        "pixels": [0] * (energy["height"] * energy["width"]),
    }
    for row in range(energy["height"]):
        for col in range(energy["width"]):
            (_, neighbor) = get_smallest_neighbor(cem, row, col)
            val = get_pixel(energy, row, col) + neighbor
            set_pixel(cem, row, col, val)
    return cem

def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    seam = [0] * cem["height"]

    index = get_index(cem, cem["height"] - 1, 0)
    bottom_row_min = get_pixel(cem, cem["height"] - 1, 0)
    for i in range(cem["width"]):
        val = get_pixel(cem, cem["height"] - 1, i)
        if val < bottom_row_min:
            index = get_index(cem, cem["height"] - 1, i)
            bottom_row_min = val
    seam[cem["height"] - 1] = index

    for row in range(cem["height"] - 1, 0, -1):
        col = index - row * cem["width"]
        index, val = get_smallest_neighbor(cem, row, col)
        seam[row - 1] = index
    return seam

def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    result = {
        "height": image["height"],
        "width": image["width"] - 1,
        "pixels": image["pixels"].copy(),
    }
    for i in reversed(seam):
        result["pixels"].pop(i)
    return result

# Custom image function
def ripple(image, ripple_step, ripple_width):
    """
    INPUT: image (dict), ripple_step (int), ripple_width (int)
    OUTPUT: image with ripple effect (dict)
    The ripple effect will be implemented by offsetting every row horizontally
    by some amount, where the ripple offset of each row is increased sinusoidally
    until ripple_width is reached, at which point it becomes offset in the opposite
    direction, and so forth. More specifically, the offset starts at 0, then it
    becomes ripple_width * sin(ripple_step), then it becomes ripple_width * 
    sin(2 * ripple_step), and so forth.
    """
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [0] * (image["height"] * image["width"])
    }
    for row in range(image["height"]):
        offset = round(ripple_width * math.sin(ripple_step * row))
        for col in range(image["width"]):
            color = get_pixel(image, row, col + offset, "extend")
            set_pixel(result, row, col, color)

    return result


# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_color_image(image, filename, mode="PNG"):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
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
    by the 'mode' parameter.
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

    pass
