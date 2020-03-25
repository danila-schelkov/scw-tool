from assets_downloader import Downloader
from reader import Reader
from lxml.etree import *
from math import *
import os


class Matrix:
    def __init__(self, matrix: list = None):
        if matrix is not None:
            self.matrix = matrix
        else:
            pass

    def to_array(self, matrix_object=None):
        return self.matrix if matrix_object is None else matrix_object.matrix

    def __matmul__(self, other):
        if len(self.to_array()) != len(other.to_array()[0]) or len(self.to_array()[0]) != len(other.to_array()):
            print("Матрицы не могут быть перемножены")
        else:
            new_matrix = []
            for z in range(4):
                t = []
                for j in range(4):
                    s = 0
                    for i in range(4):
                        s += self.to_array()[z][i] * other.to_array()[i][j]
                    t.append(s)
                    # [[1, 1, 1, 0],
                    #  [1, 1, 1, 0],
                    #  [1, 1, 1, 0],
                    #  [0, 0, 0, 1]]
                    # [[0, 0, 0, 1],
                    #  [0, 0, 0, 1],
                    #  [0, 0, 0, 1],
                    #  [1, 1, 1, 0]]
                new_matrix.append(t)
            return Matrix(new_matrix)

    def Rotation(self, w: float, axis: tuple):
        x, y, z = axis[0], axis[1], axis[2]

        matrix = [[1-2*y**2-2*z**2, 2*x*y-2*z*w, 2*x*z+2*y*w, 0],
                  [2*x*y+2*z*w, 1-2*x**2-2*z**2, 2*y*z-2*x*w, 0],
                  [2*x*z-2*y*w, 2*y*z+2*x*w, 1-2*x**2-2*y**2, 0],
                  [0, 0, 0, 1]]
        return Matrix(matrix)

    def Translation(self, axis: tuple):
        x, y, z = axis[0], axis[1], axis[2]

        matrix = [[1, 0, 0, x],
                  [0, 1, 0, y],
                  [0, 0, 1, z],
                  [0, 0, 0, 1]]
        return Matrix(matrix)

    def Scale(self, axis: tuple):
        x, y, z = axis[0], axis[1], axis[2]

        matrix = [[x, 0, 0, 0],
                  [0, y, 0, 0],
                  [0, 0, z, 0],
                  [0, 0, 0, 1]]
        return Matrix(matrix)


