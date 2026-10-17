## Lab Overview
Members: Jianing Li(jl4837), Aurora Jiaxin Shen(js3996), Demi Hu(dh785), Tzu-Yao Chang(tc845)
Clock name: <Etiquette Bonquet>

---
### Part D
### Physical Interaction Design: Feast Automata

**\*\*\*Draw 5 sketches that explore different physical arrangements for your sensing and actuation.\*\*\***

We began by individually brainstorming different ways to transform familiar dining behaviors into playful physical interactions. As a group, we developed five different Feast Automata concepts. Each concept explored a different relationship between a dining behavior, sensing method, and physical actuation.

<img width="1460" height="1042" alt="fd2492cbb96655dc926207231e09dfb2" src="https://github.com/user-attachments/assets/6a001347-e4d3-4f7b-b4cb-1343f91ab847" />

<img width="1600" height="899" alt="beb18a8e29aeba8572a4b40c747efdf8" src="https://github.com/user-attachments/assets/b3309e06-0e9c-4680-90a7-a830b505daf9" />

<img width="1809" height="1280" alt="0eb8faadc4822fdd4165d21e718c2efa" src="https://github.com/user-attachments/assets/84ea3274-c383-487d-a851-8c6a3d263036" />

<img width="1707" height="1280" alt="a3b384916a6fed51b0096f1a4ddf1df7" src="https://github.com/user-attachments/assets/d1aef762-3dfa-4e22-b8c6-f6b905f26376" />


**\*\*\*What questions do these sketches raise? What do you need to physically prototype to answer them?\*\*\***

Comparing our five ideas raised several questions about both the interaction and physical implementation:

- Which dining behavior creates the clearest and most meaningful relationship between sensing and physical feedback?
- Can the sensing interaction happen naturally without requiring users to perform an additional action just for the sensor?
- Where should sensors and actuators be placed so that they do not interfere with normal dining behavior?
- How noticeable should the physical feedback be?
- Can different servo movements communicate different meanings without additional text or screen feedback?
- How can the electronics and moving components be integrated into a tabletop object without making the dining setup feel cluttered?

For the Etiquette Flower concept specifically, we wanted to physically prototype several questions:
- Can we reliably detect when individual metal utensils are removed from the placemat using capacitive sensing?
- How large and how far apart should the sensing areas underneath the utensils be?
- Where should the flower be positioned so that its movement is visible without interfering with the meal?
- Can the flower clearly communicate two different states through a gentle nod and rapid spinning?
- How can the servos and electronics be housed inside or underneath the flower structure?


**\*\*\*Pick one design to prototype and explain why.\*\*\***

We finally picked this idea: **Etiquette Flower**

This concept is inspired by the conventions of Western dining etiquette, particularly the practice of selecting utensils in a particular order during a multi-course meal. For our prototype scenario, the expected sequence is soup spoon → outer fork and knife → inner fork and knife. The user selects utensils as they eat. Sensing areas underneath the placemat detect which utensil has been picked up. If the user selects the expected utensil, a small flower gently nods. If the user selects an incorrect utensil, the flower rapidly spins to provide more noticeable corrective feedback.

Sensing & actuation: Capacitive sensing underneath the utensil positions detects utensil selection. Servo-driven movements allow the flower to nod or spin in response.

We chose this concept because it transforms an existing dining convention into a playful interaction without requiring the user to learn a completely new behavior. The user simply selects utensils as they normally would, while the system responds through the movement of the flower. We were also interested in using physical movement rather than a screen or written instructions as feedback. The contrast between a gentle nod for a correct selection and rapid spinning for an incorrect selection creates two visually distinct responses while keeping the interaction playful. The concept also gave us a clear way to integrate both sensing and actuation into the physical table setting: sensing can be embedded underneath the placemat, while the flower serves as the visible actuated object.

Our intended interaction flow is:

User begins the meal
↓
User picks up a utensil
↓
The system detects which utensil was removed
↓
The Raspberry Pi compares it with the expected utensil
- Correct → Flower gently nods
- Incorrect → Flower rapidly spins
↓
The system waits for the next utensil selection


**\*\*\*Document your rough prototype with photos and/or video.\*\*\***

**Prototype Process**

We built a low-fidelity prototype to explore the overall physical arrangement of the selected concept, including the placement of the plate, utensils, sensing areas, and flower.

<img width="1707" height="1280" alt="23f4fb0b861f38c2a287dc92b8787796" src="https://github.com/user-attachments/assets/8db3dce8-6a5e-4fea-bfcc-a78ca51625eb" />

<img width="1280" height="960" alt="67ca3eb1c6449294ed0984af8f9770eb" src="https://github.com/user-attachments/assets/a9c34d14-86ad-4f77-95a1-b976cd1df521" />

Our prototype helped us explore the scale and position of the flower relative to the dining setup and how the sensing areas could be integrated underneath the utensil positions.

**Final Prototype**

