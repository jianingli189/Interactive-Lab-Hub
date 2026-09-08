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
   - The child is encouraged to make a wish by saying "I wish..." toward the stars. When the child says the phrase, the stars respond by becoming bright green to indicate that they have heard the child's wish, and then transition into a warm, bright yellow glow to represent the wish charging the stars.
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

We visited 4 other groups' Lab Hub pages and reviewed their interaction videos. We paid particular attention to whether the masterworks were recognizable, how clearly the light communicated its behavior, and how the characters interacted with the light.

**Groups and Their Feedback**
1. Lamiah Khan & Rawisara Chairat (https://github.com/khanlamiah019/Interactive-Lab-Hub/tree/Fall2026/Lab%201)
   "i love the creativity within the interaction w the light up stars (especially since usually light up stars dont have much to them currently). I also liked the development process as you made the stars more clear. In terms of improvements, I think it would be nice to expand on what happens when the interaction ends (when the wish is made, is the light distinguished? especially since you mentioned this is for children, what happens after? What happens if the user makes another wish)."
2. Shenye Wang & Bowei Huang (https://github.com/sw2486-hub/Interactive-Lab-Hub/blob/Fall2026/Lab%201/README.md)
   "I really liked the idea of using a child’s wish to “charge” the stars instead of just using ambient light. The green light as feedback was also a nice touch because it makes it clear that the stars actually heard the wish before they light up. I think this makes the original glow-in-the-dark stars feel much more interactive and gives the child a sense that the stars are responding to them. One thing I was curious about is what would happen if the system doesn’t recognize the child’s wish correctly. Overall, I think it’s a really creative way to turn a simple bedtime decoration into an interactive experience!"
3. Yujing Zhou, Youssef Hassan (https://github.com/jUSTbEarOCk/Interactive-Lab-Hub/tree/Fall2026/Lab%201)
   "Maybe move the phone while the children are making a wish to mimic a meteor and make the interaction more interesting. By the way, I think the version right now is already very beautiful."
4. Yuni Park (https://github.com/parky20/Interactive-Lab-Hub/tree/Fall2026/Lab%201)
   "The video in part D highlights the movement and changes of light accurately. The star shaped cut out on the phone also clearly shows what the device looks like. I really like how you guys added the interaction part between the kids and the stars. Compared to the regular glow in the dark star stickers, it is more interactive and fun for the users (kid)! I think the new device you guys ideated could potentially become a great project for this class as you can use voice recognition/AI tools to make the stars react to the user's voice -> charge."



**Feedback Summary**
The feedback helped us reflect on how the child understands and experiences the interaction, rather than only on how the stars look or change color.
1. Instruction and context: The child needs to understand how to interact with the stars, especially when using them independently at bedtime. In our first version, the parent verbally explained what the child should do, but the interaction did not clearly show how this instruction would carry into the child's own bedtime routine. In response, we set up a bed to simulate the child sleeping alone and developed a two-part scenario: the parent first introduces the stars and explains how to make a wish, and the child later remembers and uses the interaction independently.
2. Acknowledgment: The child needs to know that the stars have heard the wish. Based on the feedback, we made this moment more explicit through both sound and color. When the child says “I wish,” the stars respond with a “ding” and turn blue, signaling that they are listening. After the child finishes the wish, the stars respond with “bing bing bing~” and become brighter and warmer yellow, showing that the wish has charged them. In our first version, green was used as the acknowledgment state. In the second iteration, we changed this state to blue to create a clearer distinction between "listening" and "charged" states, with warm yellow reserved for the final charged glow.
3. Continuation: The interaction should not end immediately after one wish. The stars gradually become dim again after responding, preserving the fading quality of the original glow-in-the-dark stars while allowing the child to make another wish later. This also makes the interaction feel more like part of a bedtime routine rather than a single isolated action.
These reflections led us to rethink the stars not simply as a light that responds to a command, but as a bedtime companion that is introduced by the parent, listens to the child’s wish, acknowledges it, and responds through light and sound.
**Click [here](https://github.com/jianingli189/Interactive-Lab-Hub/blob/Fall2026/Lab%201/Iteration%20Sketch.jpg) to see our iteration sketch.** The sketch documents how we translated the feedback into changes to the interaction, including the two-scene structure, clearer acknowledgment through sound and color, and a repeatable bedtime interaction.



## Remix, Update, or Critique the Master

For our second iteration, we chose to update the original glow-in-the-dark stars and fix some of their limitations. We added sound as a second feedback modality to complement the original light-based interaction.

The original glow-in-the-dark stars are passive: ambient light charges them, darkness reveals them, and their brightness gradually fades. We wanted to preserve this familiar "charging and glowing" metaphor while giving the child a more intentional role in the interaction.

Our redesigned experience takes place in two connected scenes.

**Scene 1: Introducing the stars**

In the first scene, a parent helps the child put up the stars and introduces the interaction. Instead of explaining the stars only as decorations, the parent tells the child that they can make a wish to charge the stars. This gives the child a simple mental model for understanding how the new interaction works.
The parent therefore acts as an onboarding guide, helping the child understand that their voice can affect the stars.
**Scene 2: The bedtime interaction**

In the second scene, the child is lying in bed at night and looking at the stars on the wall. As the stars become dim, the child remembers the parent's earlier instruction and says, "I wish..." followed by a wish.
The stars first respond with a "ding" sound and a blue light. This is an acknowledgment state that communicates: the stars are listening. After the child finishes the wish, the stars respond with a series of "bing bing bing~" sounds while becoming brighter and changing to a warm yellow. This represents the child's wish charging the stars.
After the interaction, the stars gradually become dim again. This creates an interaction loop rather than a one-time response:
Stars dim → Child notices → Child makes a wish → Stars acknowledge → Child finishes the wish → Stars become charged → Stars gradually fade → Child can make another wish.

**Click [here](https://github.com/jianingli189/Interactive-Lab-Hub/blob/Fall2026/Lab%201/Lab1b_video.mp4) to see our updated interaction demo.** The updated video demonstrates both scenes: the parent's introduction of the interaction and the child's later independent bedtime interaction. 



### How our redesign responds to the original masterwork
We wanted to preserve the most recognizable aspect of the original masterwork: the transformation of darkness into a glowing night sky. However, instead of ambient light being the only source of energy, we reinterpret the child's imagination and wishes as the source of the stars' energy.
| Original Glow-in-the-dark Stars | Our ReMastered Stars |
| --- | --- |
| Ambient light charges the stars | A child's wish charges the stars |
| Passive interaction | Intentional interaction |
| Darkness reveals the stars | A child's voice activates the stars |
| Glow provides visual comfort | Light and sound provide feedback |
| No explicit acknowledgment | "Ding" + blue light = stars are listening |
| Gradual fading | Gradual fading allows repeated interaction |
| Decorative object | Interactive bedtime companion |



### Why we made these changes
Our goal was not to replace the original interaction completely, but to extend the meaning of "charging". In the original masterwork, the stars absorb physical light. In our version, they metaphorically absorb a child's wishes.
This change addresses one of the main weaknesses we identified in the original object: its limited interactivity. The original stars respond automatically to environmental light but do not acknowledge or respond to the person using them. Our version gives the child a clearer sense of agency: the child says something, the stars acknowledge it, and then the stars visibly respond.
We also added sound because light alone did not always make the interaction sufficiently explicit. The "ding" provides an immediate acknowledgment that the stars have heard the child, while the "bing bing bing~" sound accompanies the charging process. The combination of speech, sound, color, and brightness makes the cause-and-effect relationship more legible.
At the same time, we intentionally kept the gradual fading behavior from the original masterwork. This preserves the temporal quality of glow-in-the-dark stars and creates an opportunity for repeated wishes rather than making the interaction a single one-time event.



## Reflection on the ReMastering
Through this second iteration, we moved from recreating a passive lighting phenomenon to designing a small interactive relationship between a child and the stars. The parent introduces the interaction, but the child eventually learns to initiate it independently. The stars are therefore not simply a decoration or a light source; they become a familiar bedtime companion that appears to listen and respond.
The most important change in our understanding of the masterwork is that its value does not come only from the visual effect of glowing stars. It comes from the transition from an ordinary dark room to an imagined starry world. Our redesign keeps this transformation while giving the child a more active role in creating it.
Our final interaction can therefore be summarized as:
Wish → Listen → Acknowledge → Charge → Glow → Fade → Wish again.

---



*Assignment lineage: this lab merges "Staging Interaction" (Interactive Lab Hub)
with "Recreating the Masters" (Interaction Design Studio, Profs. Scott Minneman &
Wendy Ju). Massive list of interactive light masterworks generated by Claude.ai.*
