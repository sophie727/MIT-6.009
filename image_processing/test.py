#!/usr/bin/env python3

import os
import pickle
import hashlib

import lab
import pytest

TEST_DIRECTORY = os.path.dirname(__file__)


def object_hash(x):
    return hashlib.sha512(pickle.dumps(x)).hexdigest()


def compare_images(im1, im2):
    assert set(im1.keys()) == {'height', 'width', 'pixels'}, 'Incorrect keys in dictionary'
    assert im1['height'] == im2['height'], 'Heights must match'
    assert im1['width'] == im2['width'], 'Widths must match'
    assert len(im1['pixels']) == im1['height']*im1['width'], 'Incorrect number of pixels'
    assert all(isinstance(i, int) for i in im1['pixels']), 'Pixels must all be integers'
    assert all(0<=i<=255 for i in im1['pixels']), 'Pixels must all be in the range from [0, 255]'
    pix_incorrect = (None, None)
    for ix, (i, j) in enumerate(zip(im1['pixels'], im2['pixels'])):
        if i != j:
            pix_incorrect = (ix, abs(i-j))
    assert pix_incorrect == (None, None), 'Pixels must match.  Incorrect value at location %s (differs from expected by %s)' % pix_incorrect



def test_load():
    result = lab.load_greyscale_image(os.path.join(TEST_DIRECTORY, 'test_images', 'centered_pixel.png'))
    expected = {
        'height': 11,
        'width': 11,
        'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 255, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    wrong = {
        'height': 1,
        'width': 1,
        'pixels': [0]
    }
    compare_images(result, expected)

def test_inverted_1():
    im = lab.load_greyscale_image(os.path.join(TEST_DIRECTORY, 'test_images', 'centered_pixel.png'))
    result = lab.inverted(im)
    expected = {
        'height': 11,
        'width': 11,
        'pixels': [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 0, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                   255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255],
    }
    compare_images(result, expected)

def test_inverted_2():
    im = {
        'height': 1,
        'width': 4,
        'pixels': [11, 82, 128, 202],
    }
    result = lab.inverted(im)
    expected = {
        'height': 1,
        'width': 4,
        'pixels': [244,173,127,53],
    }
    compare_images(result, expected)

@pytest.mark.parametrize("fname", ['mushroom', 'twocats', 'chess'])
def test_inverted_images(fname):
    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_invert.png' % fname)
    im = lab.load_greyscale_image(inpfile)
    oim = object_hash(im)
    result = lab.inverted(im)
    expected = lab.load_greyscale_image(expfile)
    assert object_hash(im) == oim, 'Be careful not to modify the original image!'
    compare_images(result, expected)


@pytest.mark.parametrize("kernsize", [1, 3, 7])
@pytest.mark.parametrize("fname", ['mushroom', 'twocats', 'chess'])
def test_blurred_images(kernsize, fname):
    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_blur_%02d.png' % (fname, kernsize))
    input_img = lab.load_greyscale_image(inpfile)
    input_hash = object_hash(input_img)
    result = lab.blurred(input_img, kernsize)
    expected = lab.load_greyscale_image(expfile)
    assert object_hash(input_img) == input_hash, "Be careful not to modify the original image!"
    compare_images(result, expected)

def test_blurred_black_image():
    im = {
        'height': 6,
        'width': 5,
        'pixels': [0] * 30,
    }
    result1 = lab.blurred(im, 3)
    result2 = lab.blurred(im, 5)
    compare_images(result1, im)
    compare_images(result2, im)
    
def test_blurred_centered_pixel():
    im = lab.load_greyscale_image(os.path.join(TEST_DIRECTORY, 'test_images', 'centered_pixel.png'))
    result3 = lab.blurred(im, 3)
    result5 = lab.blurred(im, 5)
    expected3 = {
        'height': 11,
        'width': 11,
        'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 28, 28, 28, 0, 0, 0, 0,
                   0, 0, 0, 0, 28, 28, 28, 0, 0, 0, 0,
                   0, 0, 0, 0, 28, 28, 28, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    expected5 = {
        'height': 11,
        'width': 11,
        'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0,
                   0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0,
                   0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0,
                   0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0,
                   0, 0, 0, 10, 10, 10, 10, 10, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    compare_images(result3, expected3)
    compare_images(result5, expected5)

@pytest.mark.parametrize("kernsize", [1, 3, 9])
@pytest.mark.parametrize("fname", ['mushroom', 'twocats', 'chess'])
def test_sharpened_images(kernsize, fname):
    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_sharp_%02d.png' % (fname, kernsize))
    input_img = lab.load_greyscale_image(inpfile)
    input_hash = object_hash(input_img)
    result = lab.sharpened(input_img, kernsize)
    expected = lab.load_greyscale_image(expfile)
    assert object_hash(input_img) == input_hash, "Be careful not to modify the original image!"
    compare_images(result, expected)


@pytest.mark.parametrize("fname", ['mushroom', 'twocats', 'chess'])
def test_edges_images(fname):
    inpfile = os.path.join(TEST_DIRECTORY, 'test_images', '%s.png' % fname)
    expfile = os.path.join(TEST_DIRECTORY, 'test_results', '%s_edges.png' % fname)
    input_img = lab.load_greyscale_image(inpfile)
    input_hash = object_hash(input_img)
    result = lab.edges(input_img)
    expected = lab.load_greyscale_image(expfile)
    assert object_hash(input_img) == input_hash, "Be careful not to modify the original image!"
    compare_images(result, expected)

def test_edges_centered_pixel():
    im = lab.load_greyscale_image(os.path.join(TEST_DIRECTORY, 'test_images', 'centered_pixel.png'))
    result = lab.edges(im)
    expected = {
        'height': 11,
        'width': 11,
        'pixels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 255, 255, 255, 0, 0, 0, 0,
                   0, 0, 0, 0, 255, 0, 255, 0, 0, 0, 0,
                   0, 0, 0, 0, 255, 255, 255, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    compare_images(result, expected)


if __name__ == "__main__":
    import sys
    res = pytest.main(["-k", " or ".join(sys.argv[1:]), "-v", __file__])
