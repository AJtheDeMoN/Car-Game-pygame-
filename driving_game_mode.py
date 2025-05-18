# This is a full integration of your OBJ-based car viewer into a driving game with road generation and movement.
# Note: This version uses keyboard for driving (UP/DOWN to move, LEFT/RIGHT to rotate),
# and replaces orbiting camera with follow camera.

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import math 
import random
import time
import pygame.freetype
import pygame.mixer
import numpy as np
from OBJ import OBJ
from RoadSegment import RoadSegment

# Initialize Pygame and OpenGL
pygame.init()
global font
font = pygame.freetype.SysFont("Arial", 24)

global texture_index
texture_index = 0

def setup_lighting():
    """Configure basic lighting for the scene."""
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    ambient = [0.2, 0.2, 0.2, 1.0]
    diffuse = [0.9, 0.9, 0.8, 1.0]
    specular = [1.0, 1.0, 1.0, 1.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

def draw_cube(size=1.0):
    """Draw a simple cube of specified size."""
    hs = size / 2.0  # half size

    vertices = [
        [ hs, hs, -hs], [ hs, -hs, -hs], [-hs, -hs, -hs], [-hs, hs, -hs],  # back
        [ hs, hs,  hs], [ hs, -hs,  hs], [-hs, -hs,  hs], [-hs, hs,  hs],  # front
    ]

    surfaces = [
        [0, 1, 2, 3],  # back
        [4, 5, 6, 7],  # front
        [0, 4, 5, 1],  # right
        [3, 7, 6, 2],  # left
        [0, 4, 7, 3],  # top
        [1, 5, 6, 2],  # bottom
    ]

    glBegin(GL_QUADS)
    for surface in surfaces:
        for vertex in surface:
            glVertex3fv(vertices[vertex])
    glEnd()
    
def draw_ground_tile(center_x, center_z, size=70.0):
    """Draw a flat ground tile at specified position."""
    half = size / 2
    y = -0.05
    glColor3f(0.9, 1, 0.9)
    glBegin(GL_QUADS)
    glVertex3f(center_x - half, y, center_z - half)
    glVertex3f(center_x + half, y, center_z - half)
    glVertex3f(center_x + half, y, center_z + half)
    glVertex3f(center_x - half, y, center_z + half)
    glEnd()



# -------------------- Game Logic Functions --------------------
def generate_road():
    """Generate a random road path with connected segments."""
    segments = []
    path = [(0, 0)]
    for i in range(1, 100):
        last = path[-1]
        angle = random.uniform(-30, 30)
        dist = 6
        new_x = last[0] + math.sin(math.radians(angle)) * dist
        new_z = last[1] + math.cos(math.radians(angle)) * dist
        path.append((new_x, new_z))

    for i in range(len(path) - 1):
        segments.append(RoadSegment(path[i], path[i + 1]))
    return segments

def check_on_road(car_pos, road, road_width=2.0):
    """Check if car is on the road."""
    cx, cz = car_pos

    for seg in road:
        x1, z1 = seg.p1
        x2, z2 = seg.p2

        # Vector from point 1 to point 2
        dx = x2 - x1
        dz = z2 - z1

        # Vector from point 1 to the car
        px = cx - x1
        pz = cz - z1

        # Project point onto segment
        seg_len_squared = dx * dx + dz * dz
        if seg_len_squared == 0:
            continue  # Avoid divide-by-zero

        t = max(0, min(1, (px * dx + pz * dz) / seg_len_squared))
        closest_x = x1 + t * dx
        closest_z = z1 + t * dz

        # Distance from car to closest point
        dist_squared = (cx - closest_x) ** 2 + (cz - closest_z) ** 2

        if dist_squared <= road_width ** 2:
            return True  # On the road

    return False  # Off the road

def draw_text(text, x, y, color=(255, 255, 255)):
    """Draw 2D text on screen with specified color."""
    # Switch to orthographic projection for 2D rendering
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 1000, 0, 800, -1, 1)  # Match your display size
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Render text to a surface
    text_surface, rect = font.render(text, color)
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    
    # Create a texture
    text_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, text_texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_surface.get_width(), text_surface.get_height(), 
                0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    # Draw the texture as a quad
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x, y)
    glTexCoord2f(1, 0); glVertex2f(x + text_surface.get_width(), y)
    glTexCoord2f(1, 1); glVertex2f(x + text_surface.get_width(), y + text_surface.get_height())
    glTexCoord2f(0, 1); glVertex2f(x, y + text_surface.get_height())
    glEnd()
    
    # Clean up
    glDisable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)
    glDeleteTextures([text_texture])
    
    # Restore previous state
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

