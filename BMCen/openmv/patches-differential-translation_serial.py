# Image Patches Differential Optical Flow Translation
#
# This example shows off using your OpenMV Cam to measure translation
# in the X and Y direction by comparing the current and the previous
# image against each other. Note that only X and Y translation is
# handled - not rotation/scale in this mode.
#
# However, this examples goes beyond doing optical flow on the whole
# image at once. Instead it breaks up the process by working on groups
# of pixels in the image. This gives you a "new" image of results.
#
# NOTE that surfaces need to have some type of "edge" on them for the
# algorithm to work. A featureless surface produces crazy results.

BLOCK_W = 8 # pow2
BLOCK_H = 8 # pow2

# To run this demo effectively please mount your OpenMV Cam on a steady
# base and SLOWLY translate it to the left, right, up, and down and
# watch the numbers change. Note that you can see displacement numbers
# up +- half of the hoizontal and vertical resolution.

import sensor, image, time
from pyb import USB_VCP, LED
# NOTE!!! You have to use a small power of 2 resolution when using
# find_displacement(). This is because the algorithm is powered by
# something called phase correlation which does the image comparison
# using FFTs. A non-power of 2 resolution requires padding to a power
# of 2 which reduces the usefulness of the algorithm results. Please
# use a resolution like B128X128 or B128X64 (2x faster).

# Transmission Protocol
# SOH-(X)-GS-(Y)-EOT
#

sensor.reset()                         # Reset and initialize the sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # Set pixel format to GRAYSCALE (or RGB565)
sensor.set_framesize(sensor.B64X64)  # Set frame size to 128x128... (or 128x64)...
sensor.skip_frames(time = 2000)        # Wait for settings take effect.
clock = time.clock()                   # Create a clock object to track the FPS.

# Take from the main frame buffer's RAM to allocate a second frame buffer.
# There's a lot more RAM in the frame buffer than in the MicroPython heap.
# However, after doing this you have a lot less RAM for some algorithms...
# So, be aware that it's a lot easier to get out of RAM issues now.
extra_fb = sensor.alloc_extra_fb(sensor.width(), sensor.height(), sensor.GRAYSCALE)
extra_fb.replace(sensor.snapshot())

while(True):
    img = sensor.snapshot() # Take a picture and return the image.
    pixelX = []
    pixelY = []

    for y in range(0, sensor.height(), BLOCK_H):
        for x in range(0, sensor.width(), BLOCK_W):
            displacement = extra_fb.find_displacement(img, roi = (x, y, BLOCK_W, BLOCK_H), template_roi = (x, y, BLOCK_W, BLOCK_H))

            # Below 0.1 or so (YMMV) and the results are just noise.
            if(displacement.response() > 0.2):
                pixelX.append( int(displacement.x_translation()) )
                pixelY.append( int(displacement.y_translation()) )
            else:
                pixelX.append(0)
                pixelY.append(0)

    extra_fb.replace(img)
    print(chr(0x01), end='') # SOH
    print(*pixelX, end='')
    print(chr(0x1D), end='') # GS
    print(*pixelY, end='')
    print(chr(0x04), end='') # EOT
