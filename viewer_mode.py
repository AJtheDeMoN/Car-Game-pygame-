import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import math 
import random
import pygame.mixer
import pygame.freetype
from OBJ import OBJ

pygame.init()
global font
font = pygame.freetype.SysFont("Arial", 24)

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

def draw_text(text, x, y, color=(255, 255, 255)):
    """Draw 2D text on screen."""
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

def draw_circular_base():
    """Draw the ground as a circular green base."""
    glDisable(GL_LIGHTING)
    glColor3f(0.2, 0.9, 0.3)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, -0.01, 0)
    for angle in range(0, 361, 5):
        x = 25 * math.cos(math.radians(angle))
        z = 25 * math.sin(math.radians(angle))
        glVertex3f(x, -0.01, z)
    glEnd()
    glEnable(GL_LIGHTING)

def initialize_opengl(display):
    """Setup initial OpenGL state."""
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    setup_lighting()
    glClearColor(0.53, 0.8, 0.95, 1)
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)
    glShadeModel(GL_SMOOTH)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, display[0] / display[1], 0.1, 200.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def load_models(texture_index=1):
    """Load 3D models and return them."""
    car_obj = OBJ('OBJs/car.obj', override_texture=f"textures/texture{texture_index}.png")
    tree_model = OBJ('OBJs/tree.obj')
    grass1_model = OBJ('OBJs/grass1.obj')
    grass2_model = OBJ('OBJs/grass2.obj')
    
    return car_obj, tree_model, grass1_model, grass2_model

def create_display_lists(tree_model, grass1_model, grass2_model):
    """Create OpenGL display lists for models."""
    # Tree display list
    tree_display_list = glGenLists(1)
    glNewList(tree_display_list, GL_COMPILE)
    tree_model.render()
    glEndList()

    # Grass display lists
    grass1_display_list = glGenLists(1)
    glNewList(grass1_display_list, GL_COMPILE)
    grass1_model.render()
    glEndList()

    grass2_display_list = glGenLists(1)
    glNewList(grass2_display_list, GL_COMPILE)
    grass2_model.render()
    glEndList()
    
    return tree_display_list, grass1_display_list, grass2_display_list

def setup_audio():
    """Initialize and start audio playback."""
    pygame.mixer.pre_init(44100, -16, 2, 2048)  # Pre-initialize mixer
    pygame.mixer.init()

    # Load and start background music
    pygame.mixer.music.load("audio/nature.mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)

    # Load engine sound
    engine_sound = pygame.mixer.Sound("audio/engine.mp3")
    engine_sound.set_volume(0.6)
    engine_channel = pygame.mixer.Channel(1)
    engine_channel.play(engine_sound, -1)

def generate_tree_positions(count=30, min_radius=5, max_radius=21, min_distance=2.5):
    """Generate random positions for trees."""
    object_positions = []
    tree_positions = []
    
    while len(tree_positions) < count:
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(min_radius, max_radius)
        x, z = radius * math.cos(angle), radius * math.sin(angle)
        
        if all(math.hypot(x - ox, z - oz) > min_distance for ox, oz in object_positions):
            tree_positions.append((x, z))
            object_positions.append((x, z))
            
    return tree_positions, object_positions

def generate_grass_positions(
    count=250, min_radius=3, max_radius=21, min_distance=1.5, 
    object_positions=None, grass_models=None
):
    """Generate random positions for grass objects."""
    if object_positions is None:
        object_positions = []
    
    grass_objects = []
    while len(grass_objects) < count:
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(min_radius, max_radius)
        x, z = radius * math.cos(angle), radius * math.sin(angle)
        
        if all(math.hypot(x - ox, z - oz) > min_distance for ox, oz in object_positions):
            model = random.choice(grass_models)
            grass_objects.append((x, z, model))
            object_positions.append((x, z))
            
    return grass_objects

def handle_events(rotation, mouse_down, last_mouse_pos, zoom_radius, texture_index, car_obj):
    """Process pygame events and return updated state."""
    next_window = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_down = True
            last_mouse_pos = pygame.mouse.get_pos()
            
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_down = False
            
        elif event.type == pygame.MOUSEMOTION and mouse_down:
            x, y = pygame.mouse.get_pos()
            dx, dy = x - last_mouse_pos[0], y - last_mouse_pos[1]
            rotation[0] += dx * 0.3
            rotation[1] = max(-89, min(89, rotation[1] + dy * 0.3))
            last_mouse_pos = (x, y)
            
        elif event.type == pygame.MOUSEWHEEL:
            zoom_radius -= event.y * 0.8
            zoom_radius = max(5, min(50, zoom_radius))
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                texture_index = (texture_index % 5) + 1
                car_obj = OBJ('OBJs/car.obj', override_texture=f"textures/texture{texture_index}.png")
                
            elif event.key == pygame.K_LEFT:
                texture_index = 5 if texture_index == 1 else texture_index - 1
                car_obj = OBJ('OBJs/car.obj', override_texture=f"textures/texture{texture_index}.png")
                
            elif event.key == pygame.K_RETURN:
                next_window = True
            
            elif event.key == pygame.K_ESCAPE:
                next_window = True
                texture_index = 0
                
    return rotation, mouse_down, last_mouse_pos, zoom_radius, texture_index, car_obj, next_window

def update_camera(rotation, zoom_radius):
    """Calculate camera position based on rotation and zoom."""
    rot_x_rad = math.radians(rotation[0])
    rot_y_rad = math.radians(rotation[1])
    cos_y = math.cos(rot_y_rad)
    
    camX = -zoom_radius * math.sin(rot_x_rad) * cos_y
    camY = zoom_radius * math.sin(rot_y_rad)
    camZ = zoom_radius * math.cos(rot_x_rad) * cos_y
    
    return camX, camY, camZ

def update_lighting(light_angle):
    """Update the light position based on angle."""
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        light_angle = (light_angle + 2.0) % 360.0
    if keys[pygame.K_e]:
        light_angle = (light_angle - 2.0) % 360.0

    light_radius = 100.0
    light_height = 100.0
    light_x = math.sin(math.radians(light_angle)) * light_radius
    light_z = math.cos(math.radians(light_angle)) * light_radius
    
    glPushMatrix()
    glLoadIdentity()
    glLightfv(GL_LIGHT0, GL_POSITION, [light_x, light_height, light_z, 1])
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, [0.0, -1.0, 0.0])
    glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 90.0)
    glPopMatrix()
    
    return light_angle

