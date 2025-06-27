# ==============================================================================
#
#                                PRIMORDIA
#         A Generative Evolution RPG - Final Unified Code
#
# =================================to=============================================
# This script combines all the separate files (main.py, world.py, organism.py)
# and integrates the full gameplay mechanics from our design session.
# You can save this entire block as a single `primordia.py` file and run it.
# ==============================================================================

import numpy as np
import json
import random
from ai_interface import AIInterface
import copy
import time
import matplotlib.pyplot as plt

# --- Simulation Constants ---
WORLD_WIDTH = 50
WORLD_HEIGHT = 50
INITIAL_POPULATION = 15

# ==============================================================================
# --- From world.py ---
# ==============================================================================

class World:
    """
    Manages the 2D environment, including nutrients, and world events.
    """
    def __init__(self, width, height, diffusion_rate=0.1, nutrient_source_pos=None, nutrient_amount=10.0):
        self.width = width
        self.height = height
        self.diffusion_rate = diffusion_rate
        self.nutrient_a = np.zeros((width, height), dtype=np.float64)

        if nutrient_source_pos is None:
            self.nutrient_source_pos = (width // 2, height // 2)
        else:
            self.nutrient_source_pos = nutrient_source_pos

        self.nutrient_amount = nutrient_amount
        self.nutrient_a[self.nutrient_source_pos] = self.nutrient_amount
        
        # For Phase 4 Gameplay
        self.active_event = None
        self.toxin_grid = np.zeros((width, height), dtype=np.float64)

    def update_environment(self):
        """Updates the environment by diffusing nutrients and applying world events."""
        # --- Nutrient Diffusion (from your code) ---
        laplacian = (  self.nutrient_a[:-2, 1:-1]  # Up
                     + self.nutrient_a[2:, 1:-1]   # Down
                     + self.nutrient_a[1:-1, :-2]  # Left
                     + self.nutrient_a[1:-1, 2:]   # Right
                     - 4 * self.nutrient_a[1:-1, 1:-1])
        self.nutrient_a[1:-1, 1:-1] += self.diffusion_rate * laplacian
        self.nutrient_a[self.nutrient_source_pos] = self.nutrient_amount
        np.clip(self.nutrient_a, 0, None, out=self.nutrient_a)
        
        # --- Toxin Diffusion and Decay ---
        if np.any(self.toxin_grid > 0):
            toxin_laplacian = ( self.toxin_grid[:-2, 1:-1] + self.toxin_grid[2:, 1:-1] +
                                self.toxin_grid[1:-1, :-2] + self.toxin_grid[1:-1, 2:] -
                                4 * self.toxin_grid[1:-1, 1:-1] )
            self.toxin_grid[1:-1, 1:-1] += self.diffusion_rate * toxin_laplacian
            # Toxins slowly decay over time
            self.toxin_grid *= 0.95
            np.clip(self.toxin_grid, 0, None, out=self.toxin_grid)

        # --- Apply Event Effects (Phase 4) ---
        if self.active_event == "acid_rain":
            # Acid rain slightly increases toxin levels everywhere
            self.toxin_grid += 0.005
        elif self.active_event == "ice_age":
            # Ice age halves nutrient replenishment
            self.nutrient_a[self.nutrient_source_pos] = self.nutrient_amount / 2
    
    def get_nutrient(self, x, y):
        return self.nutrient_a[x, y]

    def consume_nutrient(self, x, y, amount):
        current_amount = self.nutrient_a[x, y]
        consumed = min(current_amount, amount)
        self.nutrient_a[x, y] -= consumed
        return consumed
        
    def get_toxin(self, x, y):
        return self.toxin_grid[x, y]
        
    def find_spawn_location(self):
        return np.random.randint(0, self.width), np.random.randint(0, self.height)

# ==============================================================================
# --- From organism.py ---
# ==============================================================================

class Organism:
    """
    Represents a single organism in the world.
    """
    REPRODUCTION_ENERGY = 150.0

    def __init__(self, world, x, y, genome, energy=100.0):
        self.world = world
        self.x = x
        self.y = y
        self.genome = genome # This is the unique genome for THIS organism
        self.energy = energy
        self.dx = 0
        self.dy = 0

    def sense(self):
        """Simple strategy: move towards the neighboring cell with the most nutrients."""
        best_pos = (self.x, self.y)
        max_nutrient = -1

        sensory_range = int(self.genome.get('SensoryRange', 1))
        for dx in range(-sensory_range, sensory_range + 1):
            for dy in range(-sensory_range, sensory_range + 1):
                if dx == 0 and dy == 0: continue
                nx = (self.x + dx) % self.world.width
                ny = (self.y + dy) % self.world.height
                
                nutrient_level = self.world.get_nutrient(nx, ny)
                if nutrient_level > max_nutrient:
                    max_nutrient = nutrient_level
                    self.dx, self.dy = np.sign(dx), np.sign(dy)
        
        if self.dx == 0 and self.dy == 0:
            self.dx, self.dy = np.random.randint(-1, 2), np.random.randint(-1, 2)

    def move(self):
        self.x = (self.x + self.dx) % self.world.width
        self.y = (self.y + self.dy) % self.world.height
        self.dx, self.dy = 0, 0
        self.energy -= self.genome.get('MovementCost', 0.2)
        
    def eat(self):
        amount_to_eat = self.genome.get('MetabolismRate', 0.1) * 10
        consumed = self.world.consume_nutrient(self.x, self.y, amount_to_eat)
        self.energy += consumed * 5

    def metabolize(self):
        self.energy -= self.genome.get('BaseMetabolism', 0.5)
        
        # Metabolize toxins (Phase 4)
        toxin_level = self.world.get_toxin(self.x, self.y)
        resistance = self.genome.get('ToxinBResistance', 0.0)
        damage = max(0, toxin_level - resistance) * 10
        self.energy -= damage


    def should_die(self):
        return self.energy <= 0

    def should_reproduce(self):
        return self.energy >= self.REPRODUCTION_ENERGY

    def reproduce(self, base_genome): # Now accepts the lineage's base genome
        self.energy /= 2
        offspring_energy = self.energy

        mutated_genome = self._mutate_genome(base_genome) # Mutates from the BASE, not parent
        
        offspring_x = (self.x + np.random.randint(-1, 2)) % self.world.width
        offspring_y = (self.y + np.random.randint(-1, 2)) % self.world.height

        return Organism(self.world, offspring_x, offspring_y, mutated_genome, offspring_energy)

    def _mutate_genome(self, base_genome):
        mutated_genome = copy.deepcopy(base_genome)
        for key, value in mutated_genome.items():
            mutation_factor = 1.0 + np.random.uniform(-0.1, 0.1)
            mutated_genome[key] = value * mutation_factor
        return mutated_genome

# ==============================================================================
# --- Synthesized lineage.py (Phase 4) ---
# ==============================================================================

class PlayerLineage:
    """Manages the player's entire collection of organisms and evolutionary path."""
    def __init__(self, world):
        self.world = world
        self.base_genome = {
            'MetabolismRate': 0.1,
            'MovementCost': 0.2,
            'BaseMetabolism': 0.5,
            'SensoryRange': 1,
            'ToxinBResistance': 0.0
        }
        self.organisms = []
        self.generation = 1
        self.evolutionary_potential = 100
        self.milestone_pop_50_reached = False

        self.spawn_organisms(INITIAL_POPULATION)

    def spawn_organisms(self, count):
        for _ in range(count):
            x, y = self.world.find_spawn_location()
            self.organisms.append(Organism(self.world, x, y, self.base_genome))
            
    def evolve_gene(self, gene, delta, cost):
        if self.evolutionary_potential >= cost:
            self.base_genome[gene] += delta
            self.evolutionary_potential -= cost
            print(f"[EVOLUTION] Base {gene} modified by {delta}. {cost} EP spent.")
            
            # --- Apply Trade-offs ---
            if gene == "ToxinBResistance":
                self.base_genome["BaseMetabolism"] += 0.01
                print("[TRADE-OFF] BaseMetabolism slightly increased.")
            return True
        else:
            print(f"[EVOLUTION FAILED] Not enough EP. Required: {cost}, Have: {self.evolutionary_potential}")
            return False


# ==============================================================================
# --- Core Game Logic (from main.py and Phase 4) ---
# ==============================================================================

def run_simulation_steps(steps, world, lineage):
    """Runs the simulation for a given number of steps."""
    for step in range(steps):
        if not lineage.organisms: break

        world.update_environment()
        survivors, new_offspring = [], []

        for org in lineage.organisms:
            org.sense()
            org.move()
            org.eat()
            org.metabolize()

            if org.should_reproduce():
                # Pass the lineage's BASE genome for mutation
                new_offspring.append(org.reproduce(lineage.base_genome))
            if not org.should_die():
                survivors.append(org)
        
        lineage.organisms = survivors + new_offspring

def check_for_achievements(lineage):
    """Checks for milestones and awards EP."""
    if len(lineage.organisms) > 50 and not lineage.milestone_pop_50_reached:
        print("\n[ACHIEVEMENT] Population surpassed 50! +75 EP")
        lineage.evolutionary_potential += 75
        lineage.milestone_pop_50_reached = True

def world_event_phase(world):
    """Triggers random world events."""
    if random.random() < 0.25: # 25% chance of an event each turn
        events = ["acid_rain", "ice_age", "nutrient_bloom"]
        chosen_event = random.choice(events)
        print(f"\n[WORLD EVENT] A strange phenomenon occurs: {chosen_event.replace('_', ' ').title()}!")
        world.active_event = chosen_event
        if chosen_event == "nutrient_bloom":
            world.nutrient_amount *= 1.5 # Temporarily boost nutrient source
    else:
        if world.active_event == "nutrient_bloom":
            world.nutrient_amount /= 1.5 # Revert bloom effect
        world.active_event = None

def print_status_report(lineage):
    print("\n--- Lineage Status Report ---")
    print(f"  Generation: {lineage.generation} | Population: {len(lineage.organisms)}")
    print(f"  Evolutionary Potential (EP): {lineage.evolutionary_potential}")
    print("  Base Genome:")
    for gene, value in lineage.base_genome.items():
        print(f"    - {gene}: {value:.3f}")
    print("-----------------------------")
    
def gather_game_state_for_ai(player_lineage, world) -> str:
    """Collects data and formats it for the AI."""
    dominant_threat = "None"
    if np.mean(world.toxin_grid) > 0.01:
        dominant_threat = "Toxins"
        
    game_data = {
        "generation": player_lineage.generation,
        "population": len(player_lineage.organisms),
        "ep": player_lineage.evolutionary_potential,
        "world_state": { "dominant_threat": dominant_threat },
        "player_choices": [
            {"choice": "increase_toxin_resistance", "cost": 60, "delta": 0.05},
            {"choice": "decrease_metabolism", "cost": 40, "delta": -0.02},
            {"choice": "improve_sensing", "cost": 30, "delta": 1},
            {"choice": "wait", "cost": 0, "delta": 0}
        ]
    }
    return json.dumps(game_data, indent=2)

def game_loop():
    """The main game loop with visualization and full AI narrative."""
    # --- Initial Setup ---
    world = World(WORLD_WIDTH, WORLD_HEIGHT)
    player_lineage = PlayerLineage(world)
    try:
        ai_interface = AIInterface()
    except ConnectionError as e:
        print(e)
        return # Exit if AI can't connect

    print("="*40)
    print("Welcome to Primordia")
    print("Guide your lineage to survive and dominate.")
    print("="*40)

    # --- Matplotlib Setup ---
    plt.ion() # Turn on interactive mode
    fig, ax = plt.subplots(figsize=(8, 8))
    # Initial image rendering
    display_grid = np.zeros((WORLD_WIDTH, WORLD_HEIGHT))
    im = ax.imshow(display_grid, cmap='viridis', vmin=0, vmax=15)
    fig.show()

    # --- The Main Game Loop ---
    while True:
        if not player_lineage.organisms:
            print("\n--- GAME OVER: EXTINCTION ---")
            break

        # --- Gameplay Phase ---
        # 1. Potentially trigger a world event
        world_event_phase(world)

        # 2. Run the core simulation
        print("\nThe world churns... Generations pass...")
        run_simulation_steps(steps=50, world=world, lineage=player_lineage)
        player_lineage.generation += 1

        # 3. Check for Achievements & Award EP
        check_for_achievements(player_lineage)

        # --- Visualization Phase ---
        # Create a display grid: nutrients are the background
        display_grid = world.nutrient_a.copy()
        # Normalize for better color range
        if np.max(display_grid) > 0:
            display_grid = display_grid / np.max(display_grid) * 10
        # Add organisms as bright dots on top
        for org in player_lineage.organisms:
            display_grid[org.x, org.y] = 15 # Brightest value
        
        ax.set_title(f"Turn: {player_lineage.generation} | Population: {len(player_lineage.organisms)}")
        im.set_data(display_grid)
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        # --- AI & Player Interaction Phase ---
        print_status_report(player_lineage)

        # 4. Get the Narrative from the AI (Step 1 of conversation)
        print("\n[Contacting AI Chronicler for a report...]")
        game_state_json = gather_game_state_for_ai(player_lineage, world)
        narrative = ai_interface.start_new_turn(game_state_json)
        print("\n--- AI Chronicle ---")
        print(narrative)
        print("--------------------")

        # 5. Get Player Input
        choices_data = json.loads(game_state_json)["player_choices"]
        try:
            player_choice_input = input("> What is your command? ")
        except EOFError: # Handles quitting the program with Ctrl+D
            break

        # 6. Get the Final Command from the AI (Step 2 of conversation)
        command_response = ai_interface.get_player_command(player_choice_input)
        command = command_response.get("command_to_execute", "wait")
        print(f"\n[Executing AI-confirmed command: {command}]")

        # 7. Execute the command
        executed = False
        for choice_option in choices_data:
            if choice_option['choice'] == command:
                if command != "wait":
                    gene_map = {
                        "increase_toxin_resistance": "ToxinBResistance",
                        "decrease_metabolism": "BaseMetabolism",
                        "improve_sensing": "SensoryRange"
                    }
                    player_lineage.evolve_gene(gene_map[command], choice_option['delta'], choice_option['cost'])
                executed = True
                break
        if not executed:
            print("AI returned an unknown command. The lineage waits.")

        print(f"\n{'='*10} END OF TURN {player_lineage.generation -1} {'='*10}")
        time.sleep(1) # Small pause to make the loop readable

    print("Closing visualization.")
    plt.ioff()
    plt.show()


if __name__ == "__main__":
    # Ensure you have your classes and helper functions defined before this call
    # For this to work, you need to have the full primordia.py script as one file.
    # So, PASTE your World, Organism, PlayerLineage, and all helper functions
    # into the top of this script.
    game_loop()