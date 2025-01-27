# Differential Optical Flow Translation
#
# This example shows off using your OpenMV Cam to measure translation
# in the X and Y direction by comparing the current and the previous
# image against each other. Note that only X and Y translation is
# handled - not rotation/scale in this mode.

# To run this demo effectively please mount your OpenMV Cam on a steady
# base and QUICKLY translate it to the left, right, up, and down and
# watch the numbers change. Note that you can see displacement numbers
# up +- half of the hoizontal and vertical resolution.

import sensor, image, time

# NOTE!!! You have to use a small power of 2 resolution when using
# find_displacement(). This is because the algorithm is powered by
# something called phase correlation which does the image comparison
# using FFTs. A non-power of 2 resolution requires padding to a power
# of 2 which reduces the usefulness of the algorithm results. Please
# use a resolution like B64X64 or B64X32 (2x faster).

# Your OpenMV Cam supports power of 2 resolutions of 64x32, 64x64,
# 128x64, and 128x128. If you want a resolution of 32x32 you can create
# it by doing "img.pool(2, 2)" on a 64x64 image.

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # Set pixel format to RGB565 or GRAYSCALE
sensor.set_framesize(sensor.B64X64) # Set frame size to 64x64
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
clock = time.clock()                # Create a clock object to track the FPS.

# Take from the main frame buffer's RAM to allocate a second frame buffer.
extra_fb = sensor.alloc_extra_fb(sensor.width(), sensor.height(), sensor.GRAYSCALE)
extra_fb.replace(sensor.snapshot())

while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    displacement = extra_fb.find_displacement(img)
    extra_fb.replace(img)

    # Offset results are noisy without filtering so we drop some accuracy.
    sub_pixel_x = int(displacement.x_translation() * 5) / 5.0
    sub_pixel_y = int(displacement.y_translation() * 5) / 5.0

    if(displacement.response() > 0.1): # Below 0.1 or so (YMMV) and the results are just noise.
        print("{0:+f}x {1:+f}y {2} {3} FPS".format(sub_pixel_x, sub_pixel_y, displacement.response(), clock.fps()))
    else:
        print(clock.fps())
