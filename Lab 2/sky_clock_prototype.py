import time
import digitalio
import board
from PIL import Image, ImageDraw
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

# Turn on backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True


# --------------------------------------------------
# DEMO MODE
# --------------------------------------------------

DEMO_MODE = True

# One complete simulated day takes 24 real seconds
DEMO_SECONDS_PER_DAY = 24

# Start at 06:00
DEMO_START_HOUR = 6.0

demo_start_time = time.time()


# --------------------------------------------------
# COLOR FUNCTIONS
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


def get_sky_color(hour):
    """
    Smooth sky color transition:

    00:00 -> deep night blue
    06:00 -> pale morning blue
    12:00 -> bright blue
    18:00 -> orange-red sunset
    24:00 -> deep night blue
    """

    midnight = (10, 25, 70)
    morning = (170, 210, 225)
    noon = (45, 170, 245)
    sunset = (235, 95, 65)

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


# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------

while True:

    # Get simulated or real time
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

    # Calculate current sky color
    sky_color = get_sky_color(hour)

    # Fill the whole screen with sky color
    draw.rectangle(
        (0, 0, width, height),
        fill=sky_color
    )

    # Update display
    disp.image(image, rotation)

    # Fast refresh for smooth demo
    if DEMO_MODE:
        time.sleep(0.05)
    else:
        time.sleep(1)