<img width="1707" height="1280" alt="f21abee3c6eca146d665b67e4d909ce4" src="https://github.com/user-attachments/assets/5ab2f77c-734a-4291-94c9-97405fecfef6" />

Our planned implementation uses capacitive sensing underneath the placemat. Separate copper-tape electrodes correspond to different utensil positions and connect to an MPR121 capacitive sensing board. The Raspberry Pi uses these signals to identify which utensil has been removed.

The flower provides the physical output. We plan to use servo-driven movement to create two different feedback behaviors:

- Correct utensil → gentle nod
- Incorrect utensil → rapid spin

We will test the sensing reliability, electrode placement, sensing thresholds, and flower mechanisms during the next stage of implementation.

We also recorded a Wizard-of-Oz demonstration of the intended interaction.


https://github.com/user-attachments/assets/50672203-766c-4e02-83a6-3138f499a55a


The video demonstrates the complete interaction sequence, including both correct and incorrect utensil selections.

Team

<img width="1707" height="1280" alt="eb35664b3cf3e968faf420e777e68e7d" src="https://github.com/user-attachments/assets/3eff010b-ed37-4e32-afec-29aaf32e91f5" />

---

## Part 2

Following exploration and reflection from Part 1, complete the "looks like," "works like" and "acts like" prototypes for your design, reiterated below.

---

### Part E

#### Build & Integrate: Sensing + Actuation

For Part 2, build the Feast Automata interaction you developed in Part D by connecting sensing/input to physical actuation.

**Your prototype should:**
- Use at least one sensing or input device.
- Use servo-based physical actuation.
- Connect sensing and actuation into a meaningful interaction around eating, drinking, cooking, serving, or sharing food.
- Additional inputs, displays, LEDs, buttons, or other outputs are optional extensions.

**Document your system with:**
- Code for your sensing + actuation prototype
- Photos and/or video of the working prototype in action
- A simple interaction diagram or sketch showing how sensing and actuation are connected
- Written reflection: What did you learn about connecting sensing, movement, and physical form? What was fun, surprising, or challenging?

**Questions to consider:**
- How does your chosen sensor or input shape the physical response?
- How does the physical arrangement of the sensor and actuator change the interaction?
- What thresholds, timing, or movement patterns make the interaction feel clear or playful?
- What changes when you adjust the sensor placement or servo motion?

Iterate on the sensing, movement, and physical form, and document what you discover.

See encoder_accel_servo_dashboard.py in the Lab 4 folder for an optional example of chaining together three devices.

**`Lab 4/encoder_accel_servo_dashboard.py`**

#### Example Application: Windmill Coaster

Now that you have explored both sensing and actuation, here is a simple example that combines the two.

The **Windmill Coaster** uses a Qwiic distance/proximity sensor to detect when a cup is placed on a coaster. When the cup is detected, a servo motor animates a small windmill by sweeping it back and forth, turning an ordinary action during drinking into a playful physical interaction.

<p align="center">
    <img src="windmill_coaster11.gif" alt="Windmill Coaster Demo" width="400"/>
</p>


This example demonstrates a simple interaction pipeline:

**cup placed → distance sensor detects cup → servo actuates windmill**

Connect the Qwiic distance sensor to the Pi and connect the servo to Channel 0 of the Servo pHAT. Make sure the Servo pHAT is powered through its USB-C connection.

Run the example script:

```bash
python windmill_coaster.py
```

The script continuously reads the proximity value from the distance sensor. When the value passes a threshold, the servo begins animating the windmill. When the cup is removed, the servo stops and returns to its resting position.

You may need to adjust `CUP_THRESHOLD` in [`windmill_coaster.py`](windmill_coaster.py) depending on the size of your cup and the physical placement of the sensor. You can run `qwiic_distance.py` first to compare readings with and without a cup.

Use this example as a starting point. Change the sensor, movement, physical form, or dining interaction to create your own Feast Automata variation.

#### Optional Extensions

The following examples are optional resources if you want to add more inputs or outputs to your prototype.

##### Using Multiple Qwiic Buttons: Changing I2C Address (Physically & Digitally)

If you want to use more than one Qwiic Button in your project, you must give each button a unique I2C address. There are two ways to do this:

##### 1. Physically: Soldering Address Jumpers

On the back of the Qwiic Button, you'll find four solder jumpers labeled A0, A1, A2, and A3. By bridging these with solder, you change the I2C address. Only one button on the chain can use the default address (0x6F).

**Address Table:**

| A3 | A2 | A1 | A0 | Address (hex) |
|----|----|----|----|---------------|
|  0 |  0 |  0 |  0 |    0x6F       |
|  0 |  0 |  0 |  1 |    0x6E       |
|  0 |  0 |  1 |  0 |    0x6D       |
|  0 |  0 |  1 |  1 |    0x6C       |
|  0 |  1 |  0 |  0 |    0x6B       |
|  0 |  1 |  0 |  1 |    0x6A       |
|  0 |  1 |  1 |  0 |    0x69       |
|  0 |  1 |  1 |  1 |    0x68       |
|  1 |  0 |  0 |  0 |    0x67       |
| ...| ...| ...| ... |     ...      |