class ScwReader(Reader):
    def HEAD(self):
        version = self.readShort()
        self.readShort()
        self.readShort()
        self.readShort()
        file = self.readString()
        return version, file

    def MATE(self):
        name = self.readString()
        effect = SubElement(self.library_effects, 'effect', id=f'{name}-effect')
        profile = SubElement(SubElement(effect, 'profile_COMMON'), 'technique', sid='common')
        phong = SubElement(profile, 'phong')
        emission = SubElement(phong, 'emission')
        ambient = SubElement(phong, 'ambient')
        diffuse = SubElement(phong, 'diffuse')
        shader = self.readString()
        self.readUByte()
        if self.readUByte() == 1:
            ambient_tex = self.readString()
            if ambient_tex != '.':
                SubElement(ambient, 'texture', texture=f'{ambient_tex}-sampler')
        else:
            a = self.readUByte() / 255
            r = self.readUByte() / 255
            g = self.readUByte() / 255
            b = self.readUByte() / 255
            SubElement(ambient, 'color').text = f'{r} {g} {b} {a}'
        if self.readUByte() == 1:
            diffuse_tex = self.readString()
            if diffuse_tex != '.':
                SubElement(diffuse, 'texture', texture=f'{diffuse_tex}-sampler')
        else:
            a = self.readUByte() / 255
            r = self.readUByte() / 255
            g = self.readUByte() / 255
            b = self.readUByte() / 255
            SubElement(diffuse, 'color').text = f'{r} {g} {b} {a}'
        if self.readUByte() == 1:
            stencil_tex = self.readString()
        else:
            a = self.readUByte() / 255
            r = self.readUByte() / 255
            g = self.readUByte() / 255
            b = self.readUByte() / 255
        self.readString()
        self.readString()
        if self.readUByte() == 1:
            colorize_tex = self.readString()
        else:
            a = self.readUByte() / 255
            r = self.readUByte() / 255
            g = self.readUByte() / 255
            b = self.readUByte() / 255
        if self.readUByte() == 1:
            emission_tex = self.readString()
            if emission_tex != '.':
                SubElement(emission, 'texture', texture=f'{emission_tex}-sampler')
        else:
            a = self.readUByte() / 255
            r = self.readUByte() / 255
            g = self.readUByte() / 255
            b = self.readUByte() / 255
            SubElement(emission, 'color').text = f'{r} {g} {b} {a}'
        alpha_texture = self.readString()
        self.readFloat()
        self.readFloat()
        lightmap_diffuse = self.readString()
        lightmap_specular = self.readString()
        a = self.readUByte() / 255
        r = self.readUByte()
        g = self.readUByte()
        b = self.readUByte()
        SubElement(SubElement(self.library_materials, 'material', id=name), 'instance_effect', url=f'#{name}-effect')

    def GEOM(self):
        name = self.readString()
        mesh = SubElement(SubElement(self.library_geometries, 'geometry', id=f'{name}'), 'mesh')
        group = self.readString()
        vertex_count = self.readUByte()
        for x in range(vertex_count):
            vertex = []
            vertex_name = self.readString()  # POSITION or NORMAL or TEXCOORD or COLOR
            index = self.readByte()
            stride = self.readUShort()
            scale = self.readFloat()
            count = self.readUInt32()
            for x1 in range(count):
                for x2 in range(stride):
                    vertex.append(self.readShort()*scale/(32767 if vertex_name != 'TEXCOORD' else 32512))
            source = SubElement(mesh, 'source', id=f'{name}-{vertex_name.lower()}')
            array = SubElement(source, 'float_array', id=f'{name}-{vertex_name.lower()}-array', count=f'{len(vertex)}')
            vertex[1::2] = [1-x for x in vertex[1::2]] if vertex_name == 'TEXCOORD' else vertex[1::2]
            array.text = ' '.join([str(v) for v in vertex])
            accessor = SubElement(SubElement(source, 'technique_common'), 'accessor', source=f'#{name}-{vertex_name.lower()}-array', count=f'{count}', stride=f'{stride}')
            for param_name in {'POSITION': ['X', 'Y', 'Z'], 'NORMAL': ['X', 'Y', 'Z'], 'TEXCOORD': ['S', 'T'], 'COLOR': ['R', 'G', 'B', 'A']}[vertex_name]:
                SubElement(accessor, 'param', name=param_name, type='float')
        controller = SubElement(self.library_controllers, 'controller', id=f'{name}-cont')
        skin = SubElement(controller, 'skin', source=f'#{name}')
        if self.readByte() == 1:
            SubElement(skin, 'bind_shape_matrix').text = ' '.join([str(self.readFloat()) for x in range(16)])
        joints_count = self.readByte()
        joints_name = []
        joints_matrix = []
        for x in range(joints_count):
            joint_name = self.readString()
            joints_name.append(joint_name)
            self.joint_names_global.append(joint_name)
            joints_matrix.append([str(self.readFloat()) for x in range(16)])
        joints_matrix = [' '.join(matrix) for matrix in joints_matrix]
        source = SubElement(skin, 'source', id=f'{name}-joints')
        array = SubElement(source, 'Name_array', id=f'{name}-joints-array', count=f'{joints_count}')
        array.text = ' '.join(joints_name)
        accessor = SubElement(SubElement(source, 'technique_common'), 'accessor', source=f'#{name}-joints-array', count=f'{joints_count}', stride='1')
        SubElement(accessor, 'param', name='JOINT', type='name')
        source = SubElement(skin, 'source', id=f'{name}-matrix')
        array = SubElement(source, 'float_array', id=f'{name}-matrix-array', count=f'{len(joints_matrix)}')
        array.text = ' '.join(joints_matrix)
        accessor = SubElement(SubElement(source, 'technique_common'), 'accessor', source=f'#{name}-matrix-array', count=f'{joints_count}', stride='16')
        SubElement(accessor, 'param', name='TRANSFORM', type='float4x4')
        weights_count = self.readUInt32()
        vcount = []
        weights = []
        vertex_weights = []
        for x in range(weights_count):
            vcount.append(0)
            jA = self.readUByte()
            jB = self.readUByte()
            jC = self.readUByte()
            jD = self.readUByte()
            wA = self.readUShort()
            wB = self.readUShort()
            wC = self.readUShort()
            wD = self.readUShort()
            weight = [[jA, wA], [jB, wB], [jC, wC], [jD, wD]]
            for pair in weight:
                if pair[0] != 0:
                    vcount[x] += 1
                    vertex_weights.append(pair[0])
                    if pair[1] not in weights:
                        weights.append(pair[1])
                    vertex_weights.append(weights.index(pair[1]))
        source = SubElement(skin, 'source', id=f'{name}-weight')
        array = SubElement(source, 'float_array', id=f'{name}-weight-array', count=f'{len(weights)}')
        array.text = ' '.join([str(weight/65535) for weight in weights])
        accessor = SubElement(SubElement(source, 'technique_common'), 'accessor', source=f'#{name}-weight-array', count=f'{len(weights)}', stride='1')
        SubElement(accessor, 'param', name='WEIGHT', type='float')
        joints = SubElement(skin, 'joints')
        SubElement(joints, 'input', semantic='JOINT', source=f'#{name}-joints')
        SubElement(joints, 'input', semantic='INV_BIND_MATRIX', source=f'#{name}-matrix')
        v_w = SubElement(skin, 'vertex_weights', count=f'{weights_count}')
        SubElement(v_w, 'input', semantic='JOINT', source=f'#{name}-joints', offset='0')
        SubElement(v_w, 'input', semantic='WEIGHT', source=f'#{name}-weight', offset='1')
        SubElement(v_w, 'vcount').text = ' '.join([str(integer) for integer in vcount])
        SubElement(v_w, 'v').text = ' '.join([str(integer) for integer in vertex_weights])
        materials_count = self.readUByte()
        SubElement(SubElement(mesh, 'vertices', id=f'{name}-vertices'), 'input', semantic='POSITION', source=f'#{name}-position')
        for x in range(materials_count):
            polygones = []
            material_name = self.readString()
            self.readString()
            triangles_count = self.readUShort()
            triangles = SubElement(mesh, 'triangles', material=f'{material_name}', count=f'{triangles_count}')
            mode = [self.readUByte() for x1 in range(2)]
            SubElement(triangles, 'input', semantic='VERTEX', source=f'#{name}-vertices', offset='0')
            if mode[0] > 1: SubElement(triangles, 'input', semantic='NORMAL', source=f'#{name}-normal', offset='1')
            if mode[0] > 2: SubElement(triangles, 'input', semantic='TEXCOORD', source=f'#{name}-texcoord', offset='2', set='0')
            for x1 in range(triangles_count):
                for x2 in range(3):
                    polygones.append(self.readShort() if mode[1] == 2 else self.readByte())  # POSITION
                    if mode[0] > 1:
                        polygones.append(self.readShort() if mode[1] == 2 else self.readByte())  # NORMAL
                        if mode[0] > 2:
                            polygones.append(self.readShort() if mode[1] == 2 else self.readByte())  # TEXCOORD
                            if mode[0] > 3:
                                vc = self.readShort if mode[1] == 2 else self.readByte()
            SubElement(triangles, 'p').text = ' '.join([str(integer) for integer in polygones])

    def CAME(self):
        pass

    def NODE(self):
        nodes_count = self.readUShort()
        for x in range(nodes_count):
            name = self.readString()
            parent = self.readString()
            has_geom = self.readUShort()
            if has_geom == 1:
                node = SubElement(self.visual_scene if parent == '' else self.visual_scene.find(f'.//*[@id="{parent}"]'), 'node', id=name, type='NODE')
                instance_controller = SubElement(node, 'instance_controller', url=f'#{name}-cont')
                technique_common = SubElement(SubElement(instance_controller, 'bind_material'), 'technique_common')
                geom_type = self.read(4).decode('utf-8')
                geom_name = self.readString()
                materials_count = self.readUShort()
                for x1 in range(materials_count):
                    symbol = self.readString()
                    target = self.readString()
                    SubElement(technique_common, 'instance_material', symbol=symbol, target=f'#{target}')
            frames_count = self.readUShort()
            if frames_count >= 1:
                matrixes = []
                times = []
                settings = [int(integer) for integer in list(bin(self.readUByte())[2:].zfill(8))]
                for frame_number in range(frames_count):
                    frame_id = self.readUShort()
                    times.append(frame_id/30)
                    if settings[7] == 1 or frame_number == 0:
                        xR = self.readShort() / 32512
                        yR = self.readShort() / 32512
                        zR = self.readShort() / 32512
                        w = self.readShort() / 32512
                    if settings[4] == 1 or frame_number == 0:
                        xT = self.readFloat()
                    if settings[5] == 1 or frame_number == 0:
                        yT = self.readFloat()
                    if settings[6] == 1 or frame_number == 0:
                        zT = self.readFloat()
                    if settings[1] == 1 or frame_number == 0:
                        xS = self.readFloat()
                    if settings[2] == 1 or frame_number == 0:
                        yS = self.readFloat()
                    if settings[3] == 1 or frame_number == 0:
                        zS = self.readFloat()
                    matrix = (Matrix().Translation((xT, yT, zT)) @ Matrix().Rotation(w, (xR, yR, zR)) @ Matrix().Scale((xS, yS, zS))).to_array()
                    if frame_id == 0:
                        node = SubElement(self.visual_scene if parent == '' else self.visual_scene.find(f'.//*[@id="{parent}"]'), 'node', id=name, type='JOINT' if name in self.joint_names_global else 'NODE')
                        SubElement(node, 'matrix', sid='transform').text = ' '.join([' '.join([str(x1) for x1 in x]) for x in matrix])
                    if frame_id > 0:
                        matrixes.append(' '.join([' '.join([str(x1) for x1 in x]) for x in matrix]))
                if frames_count > 1:
                    animation = SubElement(self.library_animations, 'animation', id=f'{name}-anim')
                    source = SubElement(animation, 'source', id=f'{name}-time')
                    array = SubElement(source, 'float_array', id=f'{name}-time-array', count=f'{frames_count}')
                    array.text = ' '.join([str(floating) for floating in times])
                    accessor = SubElement(SubElement(source, 'technique_common'), 'accessor', source=f'#{name}-time-array', count=f'{frames_count}', stride='1')
                    SubElement(accessor, 'param', name='TIME', type='float')
                    source = SubElement(animation, 'source', id=f'{name}-matrix')
                    array = SubElement(source, 'float_array', id=f'{name}-matrix-array', count=f'{frames_count*16}')
                    array.text = ' '.join(matrixes)
                    accessor = SubElement(SubElement(source, 'technique_common'), 'accessor', source=f'#{name}-matrix-array', count=f'{frames_count}', stride='16')
                    SubElement(accessor, 'param', name='TRANSFORM', type='float4x4')
                    source = SubElement(animation, 'source', id=f'{name}-interpolation')
                    array = SubElement(source, 'Name_array', id=f'{name}-interpolation-array', count=f'{frames_count}')
                    array.text = ' '.join(['LINEAR' for x in range(frames_count)])
                    accessor = SubElement(SubElement(source, 'technique_common'), 'accessor', source=f'#{name}-interpolation-array', count=f'{frames_count}', stride='1')
                    SubElement(accessor, 'param', name='INTERPOLATION', type='name')
                    sampler = SubElement(animation, 'sampler', id=f'{name}-sampler')
                    SubElement(sampler, 'input', semantic='INPUT', source=f'#{name}-time')
                    SubElement(sampler, 'input', semantic='OUTPUT', source=f'#{name}-matrix')
                    SubElement(sampler, 'input', semantic='INTERPOLATION', source=f'#{name}-interpolation')
                    SubElement(animation, 'channel', source=f'#{name}-sampler', target=f'{name}/transform')

    def __init__(self):
        self.joint_names_global = []
        collada = Element('COLLADA', xmlns='http://www.collada.org/2005/11/COLLADASchema', version='1.4.1')
        SubElement(SubElement(collada, 'asset'), 'up_axis').text = 'Y_UP'
        self.library_effects = SubElement(collada, 'library_effects')
        self.library_materials = SubElement(collada, 'library_materials')
        self.library_geometries = SubElement(collada, 'library_geometries')
        self.library_controllers = SubElement(collada, 'library_controllers')
        self.library_animations = SubElement(collada, 'library_animations')
        library_visual_scenes = SubElement(collada, 'library_visual_scenes')
        self.visual_scene = SubElement(library_visual_scenes, 'visual_scene', id='Scene')
        SubElement(SubElement(collada, 'scene'), 'instance_visual_scene', url='#Scene')
        for chunk in chunks:
            super().__init__(chunk)
            chunkname = self.read(4).decode('utf-8')
            if chunkname == 'HEAD':
                self.version, file = self.HEAD()
                filedata = Downloader().get(file)
                chunkreader = Reader(filedata[4:])
                i = 0
                while i < len(filedata) - 4:
                    length = chunkreader.readUInt32() + 8
                    i += length + 4
                    chunks.append(chunkreader.read(length))
            elif chunkname == 'MATE':
                self.MATE()
            elif chunkname == 'GEOM':
                self.GEOM()
            elif chunkname == 'CAME':
                self.CAME()
            elif chunkname == 'NODE':
                self.NODE()
        open(f'dae/{collada_name}', 'wb').write(tostring(collada, pretty_print=True, xml_declaration=True, standalone=True))


if __name__ == '__main__':
    if not os.path.isdir('scw/'):
        os.mkdir('scw/')
    if not os.path.isdir('dae/'):
        os.mkdir('dae/')
    chunks = []
    files = ['8bit_geo.scw', '8bit_win.scw']
    collada_name = files[0][:-4] + '.dae'
    for filename in files:
        filepath = f'scw/{filename}'
        filedata = open(filepath, 'rb').read()
        chunkreader = Reader(filedata[4:])
        i = 0
        while i < len(filedata)-4:
            length = chunkreader.readUInt32() + 8
            i += length + 4
            chunks.append(chunkreader.read(length))
    ScwReader()

