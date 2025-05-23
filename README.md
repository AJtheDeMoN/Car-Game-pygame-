
# 3D Car Driving Game

This project presents a 3D car driving game built with Pygame and OpenGL. It features an OBJ-based car viewer, dynamically generated roads, and a follow camera, allowing for an immersive driving experience.

## Features:
* **OBJ Model Loading**: Loads 3D models for the car, trees, and grass using custom OBJ and MTL (Material Template Library) parsers.
* **Dynamic Road Generation**: Generates a random, winding road path for varied gameplay each time.
* **Follow Camera**: The camera dynamically follows the car, providing a classic third-person driving perspective.
* **Basic Physics**: Implements acceleration, braking, friction, and steering for realistic car movement.
* **Collision Detection**: Detects if the car goes off-road, triggering a "Game Over" state.
* **Interactive Scenery**: Populates the environment with randomly placed trees and grass models.
* **Dynamic Lighting**: Features a movable light source (simulating a sun) with adjustable position.
* **Audio Integration**: Includes sound effects for acceleration, braking, engine, horn, and crash.
* **Heads-Up Display (HUD)**: Displays real-time information such as speed, elapsed time, and best time.
* **Restart Functionality**: Allows players to restart the game after a win or loss.
* **Car Customization**: Users can select from different car textures in the viewer mode before starting the game.


## Getting Started

### Prerequisites

Before running the game, ensure you have the following Python libraries installed:

* `pygame`
* `PyOpenGL`
* `Pillow` (PIL)
* `numpy`

You can install them using pip:

```bash
pip install pygame PyOpenGL Pillow numpy
```

### Running the Game

1.  **Clone the repository or download the files**: Ensure all Python scripts (`main.py`, `driving_game_mode.py`, `viewer_mode.py`, `OBJ.py`, `RoadSegment.py`) and the `OBJs`, `textures`, and `audio` folders are in the same directory.
2.  **Run the main script**:

    ```bash
    python main.py
    ```

---

## How to Play

Upon launching the game, you'll first enter the **Viewer Mode**.

### Viewer Mode Controls:

* **Left/Right Arrow Keys**: Cycle through available car textures.
* **Enter**: Select the current car texture and start the driving game.
* **Mouse Drag**: Rotate the car model.
* **Mouse Wheel**: Zoom in/out on the car model.
* **Q/E**: Rotate the light source (sun).
* **Escape**: Exit the application.

### Driving Game Mode Controls:

* **Up Arrow**: Accelerate forward.
* **Down Arrow**: Brake/Accelerate backward.
* **Left Arrow**: Steer left.
* **Right Arrow**: Steer right.
* **H**: Honk the horn.
* **Q/E**: Rotate the light source (sun).
* **R**: Increase speed multiplier (for acceleration, top speed, etc.).
* **F**: Decrease speed multiplier.
* **W/A/D**: Change camera view (front, left, right).
* **Enter**: Restart the game after a "Game Over" or "You Win" screen.
* **Escape**: Return to the car texture selection screen (viewer mode).

---

## Game Objective

The goal is to drive your car along the generated road without going off-road. Try to reach the end of the road in the fastest time possible!

---

## Project Structure

* `main.py`: The entry point of the game, managing the switch between viewer and driving modes.
* `viewer_mode.py`: Handles the initial car texture selection and viewing, including model rotation and zoom.
* `driving_game_mode.py`: Contains the core game logic for driving, physics, rendering, and audio.
* `OBJ.py`: Custom class for loading and rendering OBJ 3D models with material and texture support.
* `RoadSegment.py`: Defines the structure and rendering for individual road segments and grass strips.
* `OBJs/`: Directory containing `.obj` and `.mtl` 3D model files (e.g., car, tree, grass).
* `textures/`: Directory for car textures and other model textures.
* `audio/`: Directory for game sound effects.

---

## Acknowledgments

* OBJ models and textures from various open-source resources.
* Audio effects from royalty-free sound libraries.
