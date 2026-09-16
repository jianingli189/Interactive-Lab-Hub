import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.D5) 
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

while True:
    # --------------------------------------------------
# SKY CLOCK
# --------------------------------------------------

# Screen size:
# width = 240
# height = 135


def lerp(a, b, t):
    """Linear interpolation between two numbers."""
    return int(a + (b - a) * t)


def lerp_color(color1, color2, t):
    """Smoothly interpolate between two RGB colors."""
    return (
        lerp(color1[0], color2[0], t),
        lerp(color1[1], color2[1], t),
        lerp(color1[2], color2[2], t)
    )


def get_sky_color(hour):
    """
    Smooth sky color transition:
    00:00 -> midnight
    06:00 -> morning
    12:00 -> noon
    18:00 -> sunset
    24:00 -> midnight
    """

    midnight = (10, 25, 70)
    morning  = (170, 210, 225)
    noon     = (45, 170, 245)
    sunset   = (235, 95, 65)

    if 0 <= hour < 6:
        t = hour / 6
        return lerp_color(midnight, morning, t)

    elif 6 <= hour < 12:
        t = (hour - 6) / 6
        return lerp_color(morning, noon, t)

    elif 12 <= hour < 18:
        t = (hour - 12) / 6
        return lerp_color(noon, sunset, t)

    else:
        t = (hour - 18) / 6
        return lerp_color(sunset, midnight, t)


def get_sun_color(hour):
    """
    Sun color:
    06:00 -> pale orange
    12:00 -> bright yellow-white
    18:00 -> vivid red
    """

    sunrise = (255, 180, 110)
    noon_sun = (255, 250, 190)
    sunset_sun = (255, 70, 45)

    if 6 <= hour <= 12:
        t = (hour - 6) / 6
        return lerp_color(sunrise, noon_sun, t)

    else:
        t = (hour - 12) / 6
        return lerp_color(noon_sun, sunset_sun, t)


def draw_sun(draw, hour):
    """
    Sun travels in an arc from 06:00 to 18:00.
    """

    if hour < 6 or hour >= 18:
        return

    # Progress through daytime:
    # 06:00 = 0.0
    # 12:00 = 0.5
    # 18:00 = 1.0
    progress = (hour - 6) / 12

    # Horizontal movement
    x = 15 + progress * 210

    # Parabolic vertical movement
    # At sunrise/sunset: y is near/below bottom edge
    # At noon: y is near top
    y = 140 - 120 * (4 * progress * (1 - progress))

    radius = 14

    color = get_sun_color(hour)

    draw.ellipse(
        (
            int(x - radius),
            int(y - radius),
            int(x + radius),
            int(y + radius)
        ),
        fill=color
    )


def get_night_visibility(hour):
    """
    Moon/stars:
    18:00-19:00 -> fade in
    19:00-05:00 -> fully visible
    05:00-06:00 -> fade out
    """

    if 18 <= hour < 19:
        return hour - 18

    elif hour >= 19 or hour < 5:
        return 1.0

    elif 5 <= hour < 6:
        return 6 - hour

    else:
        return 0.0


def draw_moon(draw, sky_color, visibility):

    if visibility <= 0:
        return

    moon_color = (255, 245, 180)

    # Blend moon with sky to create fade effect
    visible_color = lerp_color(
        sky_color,
        moon_color,
        visibility
    )

    # Main moon circle
    draw.ellipse(
        (105, 28, 137, 60),
        fill=visible_color
    )

    # Cover part of the circle with sky color
    # to create crescent shape
    draw.ellipse(
        (116, 22, 143, 55),
        fill=sky_color
    )


def draw_stars(draw, sky_color, visibility):

    if visibility <= 0:
        return

    star_color = (255, 245, 180)

    visible_color = lerp_color(
        sky_color,
        star_color,
        visibility
    )

    stars = [
        (45, 30),
        (75, 65),
        (165, 35),
        (195, 70)
    ]

    radius = 3

    for sx, sy in stars:
        draw.ellipse(
            (
                sx - radius,
                sy - radius,
                sx + radius,
                sy + radius
            ),
            fill=visible_color
        )


while True:

    # ----------------------------------------------
    # 1. GET CURRENT TIME
    # ----------------------------------------------

    now = time.localtime()

    # Decimal hour:
    # e.g. 6:30 -> 6.5
    hour = (
        now.tm_hour
        + now.tm_min / 60
        + now.tm_sec / 3600
    )


    # ----------------------------------------------
    # 2. SKY
    # ----------------------------------------------

    sky_color = get_sky_color(hour)

    draw.rectangle(
        (0, 0, width, height),
        fill=sky_color
    )


    # ----------------------------------------------
    # 3. SUN
    # ----------------------------------------------

    draw_sun(draw, hour)


    # ----------------------------------------------
    # 4. MOON + STARS
    # ----------------------------------------------

    visibility = get_night_visibility(hour)

    draw_moon(
        draw,
        sky_color,
        visibility
    )

    draw_stars(
        draw,
        sky_color,
        visibility
    )


    # ----------------------------------------------
    # 5. DISPLAY
    # ----------------------------------------------

    disp.image(image, rotation)

    time.sleep(1)