def setup_audio():
    """Initialize and configure audio for the game."""
    pygame.mixer.init()
    
    # Load sound effects
    sounds = {
        'acceleration': pygame.mixer.Sound('audio/acceleration.mp3'),
        'brake': pygame.mixer.Sound('audio/brakes.mp3'),
        'engine': pygame.mixer.Sound('audio/engine.mp3'),
        'horn': pygame.mixer.Sound('audio/horn.mp3'),
        'crash': pygame.mixer.Sound('audio/crash.mp3'),
        'nature': pygame.mixer.Sound('audio/nature.mp3')
    }
    
    # Set volumes
    sounds['nature'].set_volume(0.2)  # Nature at low volume
    sounds['engine'].set_volume(0.7)
    sounds['acceleration'].set_volume(0.7)
    sounds['brake'].set_volume(0.7)
    sounds['horn'].set_volume(1)
    sounds['crash'].set_volume(1.0)
    
    return sounds

def initialize_opengl(display):
    """Setup initial OpenGL state."""
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    setup_lighting()
    glClearColor(0.53, 0.8, 0.95, 1)
    glDisable(GL_CULL_FACE)
    glShadeModel(GL_SMOOTH)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, display[0] / display[1], 0.1, 200.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def load_models():
    """Load 3D models for the game."""
    car_model = OBJ('OBJs/car.obj', override_texture=f"textures/texture{texture_index}.png")
    tree_model = OBJ("OBJs/tree.obj")
    grass1_model = OBJ("OBJs/grass1.obj")
    grass2_model = OBJ("OBJs/grass2.obj")
    
    return car_model, tree_model, grass1_model, grass2_model

def generate_scenery(road,tree_model):
    """Generate random scenery (trees and grass) along the road."""
    scenery = []
    for seg in road:
        mid_x = (seg.p1[0] + seg.p2[0]) / 2
        mid_z = (seg.p1[1] + seg.p2[1]) / 2
        angle = math.atan2(seg.p2[1] - seg.p1[1], seg.p2[0] - seg.p1[0])
        
        tree_count = random.randint(1, 3)
        
        # Helper function to place objects along the road
        def place_objects(model, count, min_dist, max_dist, scale):
            for _ in range(count):
                side = random.choice([-1, 1])
                dist = random.uniform(min_dist, max_dist)
                dx = math.cos(angle + math.pi / 2) * dist
                dz = math.sin(angle + math.pi / 2) * dist
                offset_x = mid_x + dx * side
                offset_z = mid_z + dz * side
                scenery.append((model, offset_x, offset_z, scale))

        # Place trees
        place_objects(tree_model, tree_count, 4, 12, 1.0)
        
    return scenery

def handle_audio(keys, car_speed, moving_forward, moving_backward, 
                 game_over, game_win, currently_playing, horn_playing, 
                 crash_played, sounds):
    """Handle game audio based on current state."""
    if not (game_over or game_win):
        # Horn sound (non-looping, play once per press)
        if keys[pygame.K_h] and not horn_playing:
            sounds['horn'].play(0)  # Play once
            horn_playing = True
        elif not keys[pygame.K_h]:
            horn_playing = False
        
        # Car movement sounds (looping)
        if (moving_forward and car_speed > 0) or (moving_backward and car_speed < 0):
            if currently_playing != 'acceleration':
                sounds[currently_playing].stop()
                sounds['acceleration'].play(-1)
                currently_playing = 'acceleration'
        elif (moving_backward and car_speed > 0) or (moving_forward and car_speed < 0):
            if currently_playing != 'brake':
                sounds[currently_playing].stop()
                sounds['brake'].play(-1)
                currently_playing = 'brake'
        elif car_speed == 0 or moving_forward==False or moving_backward==False:
            if currently_playing != 'engine':
                sounds[currently_playing].stop()
                sounds['engine'].play(-1)
                currently_playing = 'engine'
    # Game over - play crash sound once
    if game_over and not crash_played:
        sounds[currently_playing].stop()
        sounds['crash'].play()
        crash_played = True
        currently_playing = 'crash'
    
    if game_win:
        sounds[currently_playing].stop()
        sounds['engine'].play(-1)
        currently_playing = 'engine'
        
    return currently_playing, horn_playing, crash_played

