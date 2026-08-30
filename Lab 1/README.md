# Recreating the Masters of Interactive Light

_This project is to be done in teams of 2._

**COLLABORATORS: Jianing Li & Jessica Chon**

**THE MASTERWORK YOU DREW FROM THE HAT: The Glow-in-the-dark Stars**

---

One way to understand greatness is to look to the greats. Just as painters learn
the technique and artistry of the old masters by recreating their paintings, so
too shall we come to understand computer-mediated interaction by recreating the
interactive masterworks of our time.

This week, every team will draw a different masterwork from a hat. Some are
conceptual pieces, some are historical works, some are modern-day products —
but they all share one thing: **their central mode of interaction is carried by
light.** Think of Tinker Bell in the original stage production of *Peter Pan*,
represented by nothing more than a darting circle of light from an off-stage
mirror. There was no actor playing Tinker Bell; she existed entirely through the
way the other characters interacted with that light.

Your job is to recreate the *interaction* of the piece you drew — not to build a
museum-grade replica, but to stage the moment that makes it what it is. Someone
who knows your piece should watch your recreation and recognize it instantly.
Someone who has never heard of it should walk away understanding what it is
famous for.

You will do this using the interaction staging techniques we will use all semester: a
storyboard, some acting, a phone standing in as a controllable light (the
*Tinkerbelle* tool), a hidden human "wizard" driving it, a costume, and a
recorded video.

*Make sure you read all the instructions and understand the whole activity
before starting!*

## Prep

To start, you will need:

