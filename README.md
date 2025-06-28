# Welcome to Primordia\!

We are so glad you're here to explore this unique world. Primordia is a text-based generative RPG where you don't play a character, but rather guide the evolution of a primordial organism. The game world is a dynamic 2D cellular automaton governed by mathematical laws, creating emergent environmental pressures. Your RPG choices directly manipulate your species' genome, and you witness the results of natural selection in a real-time visualization.

This project was born from a passion for combining concepts from evolutionary biology, cellular automata, generative AI, and classic RPGs into a novel, text-driven experience.

(github-recording.gif)

## Core Concepts

  * **A Living World:** The environment is not a static map. It's a 2D grid where nutrients diffuse and toxins spread according to mathematical models, creating ever-changing challenges and opportunities for your lineage.
  * **Evolution in Your Hands:** Your organisms live, move, eat, reproduce, and die on the grid. Offspring inherit the `base_genome` of their lineage with a chance of mutation, driving natural selection forward.
  * **Meaningful Choices:** As the "guiding hand," you earn Evolutionary Potential (EP) by completing milestones. You can then spend EP to make directed changes to your lineage's core DNA, giving them the edge they need to survive.
  * **A Dynamic Narrator:** The game is narrated by the "AI Chronicler," a live connection to Google's Gemini model. It analyzes the game state each turn to provide rich, situational, and evocative descriptions of your lineage's ongoing saga.

## Features

  * **Real-Time Visualization:** Watch your cellular automata world come to life with a `matplotlib` plot that displays nutrients and organisms.
  * **Automated Setup:** Simple shell scripts are included to handle all setup and dependency installation for you.
  * **AI-Powered Narrative:** Every game is unique, with story elements and descriptions generated live by the Gemini AI.
  * **Emergent Gameplay:** The interaction between the mathematical world and the evolving organisms leads to unpredictable and fascinating outcomes.

## Tech Stack

  * **Python 3:** The core language for the simulation.
  * **NumPy:** For high-performance numerical operations on the world grid.
  * **Matplotlib:** To provide the real-time visualization.
  * **Google Gemini API:** To power the dynamic AI narrator.

## Getting Started: A Simple, Automated Setup

We've created simple scripts to make getting started as easy as possible. Please follow these steps carefully.

#### Step 1: Get the Code

First, you'll need to get the project files onto your computer. If you have Git installed, you can clone the repository.

```bash
git clone [https://github.com/software-cpu/primordia_project]
cd primordia
```

#### Step 2: Add Your Google AI API Key