def render_scene(car_obj, tree_positions, grass_objects, tree_display_list, camY):
    """Render all scene elements."""
    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Ground
    if camY >= 0:
        draw_circular_base()

    # Car
    car_obj.render()

    # Trees
    for x, z in tree_positions:
        glPushMatrix()
        glTranslatef(x, -0.01, z)
        glScalef(0.2, 0.2, 0.2)
        glCallList(tree_display_list)
        glPopMatrix()

    # Grass
    for x, z, model in grass_objects:
        glPushMatrix()
        glTranslatef(x, -0.01, z)
        glScalef(0.5, 0.5, 0.5)
        glCallList(model)
        glPopMatrix()

    # Draw title/instruction near top center
    draw_text("Press Left/Right Arrow to change car texture, Enter to start the game", 200, 750, (255, 255, 255))

    # Individual control instructions (one per line, top-left corner)
    instructions = [
        "Click R/F to control speed",
        "Q/E to control sunlight direction",
        "A/W/D to control camera angle",
        "ESC to return to the main menu",
        "ESC in the main menu to quit",
        "INSTRUCTIONS:",
    ]

    start_y = 20   # Top of the screen
    line_spacing = 25
    x = 20         # Left side padding

    for i, instruction in enumerate(instructions):
        draw_text(instruction, x, start_y + i * line_spacing, (255, 255, 255))



def run_viewer_mode(display):
    print("Running viewer mode...")
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    initialize_opengl(display)
    setup_lighting()

    texture_index = 1
    car_obj, tree_model, grass1_model, grass2_model = load_models(texture_index)
    
    tree_display_list, grass1_display_list, grass2_display_list = create_display_lists(
        tree_model, grass1_model, grass2_model
    )
    
    setup_audio()
    
    # Generate scene objects
    tree_positions, object_positions = generate_tree_positions()
    grass_models = [grass1_display_list, grass2_display_list]
    grass_objects = generate_grass_positions(
        object_positions=object_positions, 
        grass_models=grass_models
    )
    
    # Game state
    clock = pygame.time.Clock()
    rotation = [0, 20]
    mouse_down = False
    last_mouse_pos = (0, 0)
    zoom_radius = 12
    light_angle = 0.0

    # Main loop
    while True:
        dt = clock.tick(60) / 1000.0
        fps = clock.get_fps()
        pygame.display.set_caption(f"3D Car Viewer - FPS: {int(fps)}")

        # Handle input
        rotation, mouse_down, last_mouse_pos, zoom_radius, texture_index, car_obj, next_window = handle_events(
            rotation, mouse_down, last_mouse_pos, zoom_radius, texture_index, car_obj
        )

        if next_window:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            return texture_index

        # Update camera
        camX, camY, camZ = update_camera(rotation, zoom_radius)
        
        # Setup view
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(camX, camY, camZ, 0, 0, 0, 0, 1, 0)

        # Update lighting
        light_angle = update_lighting(light_angle)
        
        # Render everything
        render_scene(car_obj, tree_positions, grass_objects, tree_display_list, camY)

        # Swap buffers
        pygame.display.flip()
