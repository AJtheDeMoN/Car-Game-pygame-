from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math 

class RoadSegment:
    def __init__(self, p1, p2, width=4.0):
        self.p1 = p1  # (x, z)
        self.p2 = p2
        self.width = width

    def get_side_vertices(self):
        x1, z1 = self.p1
        x2, z2 = self.p2

        dx = z2 - z1
        dz = x1 - x2
        length = math.sqrt(dx**2 + dz**2)
        dx = dx / length * self.width / 2
        dz = dz / length * self.width / 2

        # Return left and right side vertices of the road
        return {
            "left1": (x1 - dx, z1 - dz),
            "right1": (x1 + dx, z1 + dz),
            "left2": (x2 - dx, z2 - dz),
            "right2": (x2 + dx, z2 + dz)
        }

    def draw(self):
        x1, z1 = self.p1
        x2, z2 = self.p2

        # Correct direction vector
        dx = x2 - x1
        dz = z2 - z1
        length = math.sqrt(dx**2 + dz**2)
        dx /= length
        dz /= length

        # Perpendicular (normal) vector for width
        perp_x = -dz
        perp_z = dx

        half_width = self.width / 2

        # Road corners
        left1 = (x1 + perp_x * -half_width, z1 + perp_z * -half_width)
        right1 = (x1 + perp_x * half_width, z1 + perp_z * half_width)
        left2 = (x2 + perp_x * -half_width, z2 + perp_z * -half_width)
        right2 = (x2 + perp_x * half_width, z2 + perp_z * half_width)

        # Draw road
        glColor3f(0.40, 0.25, 0.13)
        glBegin(GL_QUADS)
        glVertex3f(left1[0], 0, left1[1])
        glVertex3f(right1[0], 0, right1[1])
        glVertex3f(right2[0], 0, right2[1])
        glVertex3f(left2[0], 0, left2[1])
        glEnd()

    def draw_connection(self, next_segment):
        this_vertices = self.get_side_vertices()
        next_vertices = next_segment.get_side_vertices()

        y = 0  # Same height as road

        # Left edge patch
        glColor3f(0.40, 0.25, 0.13)
        glBegin(GL_QUADS)
        glVertex3f(this_vertices["left2"][0], y, this_vertices["left2"][1])
        glVertex3f(next_vertices["left1"][0], y, next_vertices["left1"][1])
        glVertex3f(next_vertices["right1"][0], y, next_vertices["right1"][1])
        glVertex3f(this_vertices["right2"][0], y, this_vertices["right2"][1])
        glEnd()

    def get_grass_vertices(self):
        x1, z1 = self.p1
        x2, z2 = self.p2

        dx = x2 - x1
        dz = z2 - z1
        length = math.sqrt(dx**2 + dz**2)
        dx /= length
        dz /= length

        # Perpendicular vector
        perp_x = -dz
        perp_z = dx
        grass_offset = self.width / 2 + 15.0

        return {
            "outer_left1": (x1 - perp_x * grass_offset, z1 - perp_z * grass_offset),
            "outer_right1": (x1 + perp_x * grass_offset, z1 + perp_z * grass_offset),
            "outer_left2": (x2 - perp_x * grass_offset, z2 - perp_z * grass_offset),
            "outer_right2": (x2 + perp_x * grass_offset, z2 + perp_z * grass_offset)
        }


    def draw_grass_strip(self):
        x1, z1 = self.p1
        x2, z2 = self.p2

        dx = x2 - x1
        dz = z2 - z1
        length = math.sqrt(dx**2 + dz**2)
        dx /= length
        dz /= length

        perp_x = -dz
        perp_z = dx

        grass_offset = self.width / 2 + 15.0
        y = -0.01  # Slightly below the road

        left1 = (x1 + perp_x * -grass_offset, z1 + perp_z * -grass_offset)
        right1 = (x1 + perp_x * grass_offset, z1 + perp_z * grass_offset)
        left2 = (x2 + perp_x * -grass_offset, z2 + perp_z * -grass_offset)
        right2 = (x2 + perp_x * grass_offset, z2 + perp_z * grass_offset)

        glColor3f(0.3, 0.8, 0.2)
        glBegin(GL_QUADS)
        glVertex3f(left1[0], y, left1[1])
        glVertex3f(right1[0], y, right1[1])
        glVertex3f(right2[0], y, right2[1])
        glVertex3f(left2[0], y, left2[1])
        glEnd()

    def draw_grass_connection(self, next_segment):
        y = -0.01  # Same grass height

        current = self.get_grass_vertices()
        nxt = next_segment.get_grass_vertices()

        glColor3f(0.3, 0.8, 0.2)
        
        # Left grass seam
        glBegin(GL_QUADS)
        glVertex3f(current["outer_left2"][0], y, current["outer_left2"][1])
        glVertex3f(nxt["outer_left1"][0], y, nxt["outer_left1"][1])
        glVertex3f(nxt["outer_right1"][0], y, nxt["outer_right1"][1])
        glVertex3f(current["outer_right2"][0], y, current["outer_right2"][1])
        glEnd()
