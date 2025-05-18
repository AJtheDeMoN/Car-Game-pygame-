import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from viewer_mode import run_viewer_mode
from driving_game_mode import run_driving_game
from OBJ import OBJ

def initialize_opengl(display):
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glClearColor(0.53, 0.8, 0.95, 1)
    glDisable(GL_CULL_FACE)
    glShadeModel(GL_SMOOTH)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, display[0] / display[1], 0.1, 200.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def main():
    pygame.init()
    display_info = pygame.display.Info()
    display = (display_info.current_w, display_info.current_h)

    pygame.display.set_mode(display, DOUBLEBUF | OPENGL | FULLSCREEN)
    pygame.display.set_caption("3D Car Project")

    initialize_opengl(display)

    while True:
        texture_index = run_viewer_mode(display)
        if texture_index == 0:
            break
        run_driving_game(display, texture_index)

if __name__ == "__main__":
    main()
    pygame.quit()
    quit()