def update_car_physics(keys, car_speed, car_angle, car_pos, times, max_speed, 
                      acceleration, brake_force, friction, game_over, game_win, dt):
    """Update car physics based on inputs and current state and time elapsed."""
    if game_over or game_win:
        # In the game over case, we still need to return all 10 values
        moving_forward = False
        moving_backward = False
        return car_speed, car_angle, car_pos, times, max_speed, acceleration, brake_force, friction, moving_forward, moving_backward
        
    moving_forward = keys[pygame.K_UP]
    moving_backward = keys[pygame.K_DOWN]
    
    # Scale all physics values by delta time (dt)
    frame_acceleration = acceleration * dt * 15  # Scale to make it feel similar at 15fps
    frame_brake_force = brake_force * dt * 15
    frame_friction = friction * dt * 15
    
    # Acceleration & Braking
    if moving_forward:
        if car_speed < 0:
            car_speed += frame_brake_force
        else:
            car_speed = min(car_speed + frame_acceleration, max_speed)
    elif moving_backward:
        if car_speed > 0:
            car_speed -= frame_brake_force
        else:
            car_speed = max(car_speed - frame_acceleration, -max_speed / 2)
    else:
        if car_speed > 0 and frame_friction > car_speed:
            car_speed = 0
        elif car_speed < 0 and -frame_friction < car_speed:
            car_speed = 0
        else:
            if car_speed > 0:
                car_speed -= frame_friction
            elif car_speed < 0:
                car_speed += frame_friction
            else:
                car_speed = 0

    # Adjust speed multiplier - scale by dt to make consistent at any frame rate
    if keys[pygame.K_r] and times < 4.9:
        times += 0.1 * dt * 15
        max_speed = 0.5 * times
        acceleration = 0.1 * times
        brake_force = 0.05 * times
        friction = 0.02 * times
    if keys[pygame.K_f] and times > 0.51:
        times -= 0.1 * dt * 15
        max_speed = 0.5 * times
        acceleration = 0.1 * times
        brake_force = 0.05 * times
        friction = 0.02 * times

    # Steering - scale rotation by dt
    steering_speed = 1.0 * dt * 60  # Base steering speed
    if car_speed != 0:
        if keys[pygame.K_LEFT]:
            car_angle += (steering_speed * times * car_speed / max_speed * 0.7)
        if keys[pygame.K_RIGHT]:
            car_angle -= (steering_speed * times * car_speed / max_speed * 0.7)

    # Move car - actual movement scaled by dt
    rad = math.radians(car_angle)
    movement = car_speed * dt * 30  # Scale movement by dt
    car_pos[0] += math.sin(rad) * movement
    car_pos[1] += math.cos(rad) * movement
    
    # Make sure to return all 10 values, including moving_forward and moving_backward
    return car_speed, car_angle, car_pos, times, max_speed, acceleration, brake_force, friction, moving_forward, moving_backward

def update_camera(keys, car_pos, car_angle):
    """Update camera position based on car position and view keys."""
    cam_offset = 10
    rad = math.radians(car_angle)
    if keys[pygame.K_w]:
        cam_x = car_pos[0] + math.sin(rad) * cam_offset
        cam_z = car_pos[1] + math.cos(rad) * cam_offset
    elif keys[pygame.K_a]:
        cam_x = car_pos[0] + math.cos(rad) * cam_offset
        cam_z = car_pos[1] - math.sin(rad) * cam_offset
    elif keys[pygame.K_d]:
        cam_x = car_pos[0] - math.cos(rad) * cam_offset
        cam_z = car_pos[1] + math.sin(rad) * cam_offset
    else:
        cam_x = car_pos[0] - math.sin(rad) * cam_offset
        cam_z = car_pos[1] - math.cos(rad) * cam_offset

    return cam_x, cam_z