For example, if you solder A0 closed (leave A1, A2, A3 open), the address becomes 0x6E.

**Soldering Tips:**
- Use a small amount of solder to bridge the pads for the jumper you want to close.
- Only one jumper needs to be closed for each address change (see table above).
- Power cycle the button after changing the jumper.

##### 2. Digitally: Using Software to Change Address

You can also change the address in software (temporarily or permanently) using the example script `qwiic_button_ex6_changeI2CAddress.py` in the Lab 4 folder. This is useful if you want to reassign addresses without soldering.

Run the script and follow the prompts:
```bash
python qwiic_button_ex6_changeI2CAddress.py
```
Enter the new address (e.g., 5B for 0x5B) when prompted. Power cycle the button after changing the address.

**Note:** The software method is less foolproof and you need to make sure to keep track of which button has which address!


##### Using Multiple Buttons in Code

After setting unique addresses, you can use multiple buttons in your script. See these example scripts in the Lab 4 folder:

- **`qwiic_1_button.py`**: Basic example for reading a single Qwiic Button (default address 0x6F). Run with:
	```bash
	python qwiic_1_button.py
	```

- **`qwiic_button_led_demo.py`**: Demonstrates using two Qwiic Buttons at different addresses (e.g., 0x6F and 0x6E) and controlling their LEDs. Button 1 toggles its own LED; Button 2 toggles both LEDs. Run with:
	```bash
	python qwiic_button_led_demo.py
	```

Here is a minimal code example for two buttons:
```python
import qwiic_button

# Default button (0x6F)
button1 = qwiic_button.QwiicButton()
# Button with A0 soldered (0x6E)
button2 = qwiic_button.QwiicButton(0x6E)

button1.begin()
button2.begin()

while True:
		if button1.is_button_pressed():
				print("Button 1 pressed!")
		if button2.is_button_pressed():
				print("Button 2 pressed!")
```

For more details, see the [Qwiic Button Hookup Guide](https://learn.sparkfun.com/tutorials/qwiic-button-hookup-guide/all#i2c-address).

---

##### PCF8574 GPIO Expander: Add More Pins Over I²C

Sometimes your Pi’s header GPIO pins are already full (e.g., with a display or HAT). That’s where an I²C GPIO expander comes in handy.

We use the Adafruit PCF8574 I²C GPIO Expander, which gives you 8 extra digital pins over I²C. It’s a great way to prototype with LEDs, buttons, or other components on the breadboard without worrying about pin conflicts—similar to how Arduino users often expand their pinouts when prototyping physical interactions.

**Why is this useful?**
- You only need two wires (I²C: SDA + SCL) to unlock 8 extra GPIOs.
- It integrates smoothly with CircuitPython and Blinka.
- It allows a clean prototyping workflow when the Pi’s 40-pin header is already occupied by displays, HATs, or sensors.
- Makes breadboard setups feel more like an Arduino-style prototyping environment where it’s easy to wire up interaction elements.

**Demo Script:** `Lab 4/gpio_expander.py`

<p align="center">
    <img src="gpio_leds.gif" alt="GPIO Expander LED Demo" width="400"/>
</p>

We connected 8 LEDs (through 220 Ω resistors) to the expander and ran a little light show. The script cycles through three patterns:
- Chase (one LED at a time, left to right)
- Knight Rider (back-and-forth sweep)
- Disco (random blink chaos)

Every few runs, the script swaps to the next pattern automatically:
```bash
python gpio_expander.py
```

This is a playful way to visualize how the expander works, but the same technique applies if you wanted to prototype buttons, switches, or other interaction elements. It’s a lightweight, flexible addition to your prototyping toolkit.

---


---

---

### Part F

### Final Documentation

Document all the prototypes and iterations you have designed and worked on! Again, deliverables for this lab are writings, sketches, photos, and videos that show what your prototype:
* "Looks like": shows how the device should look, feel, sit, weigh, etc.
* "Works like": shows what the device can do
* "Acts like": shows how a person would interact with the device

---

## Deliverables \& Submission for Lab 4

The deliverables for this lab are, writings, sketches, photos, and videos that show what your prototype:
* "Looks like": shows how the device should look, feel, sit, weigh, etc.
* "Works like": shows what the device can do.
* "Acts like": shows how a person would interact with the device.

For submission, the readme.md page for this lab should be edited to include the work you have done:
* Upload any materials that explain what you did, into your lab 4 repository, and link them in your lab 4 readme.md.
* Link your Lab 4 readme.md in your main Interactive-Lab-Hub readme.md. 
* Labs are due on Mondays, make sure to submit your Lab 4 readme.md to Canvas.