To connect to the AI Narrator, you need a free API key from [Google AI Studio](https://aistudio.google.com/).

Once you have your key, **open the `run.sh` file** in a text editor. You will see a line at the top:

```sh
API_KEY="AIzaSyA_ND4DTy4TmMyQfLglliZdwQCBNTRh1Ls"
```

**Replace the key in the quotes** with your own personal API key and save the file. This ensures the AI can connect every time you run the game.

#### Step 3: Run the One-Time Setup Script

Next, we need to run a script that will create a virtual environment and install all the necessary libraries.

First, you may need to make the scripts executable. You only need to do this once.

```bash
chmod +x setup.sh run.sh
```

Now, run the setup script:

```bash
./setup.sh
```

This will take a moment to install `numpy`, `matplotlib`, and the Google AI library.

#### Step 4: Play the Game\!

That's it\! You are all set up. From now on, whenever you want to play, just navigate to the project folder in your terminal and run this single command:

```bash
./run.sh
```

The game will launch, complete with the AI connection and the visualization window. We hope you enjoy it\!

***A Note for Windows Users:*** *These scripts (`.sh`) are designed for Unix-style shells. If you are on Windows, we highly recommend using [Git Bash](https://git-scm.com/downloads), which is included with the standard Git for Windows installation, to run this project.*
Of course. A section detailing the mathematics is a fantastic idea for a project like this. It adds depth to the README and highlights the scientific principles that make the game's emergent behavior possible.

Here is a sidebar written in Markdown. You can copy and paste this entire section into your `README.md` file, perhaps just before the "Tech Stack" or "How to Play" sections.

### The Mathematical Heart of Primordia

The complex and often unpredictable behavior of the Primordia ecosystem isn't magic; it's an emergent property arising from several layers of mathematics working in concert. Here’s a deeper look at the engine under the hood.

#### 1. The Diffusion Equation: A World in Motion

The core of the dynamic environment is a Partial Differential Equation (PDE) known as the **Heat Equation**, or more generally, the **Diffusion Equation**. In its continuous form, it's written as:

$$\frac{\partial u}{\partial t} = D \nabla^2 u$$

* $u$ represents the concentration of a substance (like our nutrient).
* $t$ is time.
* $D$ is the diffusion constant, controlling how fast the substance spreads.
* $\nabla^2$ is the Laplacian operator, which essentially measures the curvature or "lumpiness" of the concentration.

In simple terms, this equation states that the rate of change in concentration at a point is proportional to the difference between that point and the average of its surroundings. This is the fundamental law that makes nutrients spread out from their source.

In our game, we can't solve this continuous equation perfectly. Instead, we use a discrete approximation on our grid called the **Forward-Time Central-Space (FTCS)** scheme. For each cell `(i, j)` at each time step `t`, the new concentration is calculated based on its neighbors:

$$u_{i,j}^{t+1} \approx u_{i,j}^{t} + \alpha (u_{i+1,j}^{t} + u_{i-1,j}^{t} + u_{i,j+1}^{t} + u_{i,j-1}^{t} - 4u_{i,j}^{t})$$

Here, $\alpha$ is a factor related to our `diffusion_rate`. This simple calculation, when applied across the whole grid every step, creates the beautiful, flowing patterns of our nutrient field.

#### 2. Organism Energetics: The Math of Life and Death

Each organism's survival is governed by a simple but strict energy budget, which can be viewed as a system of **difference equations**:

$$E_{t+1} = E_{t} + \Delta E$$

Where the change in energy, $\Delta E$, per turn is calculated as:

$$\Delta E = E_{\text{gained}} - (E_{\text{metabolism}} + E_{\text{movement}} + E_{\text{damage}})$$

* $E_{\text{gained}}$ is a function of the nutrient level in the organism's current cell and its `MetabolismRate` gene.
* $E_{\text{metabolism}}$ is the constant energy cost to simply exist for one turn, modified by its `BaseMetabolism` gene.
* $E_{\text{movement}}$ is the energy cost for moving, determined by its `MovementCost` gene.
* $E_{\text{damage}}$ is the health lost from environmental hazards like toxins, offset by its `ToxinBResistance` gene.

Life and death are determined by simple but critical **inequalities**:
* **Reproduction:** `If` $E \geq E_{\text{reproduction}}$
* **Death:** `If` $E \leq 0$

#### 3. Genetics and Stochastic Processes

Randomness, or **stochasticity**, is crucial for creating diversity and unpredictable evolution. This is primarily seen in genetic mutation. When an organism reproduces, the offspring's genome is based on the lineage's `base_genome`, but with a random factor applied:

$$\text{gene}_{\text{new}} = \text{gene}_{\text{base}} \times (1 + \mathcal{U}(-0.1, 0.1))$$

Where $\mathcal{U}(-0.1, 0.1)$ represents a random number drawn from a uniform distribution between -0.1 and 0.1. This **multiplicative noise** ensures that evolution has a wide range of traits to select from over many generations.

#### 4. Cellular Automata and Grid Dynamics

The entire world is a **Cellular Automaton**: a grid of cells where the state of each cell (e.g., its nutrient level) evolves based on a set of rules applied to its local neighbors.

A key piece of math that makes our grid continuous and interesting is **Modulo Arithmetic**. When an organism moves, its new position is calculated as:

$$x_{\text{new}} = (x_{\text{old}} + \Delta x) \pmod{W}$$

Where $W$ is the width of the world. This operation creates a "toroidal" or "wrap-around" world, so an organism moving off the right edge instantly reappears on the left. This prevents sterile edge conditions and keeps the ecosystem fully interactive.

## How to Play

  * The game runs in turns. The `matplotlib` window shows a top-down view of your world.
  * Each turn, your terminal will display a status report of your lineage and a beautiful narrative from the AI Chronicler.
  * You will be given a list of evolutionary commands, each with an EP cost.
  * Type the number corresponding to your choice and press Enter to guide your lineage's evolution.
  * Watch the simulation run and see the consequences of your choice in the visualization and the next turn's report.
  * Your goal is to survive, adapt, and thrive in the primordial soup\!

## File Structure

  * `primordia.py`: The main, unified script containing all game logic and classes.
  * `ai_interface.py`: Handles the connection and conversational logic with the Google Gemini API.
  * `setup.sh`: A one-time script to create the virtual environment and install dependencies.
  * `run.sh`: The script you use to launch the game. **Remember to add your API key here\!**
  * `README.md`: This file, providing guidance and information about the project.

Thank you for checking out Primordia. We hope you have a wonderful time guiding your lineage to greatness\!
