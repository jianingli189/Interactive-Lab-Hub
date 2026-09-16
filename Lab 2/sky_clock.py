import math
import time
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789


# --------------------------------------------------
# DISPLAY SETUP
# --------------------------------------------------

cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

BAUDRATE = 64000000

spi = board.SPI()

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

# Landscape screen: 240 x 135
height = disp.width
width = disp.height

image = Image.new("RGB", (width, height))
rotation = 90

draw = ImageDraw.Draw(image)

# Clear screen
draw.rectangle(
    (0, 0, width, height),
    fill=(0, 0, 0)
)

disp.image(image, rotation)

# Turn on backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True


# --------------------------------------------------
# DEMO MODE
# --------------------------------------------------

DEMO_MODE = True

# 24 real seconds = 24 simulated hours
DEMO_SECONDS_PER_DAY = 24

# Demo starts at 06:00
DEMO_START_HOUR = 6.0

demo_start_time = time.time()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

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


# --------------------------------------------------
# SKY
# --------------------------------------------------

def get_sky_color(hour):

    midnight = (10, 25, 70)
    morning = (170, 210, 225)
    noon = (45, 170, 245)
    sunset = (235, 95, 65)

    if 0 <= hour < 6:

        t = hour / 6

        return lerp_color(
            midnight,
            morning,
            t
        )

    elif 6 <= hour < 12:

        t = (hour - 6) / 6

        return lerp_color(
            morning,
            noon,
            t
        )

    elif 12 <= hour < 18:

        t = (hour - 12) / 6

        return lerp_color(
            noon,
            sunset,
            t
        )

    else:

        t = (hour - 18) / 6

        return lerp_color(
            sunset,
            midnight,
            t
        )


# --------------------------------------------------
# SUN
# --------------------------------------------------

def get_sun_color(hour):

    sunrise = (255, 180, 110)
    noon_sun = (255, 250, 190)
    sunset_sun = (255, 70, 45)

    if 6 <= hour <= 12:

        t = (hour - 6) / 6

        return lerp_color(
            sunrise,
            noon_sun,
            t
        )

    else:

        t = (hour - 12) / 6

        return lerp_color(
            noon_sun,
            sunset_sun,
            t
        )


def draw_sun(draw, hour):

    # No sun between 18:00 and 06:00
    if hour < 6 or hour >= 18:
        return

    # 06:00 = 0
    # 12:00 = 0.5
    # 18:00 = 1
    progress = (hour - 6) / 12

    # Move left -> right
    x = 15 + progress * 210

    # Arc movement
    y = 140 - 120 * (
        4 * progress * (1 - progress)
    )

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


# --------------------------------------------------
# NIGHT VISIBILITY
# --------------------------------------------------

def get_night_visibility(hour):

    # Fade in
    if 18 <= hour < 19:
        return hour - 18

    # Fully visible
    elif hour >= 19 or hour < 5:
        return 1.0

    # Fade out
    elif 5 <= hour < 6:
        return 6 - hour

    else:
        return 0.0


# --------------------------------------------------
# MOON
# --------------------------------------------------

def draw_moon(draw, sky_color, hour, visibility):

    if visibility <= 0:
        return

    moon_color = (255, 245, 180)

    visible_color = lerp_color(
        sky_color,
        moon_color,
        visibility
    )

    # Convert 18:00 -> 06:00 into a 0 -> 1 journey
    if hour >= 18:
        night_hour = hour - 18
    else:
        night_hour = hour + 6

    progress = night_hour / 12

    # Left -> right
    x = 15 + progress * 210

    # Moon arc
    y = 140 - 95 * (
        4 * progress * (1 - progress)
    )

    radius = 16

    # Main moon circle
    draw.ellipse(
        (
            int(x - radius),
            int(y - radius),
            int(x + radius),
            int(y + radius)
        ),
        fill=visible_color
    )

    # Cover part of moon with sky
    # to make crescent shape
    draw.ellipse(
        (
            int(x - 3),
            int(y - radius - 5),
            int(x + radius + 8),
            int(y + radius - 5)
        ),
        fill=sky_color
    )


# --------------------------------------------------
# STARS
# --------------------------------------------------

def draw_stars(draw, sky_color, visibility):

    if visibility <= 0:
        return

    star_color = (255, 245, 180)

    stars = [
        (45, 30),
        (75, 65),
        (165, 35),
        (195, 70)
    ]

    radius = 3

    current_time = time.time()

    for i, (sx, sy) in enumerate(stars):

        # Gentle twinkle
        twinkle = (
            0.75
            + 0.25
            * math.sin(current_time * 2 + i * 1.7)
        )

        brightness = visibility * twinkle

        visible_color = lerp_color(
            sky_color,
            star_color,
            brightness
        )

        draw.ellipse(
            (
                sx - radius,
                sy - radius,
                sx + radius,
                sy + radius
            ),
            fill=visible_color
        )


# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------

while True:

    # ----------------------------------------------
    # 1. GET TIME
    # ----------------------------------------------

    if DEMO_MODE:

        elapsed = time.time() - demo_start_time

        hour = (
            DEMO_START_HOUR
            + elapsed * 24 / DEMO_SECONDS_PER_DAY
        ) % 24

    else:

        now = time.localtime()

        hour = (
            now.tm_hour
            + now.tm_min / 60
            + now.tm_sec / 3600
        )


    # ----------------------------------------------
    # 2. DRAW SKY
    # ----------------------------------------------

    sky_color = get_sky_color(hour)

    draw.rectangle(
        (0, 0, width, height),
        fill=sky_color
    )


    # ----------------------------------------------
    # 3. DRAW SUN
    # ----------------------------------------------

    draw_sun(
        draw,
        hour
    )


    # ----------------------------------------------
    # 4. DRAW MOON + STARS
    # ----------------------------------------------

    visibility = get_night_visibility(hour)

    draw_moon(
        draw,
        sky_color,
        hour,
        visibility
    )

    draw_stars(
        draw,
        sky_color,
        visibility
    )


    # ----------------------------------------------
    # 5. UPDATE DISPLAY
    # ----------------------------------------------

    disp.image(
        image,
        rotation
    )


    # ----------------------------------------------
    # 6. FRAME RATE
    # ----------------------------------------------

    if DEMO_MODE:
        time.sleep(0.05)
    else:
        time.sleep(1)