def update_lighting(keys, light_angle, dt):
    """Update the light position based on user input and time elapsed."""
    rotation_speed = 2.0 * dt * 60  # Scale by dt
    light_angle += 0.1
    if keys[pygame.K_q]:
        light_angle = (light_angle + rotation_speed) % 360.0
    if keys[pygame.K_e]:
        light_angle = (light_angle - rotation_speed) % 360.0
        
    return light_angle

def calculate_light_position(light_angle):
    """Calculate the light position based on the light angle."""
    light_radius = 2000.0
    light_height = 1000.0
    light_x = math.sin(math.radians(light_angle)) * light_radius
    light_z = math.cos(math.radians(light_angle)) * light_radius
    
    return light_x, light_height, light_z

def draw_sun(light_x, light_height, light_z):
    """Draw a visual representation of the sun."""
    glPushMatrix()
    glTranslatef(light_x, light_height, light_z)
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 0.0)  # Yellow for sun
    glScalef(1.0, 1.0, 1.0)  # Scale for sun size
    draw_cube(1.0)  # Use your existing draw_cube function
    glEnable(GL_LIGHTING)
    glPopMatrix()

def draw_road_and_scenery(road, scenery):
    """Draw the road, grass, and scenery objects."""
    # Ground start and end
    draw_ground_tile(*road[0].p1)
    draw_ground_tile(*road[-1].p2)

    # Draw road and grass
    for i, seg in enumerate(road):
        seg.draw()
        seg.draw_grass_strip()
        if i < len(road) - 1:
            seg.draw_connection(road[i + 1])
            seg.draw_grass_connection(road[i + 1])

    # Draw trees and grass
    for model, x, z, scale in scenery:
        glPushMatrix()
        glTranslatef(x, 0, z)
        glScalef(0.2, 0.2, 0.2)
        model.render()
        glPopMatrix()

def draw_car(car_pos, car_angle, car_model):
    """Draw the car at its current position and rotation."""
    glPushMatrix()
    glTranslatef(car_pos[0], 0.0, car_pos[1])
    glRotatef(car_angle, 0, 1, 0)
    glScalef(1, 1, 1)
    car_model.render()
    glPopMatrix()

def draw_hud(best_time, car_speed, times, start_time, game_over, game_win, elapsed_time):
    """Draw the heads-up display with game information."""
    # Draw best time    
    draw_text(f"Best Time: {best_time:.2f}s", 10, 10, (255, 255, 255))
    # Draw car speed
    current_speed = car_speed * 100
    draw_text(f"Speed: {int(current_speed)}", 10, 40, (255, 255, 255))
    # Draw times speed
    draw_text(f"Times: {times:.1f}", 10, 70, (255, 255, 255))

    if start_time and not game_over and not game_win:
        elapsed = float(time.time() - start_time)
        draw_text(f"Time: {elapsed:.2f}s", 10, 740, (255, 255, 255))

    if game_over:
        draw_text("GAME OVER", 400, 420, (255, 0, 0))  # Centered, red
        draw_text("Press ENTER to Restart", 350, 370, (255, 255, 255))

    if game_win:
        elapsed = float(elapsed_time)
        draw_text(f"YOU WIN! Time: {elapsed:.2f}s", 350, 420, (0, 255, 0))  # Centered, green
        draw_text("Press ENTER to Restart", 350, 370, (255, 255, 255))

def check_game_status(car_pos, road, start_time, game_over, game_win, elapsed_time):
    """Check if the game has been won or lost."""
    # Win check
    last_seg = road[-1]
    end_vec = last_seg.p2
    if math.dist(car_pos, end_vec) < 1.5 and game_win == False:
        game_win = True
        elapsed_time = time.time() - start_time if start_time else 0

    # Game over check using rectangle bounds
    if not check_on_road(car_pos, road):
        game_over = True
        elapsed_time = time.time() - start_time if start_time else 0
        
    return game_over, game_win, elapsed_time

