from pygame.locals import *
from OpenGL.arrays import vbo
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import os
import numpy as np

class OBJ:
    def __init__(self, filename,override_texture=None):
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        self.materials = {}
        self.current_material = None
        self.textures = {}
        self.vbos = {}
        self.override_texture = override_texture
        self.load_model(filename)
        self.build_vbos()
        self.filename = filename

    def build_vbos(self):
        unique_vertex_map = {}
        final_data = {}
        for material, face_group in self.faces:
            if material not in final_data:
                final_data[material] = []

            for v_idx, vt_idx, vn_idx in face_group:
                key = (v_idx, vt_idx, vn_idx)
                if key not in unique_vertex_map:
                    vertex = self.vertices[v_idx]
                    tex = self.texcoords[vt_idx] if vt_idx is not None and vt_idx < len(self.texcoords) else (0.0, 0.0)
                    normal = self.normals[vn_idx] if vn_idx is not None and vn_idx < len(self.normals) else (0.0, 0.0, 0.0)
                    unique_vertex_map[key] = vertex + tex + normal
                final_data[material].append(unique_vertex_map[key])

        for material, vertices in final_data.items():
            flat_data = []
            for v in vertices:
                flat_data.extend(v)
            data_np = np.array(flat_data, dtype=np.float32)
            vbo_id = vbo.VBO(data_np)
            self.vbos[material] = (vbo_id, len(vertices))

    def load_model(self, filename):
        dir_path = os.path.dirname(filename)
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('mtllib'):
                    self.load_mtl(os.path.join(dir_path, line.split()[1]))
                elif line.startswith('usemtl'):
                    self.current_material = line.split()[1]
                elif line.startswith('v '):
                    self.vertices.append(tuple(map(float, line.split()[1:4])))
                elif line.startswith('vn'):
                    self.normals.append(tuple(map(float, line.split()[1:4])))
                elif line.startswith('vt'):
                    self.texcoords.append(tuple(map(float, line.split()[1:3])))
                elif line.startswith('f'):
                    face = []
                    for v in line.strip().split()[1:]:
                        vals = v.split('/')
                        v_idx = int(vals[0]) - 1
                        vt_idx = int(vals[1]) - 1 if len(vals) > 1 and vals[1] else None
                        vn_idx = int(vals[2]) - 1 if len(vals) > 2 and vals[2] else None
                        face.append((v_idx, vt_idx, vn_idx))
                    self.faces.append((self.current_material, face))

    def load_texture(self, image_path):
        if image_path in self.textures:
            return self.textures[image_path]
        try:
            texture_surface = Image.open(image_path).convert('RGB')
            texture_data = texture_surface.tobytes("raw", "RGB", 0, -1)
            width, height = texture_surface.size

            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
            glBindTexture(GL_TEXTURE_2D, 0)

            self.textures[image_path] = texture_id
            return texture_id
        except Exception as e:
            print(f"Failed to load texture {image_path}: {e}")
            return None

    def load_mtl(self, filename):
        current = None
        dir_path = os.path.dirname(filename)
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('newmtl'):
                    current = line.split()[1]
                    self.materials[current] = {'Kd': (1, 1, 1), 'map_Kd': None, 'texture_id': None}
                elif line.startswith('Kd') and current:
                    self.materials[current]['Kd'] = tuple(map(float, line.split()[1:4]))
                elif line.startswith('map_Kd') and current:
                    if self.override_texture and current.lower() == 'main':
                        image_path = self.override_texture
                    else:
                        image_path = line.split(' ', 1)[1].strip().replace('\\', '/').replace(' ', '_')
                    rel_path = os.path.join(dir_path, image_path)
                    self.materials[current]['map_Kd'] = rel_path
                    self.materials[current]['texture_id'] = self.load_texture(rel_path)

    def render(self):
        glEnable(GL_TEXTURE_2D)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        for material, (vbo_id, count) in self.vbos.items():
            mat = self.materials.get(material, {})
            color = mat.get('Kd', (1, 1, 1))
            texture_id = mat.get('texture_id')

            if material and material.lower() == "window":
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glColor4f(*color, 0.4)
            else:
                glColor3fv(color)

            if texture_id:
                glBindTexture(GL_TEXTURE_2D, texture_id)
            else:
                glBindTexture(GL_TEXTURE_2D, 0)

            vbo_id.bind()
            stride = 32  # 3 pos (12) + 2 tex (8) + 3 norm (12)
            glVertexPointer(3, GL_FLOAT, stride, vbo_id)
            glTexCoordPointer(2, GL_FLOAT, stride, vbo_id + 12)
            glNormalPointer(GL_FLOAT, stride, vbo_id + 20)
            glDrawArrays(GL_TRIANGLES, 0, count)
            vbo_id.unbind()

            if material and material.lower() == "window":
                glDisable(GL_BLEND)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisable(GL_TEXTURE_2D)