1. Read about Git [here](https://git-scm.com/book/en/v2/Getting-Started-What-is-Git%3F).
2. Set up your own Github "Lab Hub" by forking the [Interactive-Lab-Hub repository](https://github.com/IRL-CT/Interactive-Lab-Hub). To get lab updates, simply use [GitHub's "Sync fork" button](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork) when new content is available.

3. Set up your `README.md` so it has your name and links to this lab. Learn to
   format a README [here](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).
4. **Draw your masterwork from the hat and write it at the top of this file.**
   Whatever you drew is yours — lean into it.

## Materials

For this lab you will need:

1. Paper, markers/pens, scissors
2. A smartphone with a browser that can display a webpage (your stand-in "light")
3. A computer to host the control webpage
4. Found objects and materials to **costume your phone so it looks like the
   device in your masterwork** — doll clothes, a paper lantern, a bottle, foil,
   a cardboard shell, whatever it takes. Be resourceful.

## Deliverables

Submit all of the following in this lab folder of your Lab Hub, as links or
uploaded files. **Each group member posts their own copy to their own Github repo**, even if the work is
shared.

1. A short **research write-up** of your masterwork (what it is, when, who made
   it, and — most importantly — what the interaction is)
2. **3 iterated storyboards** of the interaction in the masterwork
5. A **video sketch** of your prototyped interaction
6. Any **reflections** on the process

Labs are due on Mondays. Make sure this page is linked from your main class hub
page.

---

# **The Report**

## Part 0. Know Your Master

Before you prototype anything, get intimately acquainted with the piece you
drew. Do real research. You are looking less for trivia than for the *shape of
the interaction*:

- **What inputs are available to the user? What responses does the work give?**
     - *Primary input*: Surrounding light, including sunlight, lamplight, and room lighting.
     - *User interaction*: Turn on or turn off room lights, open or close curtains, install the stars on ceilings and walls, look at the stars.
     - *Responses*: Glow and become visible in the darkness just like real stars. Fade gradually. Appear brighter after stronger or longer light exposure.
- **Who is present, and how does the piece color the relationships between them?**
     - The primary users are children, particularly in a bedtime setting, while parents or caregivers often play a supporting role. A parent may turn off the bedroom light and leave the child with the glowing stars, creating a familiar transition from the daytime environment to bedtime. For children who are uncomfortable with darkness, the stars can make the room feel less empty or threatening and provide a familiar visual presence while they fall asleep. They can also create a shared moment of imagination between children and caregivers.
- **What is the piece famous for? What are its strengths and its weaknesses?**
     - The piece is famous for transforming an ordinary bedroom into a miniature night sky after the lights are turned off. Their most recognizable feature is their ability to absorb light during the day and produce a soft glow in the darkness, creating a simple but magical visual experience. For many children, the stars can turn bedtime into an imaginative experience, making the dark room feel less empty or frightening.
     - *Strengths*: Simplicity and accessibility. They require no complicated controls, batteries, or active input from the user. The interaction is largely created by the transition between light and darkness: light charges the stars, while darkness reveals their glow. They are also inexpensive, easy to install, and can transform a familiar environment with very little effort. Their passive nature can also make them a comforting and unobtrusive presence at bedtime.
     - *Weakness*: The stars provide very limited interactivity and cannot actively respond to the user's behavior or environment. Their brightness also gradually fades, so the experience is relatively passive and temporary. In addition, the stars depend on sufficient exposure to light beforehand, which means that their effectiveness can vary depending on the environment. Most importantly, while they can create a comforting atmosphere, they do not actively adapt to a child's individual needs or respond to changes in the child's emotional state.

**Describe your masterwork here, in your own words. What is the core interaction
someone would recognize it by?**
- Glow-in-the-dark stars transform a familiar bedroom into a small glowing night sky. During the day, they absorb ambient light. When the room becomes dark, the stored energy is released as a soft glow, which gradually fades over time.
- The core interaction is therefore *light → darkness → glow → gradual fading*. The user does not directly command the stars. Instead, an ordinary environmental change causes the stars to become visible. This passive interaction is what makes the stars feel magical: something that appeared ordinary during the day suddenly becomes visible and meaningful at bedtime.


## Part A. Plan


**Our setting, players, activity, and goals**

For our recreation, we started from the original bedtime experience of glow-in-the-dark stars and reinterpreted the way the stars become "charged".

- **Setting:** Where and when does this interaction happen? 
   - A child's bedroom at bedtime. The room is initially illuminated by a normal bedroom light. As the child prepares to sleep, the room becomes darker and the glow-in-the-dark stars on the wall or ceiling become the focus of attention.
- **Players:** Who is involved? Who else is present? Think through everyone in
  the setting, not just the primary user.
   - Child: The primary user. The child notices the stars, speaks to them, and makes a wish.
   - Parent/caregiver: A supporting character who helps establish the bedtime context and may introduce the idea of wishing to the stars.
   - Stars: The interactive element. They respond to the child's wish through changes in brightness and color.
- **Activity:** What is happening between the players and the light?
   - Instead of being charged passively by everyday exposure to light, the stars in our recreation are "charged" by a child's wishes.
   - The child notices that the stars have become dim and asks why they are no longer glowing. The child is encouraged to make a wish by saying "I wish..." toward the stars. A speech-recognition mechanism detects the phrase and triggers the stars to respond. The stars first become bright green to indicate that they have heard the child's wish, and then transition into a warm, bright yellow glow to represent the wish charging the stars. When no new wish is detected, the stars gradually become dimmer over time.
   - In this way, we reinterpret the original charging mechanism as an intentional interaction between the child and the stars.
- **Goals:** What is each player trying to do?
   - Visualize children's wishes. Turn an abstract and invisible wish into a visible response from the stars.
   - Encourage engagement. Transform a passive bedtime object into something children can actively interact with.
   - Create joy and imagination. Make bedtime feel playful, magical, and emotionally meaningful.
   - Create a sense of companionship: Make the stars feel as if they are listening and responding to the child.


**Storyboards**

**Click [here](https://github.com/jianingli189/Interactive-Lab-Hub/blob/Fall2026/Lab%201/Storyboards.jpg) to see our storyboards.**
Our three-scene storyboard explores the interaction as a bedtime ritual:
1. Notice: The child notices that the stars have become dim and wonders why they are no longer glowing.
2. Wish: The child is encouraged to make a wish and says "I wish..." toward the stars.
3. Response: The stars acknowledge the wish by becoming brighter, creating a visible and joyful response for the child.
The storyboard helped us shift the stars from a passive decorative object into an interactive bedtime companion while preserving their original association with darkness, bedtime, and imagination.

**Feedback and Iteration**

Our initial concept was relatively simple: the child would make a wish, and the stars would become brighter as if the wish had charged them.
When we acted out and prototyped the interaction, however, we noticed a communication problem. If the stars simply became brighter after the child spoke, it was difficult to tell whether the stars had actually heard the child's wish or whether the change in brightness was simply a programmed response.
We therefore introduced an intermediate feedback state. When the system detects the phrase "I wish", the stars change from a dim yellow to a bright green. This acts as an acknowledgment cue: the stars have heard the child. After the child finishes expressing the wish, the stars transition from green to a brighter warm yellow, representing the stars being "charged" by the wish. They then gradually fade when there is no new interaction.
This iteration made the interaction more legible by giving the child a clear cause-and-effect sequence:
*Wish → Stars listen → Stars acknowledge → Stars become charged → Stars gradually fade*.


## Part B. Act out the Interaction

Acting out the storyboard helped us realize that the interaction needed a clearer moment of acknowledgment.
On paper, the sequence of "child makes a wish → stars light up" seemed intuitive. However, when we physically acted it out, we noticed that the child had no clear indication that the stars had actually heard the wish. The transition from speaking to the stars becoming brighter happened too abruptly.
This led us to introduce an intermediate response from the stars. The stars briefly change color to signal that the wish has been heard before becoming fully charged.
Acting also helped us recognize that the interaction is not strictly sequential. After the stars become bright, the child can make another wish, wait and watch the stars fade, or interact with the stars again later. The system therefore needs to support a repeating interaction loop rather than a single fixed sequence.
Key interaction loop:
Stars dim → Child notices → Child makes a wish → Stars acknowledge → Stars glow → Stars fade → Child can wish again.


## Part C. Prototype the Light (light first!)

**Click [here](https://github.com/jianingli189/Interactive-Lab-Hub/blob/Fall2026/Lab%201/Light%20prototype.jpg) to see our light prototype.**

We used a smartphone as the stand-in light for the stars and controlled its visual output through the prototype setup in a laptop.
Our main focus was not on reproducing the physical appearance of the original glow-in-the-dark stars, but on reproducing their recognizable light behavior and our reinterpretation of the charging interaction.
We prototyped several light states:
1. Dim yellow: The stars are waiting for interaction.
2. Green: The stars have detected "I wish" and are acknowledging the child's wish.
3. Bright yellow: The stars have been "charged" by the wish.
4. Gradual fading: The stars slowly lose their brightness when there is no new wish.
This allowed us to test whether the light itself could communicate the interaction before adding additional modalities.


## Part D. Wizard the Device

We used a wizarded setup to simulate the behavior of the interactive stars without implementing the complete sensing and control system.
One person acted as the child and interacted with the stars, while another person secretly controlled the light states from the computer. The hidden "wizard" changed the stars between dim yellow, green, and bright yellow based on the child's speech and actions.
This allowed us to test the interaction from the user's perspective without requiring the final speech-recognition system to be fully implemented.


## Part E. (optional) Costume the Device

**Click [here](https://github.com/jianingli189/Interactive-Lab-Hub/blob/Fall2026/Lab%201/Costumed%20device.jpg) to see our Costumed device.**

For the physical prototype, we wanted the phone to visually read as a glowing star rather than as a smartphone. We covered most of the phone's surface with sticky notes and left a small star-shaped opening in the center. The light from the screen could therefore shine through the star-shaped opening, making the phone appear like a single glowing star.
We also drew and attached several additional paper stars around the phone to create the feeling of a larger starry sky rather than a single isolated light. This helped us recreate the original context of glow-in-the-dark stars, which are typically installed together across a child's bedroom wall or ceiling.
The costume also helped separate the device itself from the technology behind it. Although the smartphone was controlling the light, the visual prototype encouraged the viewer to perceive the light as a star that could listen and respond to the child.


## Part F. Record

**Click [here](https://github.com/jianingli189/Interactive-Lab-Hub/blob/Fall2026/Lab%201/Prototyping%20Process.jpg) to see our whole prototyping process.**

**Click [here](https://github.com/jianingli189/Interactive-Lab-Hub/blob/Fall2026/Lab%201/Interaction%20Demo%20Video.mp4) to see our video.**

Our video sketch demonstrates the core interaction between the child and the stars.
The child notices that the stars are dim, makes a wish by saying "I wish...", and receives a visible response from the stars. The stars first acknowledge the wish with a green light and then become brighter to represent being charged by the child's wish.
The video focuses on the interaction sequence rather than the final physical appearance of the device. We wanted the viewer to understand that the child's wish is what causes the stars to become charged and glow.

We preserved the original stars' core metaphor of "charging and glowing," but changed what provides the energy: from ambient light to a child's imagination.
| Original                        | Our Recreation                   |
| ------------------------------- | -------------------------------- |
| Ambient light charges the stars | A child's wish charges the stars |
| Invisible charging              | Visible interaction              |
| Passive                         | Intentional                      |
| Light → glow                    | Wish → response → glow           |
| Quiet companionship             | Interactive companionship        |
| Gradual fading                  | Gradual fading                   |

**Collaborators:** Jianing Li & Jessica Chon
Both collaborators contributed to the research, interaction concept, storyboard development, prototyping, acting, and iteration of the project.

---

# Part 2 — ReMastering the light

*This describes the second week's work for this lab activity.*

## Prep (before the next lab)

Find three other groups. (How? Maybe Slack?) Visit their Lab Hub pages, watch their
videos, and give them reactions and feedback: tell them what you saw happening,
guess the masterwork and the goals of the characters, and ask about anything that
wasn't clear.

**Who were the other groups you kibitzed with? Add links to their project pages here.**
**Summarize the feedback you got from your partners here.**

## Remix, Update, or Critique the Master

Now that you understand your masterwork from the inside, respond to it. Do the
recreation again, but this time make it your own — pick one of these moves (or
combine them):

1. **Remix the modality.** Your recreation no longer has to (just) use light. Use
   vibration, sound, motion, heat — whatever best carries the interaction. Feel
   free to fork and modify the Tinkerbelle code. (Add your updates to this lab's folder!)
2. **Update it.** Redesign the piece for today's context, or for a setting its
   creators never imagined (the piece with roommates in the room, with children
   present, on a phone, in a car).
3. **Fix its weaknesses.** You identified this master's strengths and weaknesses
   in Part 0 — now address a weakness, or push a strength further.

We will grade this second pass with an emphasis on **creativity** and on how well
your response engages with what your master was really doing.

**Document everything here — especially the storyboard and video. Photos of the
prototype are great too.**

---



*Assignment lineage: this lab merges "Staging Interaction" (Interactive Lab Hub)
with "Recreating the Masters" (Interaction Design Studio, Profs. Scott Minneman &
Wendy Ju). Massive list of interactive light masterworks generated by Claude.ai.*