def handle_events(keys, start_time):
    """Handle pygame events and check for game exit."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
    # Start the timer when any movement key is pressed
    if start_time is None and (keys[pygame.K_UP] or keys[pygame.K_DOWN] or 
                              keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
        start_time = time.time()
        
    return start_time

def handle_restart(keys, game_over, game_win, road, sounds, currently_playing, crash_played):
    """Handle game restart if needed."""
    if (game_over or game_win) and keys[pygame.K_RETURN]:
        # Reset game
        car_pos = list(road[0].p2)
        car_speed = 0.0
        car_angle = 0.0
        start_time = None
        game_over = False
        game_win = False
        sounds[currently_playing].stop()
        sounds['engine'].play(-1)
        currently_playing = 'engine'
        crash_played = False
        return True, car_pos, car_speed, car_angle, start_time, game_over, game_win, currently_playing, crash_played
    
    return False, None, None, None, None, game_over, game_win, currently_playing, crash_played

def update_best_time(best_time, game_win, elapsed_time):
    """Update the best time if appropriate."""
    if game_win:
        if best_time == 0 or elapsed_time < best_time:
            return elapsed_time
    return best_time

def run_driving_game(display, Texture_index):
    from OpenGL.GLUT import glutInit
    glutInit()
    global texture_index
    texture_index = Texture_index

    # Setup game components
    car_model, tree_model, grass1_model, grass2_model = load_models()
    road = generate_road()
    scenery = generate_scenery(road, tree_model)
    sounds = setup_audio()
    
    # Start ambient nature sound
    sounds['nature'].play(-1)
    
    # Game state initialization
    clock = pygame.time.Clock()
    car_pos = list(road[0].p2)
    car_speed = 0.0
    car_angle = 0.0
    currently_playing = 'engine'
    sounds['engine'].play(-1)
    horn_playing = False
    crash_played = False
    times = 1
    max_speed = 0.5 * times
    acceleration = 0.1
    brake_force = 0.05
    friction = 0.02
    start_time = None
    elapsed_time = 0
    light_angle = 0
    best_time = 0
    game_over = False
    game_win = False
    last_time = time.time()

    # Main game loop
    while True:
        # Time tracking - calculate real delta time between frames
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Cap dt to avoid physics issues on very slow frames
        dt = min(dt, 0.1)
        
        fps = clock.get_fps()
        pygame.display.set_caption(f"3D Car Driving Game - FPS: {int(fps)}")
        
        # Get keyboard input
        keys = pygame.key.get_pressed()
        
        # Handle events and possible restart
        start_time = handle_events(keys, start_time)
        restart, new_car_pos, new_car_speed, new_car_angle, new_start_time, game_over, game_win, currently_playing, crash_played = (
            handle_restart(keys, game_over, game_win, road, sounds, currently_playing, crash_played)
        )
        
        if restart:
            car_pos, car_speed, car_angle, start_time = new_car_pos, new_car_speed, new_car_angle, new_start_time
            
        # Update car physics - now passing dt
        car_speed, car_angle, car_pos, times, max_speed, acceleration, brake_force, friction, moving_forward, moving_backward = (
            update_car_physics(keys, car_speed, car_angle, car_pos, times, max_speed, 
                              acceleration, brake_force, friction, game_over, game_win, dt)
        )
        
        # Check game status (win/lose)
        game_over, game_win, elapsed_time = check_game_status(
            car_pos, road, start_time, game_over, game_win, elapsed_time
        )
        
        # Update best time if needed
        best_time = update_best_time(best_time, game_win, elapsed_time)
        
        # Handle audio
        currently_playing, horn_playing, crash_played = handle_audio(
            keys, car_speed, moving_forward, moving_backward, 
            game_over, game_win, currently_playing, horn_playing, 
            crash_played, sounds
        )
        
        # Start rendering
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Update camera
        cam_x, cam_z = update_camera(keys, car_pos, car_angle)
        gluLookAt(cam_x, 4, cam_z, car_pos[0], 0, car_pos[1], 0, 1, 0)
        
        # Update lighting - now passing dt
        light_angle = update_lighting(keys, light_angle, dt)
        light_x, light_height, light_z = calculate_light_position(light_angle)
        glLightfv(GL_LIGHT0, GL_POSITION, [light_x, light_height, light_z, 1])
        
        # Draw scene elements
        draw_sun(light_x, light_height, light_z)
        draw_road_and_scenery(road, scenery)
        draw_car(car_pos, car_angle, car_model)
        draw_hud(best_time, car_speed, times, start_time, game_over, game_win, elapsed_time)

        if keys[pygame.K_ESCAPE]:
            return
        
        # Swap buffers
        pygame.display.flip()
        
        # Frame rate control - just for display, doesn't affect physics now
        clock.tick(60)
