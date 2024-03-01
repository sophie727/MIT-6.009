"""
6.101 Lab 0:
Audio Processing
"""

import wave
import struct
# No Additional Imports Allowed!


def backwards(sound):
    """
    Given a sound, returns the reversed version of the sound without changing the input sound.
    """
    rate = sound['rate']
    samples = sound['samples']
    reversedSamples = []
    for i in range(len(samples)):
        reversedSamples.append(samples[len(samples)-i-1])

    reversedSound = {
        'rate': rate,
        'samples': reversedSamples
    }

    return reversedSound


def mix(sound1, sound2, p):
    """
    Given two sounds and a mixing ratio, mixes the sounds and returns it without editing the inputs. Mixing two sounds consists of averaging corresponding samples in the two sounds, with the samples being weighted according to the mixing ratio.
    """

    rate1 = sound1['rate']
    samples1 = sound1['samples']
    rate2 = sound2['rate']
    samples2 = sound2['samples']

    if rate1 != rate2:
        return None
    else:
        mixedSamples = []

        if len(samples1) > len(samples2):
            # This piece of code switches samples1 and samples2, so with the rest of the mixing, we can treat samples1 as shorter than samples2.

            [samples1, samples2] = [samples2, samples1]

            p = 1 - p

        for i in range(len(samples1)):
            mixedSamples.append(samples1[i]*p + samples2[i]*(1-p))
        for i in range(len(samples1), len(samples2)):
            mixedSamples.append(samples2[i]*(1-p))

        mixedSound = {
            'rate': rate1,
            'samples': mixedSamples
        }

        return mixedSound

def convolve(sound, kernel):
    """
    Given a sound and a kernel, we return the convolution of the sound and kernel. Here, convolution is defined as convolving the list of sound samples with the kernel.
    """
    # Essentially, convolution is just polynomial multiplication.
    samples = sound['samples']

    convolutedSamples = [0]*(len(samples) + len(kernel) - 1)

    for i in range(len(samples) + len(kernel) - 1):
        # continuing with the polynomial multiplication concept, this is calculating the coefficient of x^i.
        c = 0
        for j in range(len(kernel)):
            if (i >= j) and (i-j < len(samples)):
                c += kernel[j]*samples[i-j]

        convolutedSamples[i] = c

    convolutedSound = {
        'rate': sound['rate'],
        'samples': convolutedSamples
    }    

    return convolutedSound



def echo(sound, num_echoes, delay, scale):
    """
    Given a sound, return a sound that is an echoed version of the original sound. Specifically, the number of echoes, delay between echoes, and scale of each echo is also inputted.
    """
    sample_delay = round(delay * sound['rate'])

    samples = sound['samples']

    echoedSamples = [0] * (len(samples) + num_echoes * sample_delay)

    echoScale = 1
    for echo in range(num_echoes + 1):
        for i in range(len(samples)):
            echoedSamples[i + echo * sample_delay] += samples[i] * echoScale

        echoScale *= scale

    echoedSound = {
        'rate': sound['rate'],
        'samples': echoedSamples
    }

    return echoedSound

    # echo using convolution. Takes a long time
    # echoKernel = [0] * (sample_delay * num_echoes + 1)
    # echoScale = 1
    # for i in range(num_echoes):
    #     echoKernel[sample_delay*i] = echoScale
    #     echoScale *= scale
    # echoKernel[-1] = echoScale
    # return convolve(sound, echoKernel)


def pan(sound):
    """
    Given a sound, returns a version of the sound that pans from left to right. That is, all the sound initially comes from the left, and then the audio from the left decreases linearly and the audio from the right increases linearly until all the audio comes from the right.
    """
    left = sound['left']
    right = sound['right']
    N = len(left)

    panLeft = [0] * N
    panRight = [0] * N

    for i in range(N):
        panLeft[i] = left[i] * (1-(i)/(N-1))
        panRight[i] = right[i] * (i)/(N-1)

    panSound = {
        'rate': sound['rate'],
        'left': panLeft,
        'right': panRight
    }

    return panSound


def remove_vocals(sound):
    """
    Given a sound, returns a version of the sound with vocals removed. This is done by subtracting the right samples from the left samples, as vocals are usually recorded in mono, so the vocals usually get subtracted out through this process.
    """
    left = sound['left']
    right = sound['right']

    removedVocalsSamples = [0] * len(left)

    for i in range(len(left)):
        removedVocalsSamples[i] = left[i] - right[i]
    
    removedVocalsSound = {
        'rate': sound['rate'],
        'samples': removedVocalsSamples
    }

    return removedVocalsSound


def bass_boost_kernel(n_val, scale=0):
    """
    Construct a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ n_val

    Then we scale that piece up and add a copy of the original signal back in.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    kernel = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    for i in range(n_val):
        kernel = convolve(kernel, base["samples"])
    kernel = kernel["samples"]

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel) // 2] += 1

    return kernel


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = file.readframes(1)
            if chan == 2:
                left.append(struct.unpack("<h", frame[:2])[0])
                right.append(struct.unpack("<h", frame[2:])[0])
            else:
                datum = struct.unpack("<h", frame)[0]
                left.append(datum)
                right.append(datum)

        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = file.readframes(1)
            if chan == 2:
                left = struct.unpack("<h", frame[:2])[0]
                right = struct.unpack("<h", frame[2:])[0]
                samples.append((left + right) / 2)
            else:
                datum = struct.unpack("<h", frame)[0]
                samples.append(datum)

        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for left, right in zip(sound["left"], sound["right"]):
            left = int(max(-1, min(1, left)) * (2**15 - 1))
            right = int(max(-1, min(1, right)) * (2**15 - 1))
            out.append(left)
            out.append(right)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)


    # hello = load_wav("sounds/hello.wav")

    # write_wav(backwards(hello), 'hello_reversed.wav')



    # mystery = load_wav("sounds/mystery.wav")
    # write_wav(backwards(mystery), 'mystery_reversed.wav')

    # synth = load_wav("sounds/synth.wav")
    # water = load_wav("sounds/water.wav")
    # write_wav(mix(synth, water, 0.2), 'synth_water_mixed.wav')

    # iceAndChilli = load_wav("sounds/ice_and_chilli.wav")
    # write_wav(convolve(iceAndChilli, bass_boost_kernel(1000, 1.5)), 'ice_and_chilli_convoluted.wav')

    # chord = load_wav("sounds/chord.wav")
    # write_wav(echo(chord, 5, 0.3, 0.6), 'chord_echo.wav')

    # car = load_wav("sounds/car.wav", stereo=True)
    # write_wav(pan(car), "car_pan.wav")

    mountain = load_wav("sounds/lookout_mountain.wav", stereo=True)
    write_wav(remove_vocals(mountain), "lookout_mountain_removed_vocals.wav")

    s = {
    'rate': 8,
    'left': [1, 2, 3, 4, 5],
    'right': [5, 5, 5, 5, 5]
    }
    print(remove_vocals(s))