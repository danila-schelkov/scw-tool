import math
from math import *
import mathutils
import os

import requests

from reader import Reader
from lxml.etree import *


class ScwParse(Reader):
    def __init__(self, filedata):
        jointsnames = []
        COLLADA = Element('COLLADA', xmlns='http://www.collada.org/2005/11/COLLADASchema', version='1.4.1')
        SubElement(SubElement(COLLADA, 'asset'), 'up_axis').text = 'Y_UP'
        libImages = SubElement(COLLADA, 'library_images')  # TODO: add support images
        libEffects = SubElement(COLLADA, 'library_effects')  # TODO: add support effects for material
        libMaterials = SubElement(COLLADA, 'library_materials')
        libGeometries = SubElement(COLLADA, 'library_geometries')
        libControllers = SubElement(COLLADA, 'library_controllers')
        libAnimations = SubElement(COLLADA, 'library_animations') 
        libVisualScene = SubElement(COLLADA, 'library_visual_scenes')
        visualScene = SubElement(libVisualScene, "visual_scene", id='Scene', name='Scene')
        libCameras = SubElement(COLLADA, 'library_cameras')  # TODO: add support cameras
        SubElement(SubElement(COLLADA, 'scene'), 'instance_visual_scene', url="#Scene")

        reader = Reader(filedata)
        chunks, i = [], 0
        reader.read(4)
        while i < len(filedata) and filedata[i+8:i+12] != b'WEND':
            chunklen = reader.readInteger(4) + 8
            chunks.append(reader.read(chunklen))
            i += chunklen + 4
        for chunk in chunks:
            reader = Reader(chunk)
            chunkname = reader.read(4).decode('utf-8')
            if chunkname == 'HEAD':
                version = reader.readShort()
                reader.readShort()
                reader.readShort()
                reader.readShort()
                file = reader.readString()
                if file != '':
                    data = requests.get(f'https://game-assets.brawlstarsgame.com/2dfa77ba3448e4e2334430fd54c5b157ae6e4f64/{file}').content
                    fileread = Reader(data)
                    i = 0
                    fileread.read(4)
                    while i < len(filedata) and data[i + 8:i + 12] != b'WEND':
                        chunklen = fileread.readInteger(4) + 8
                        chunks.append(fileread.read(chunklen))
                        i += chunklen + 4
        for chunk in chunks:
            reader = Reader(chunk)
            chunkname = reader.read(4).decode('utf-8')
            if chunkname == 'MATE':
                name = reader.readString()
                SubElement(libMaterials, 'material', id=name)
                shader = reader.readString()
                reader.readUByte()
                if reader.readUByte() == 1:
                    ambienttex = reader.readString()
                else:
                    ambientcolor = reader.read(4)
                if reader.readUByte() == 1:
                    diffusetex = reader.readString()
                else:
                    diffusecolor = reader.read(4)
                if reader.readUByte() == 1:
                    stenciltex = reader.readString()
                else:
                    stencilcolor = reader.read(4)
                texture1 = reader.readString()
                texture2 = reader.readString()
                if reader.readUByte() == 1:
                    colorizetex = reader.readString()
                else:
                    colorizecolor = reader.read(4)
                if reader.readUByte() == 1:
                    emissiontex = reader.readString()
                else:
                    emissioncolor = reader.read(4)
                reader.readString()
                reader.readFloat()
                reader.readFloat()
                lightmapdiffuse = reader.readString()
                lightmapspecular = reader.readString()
                reader.readUByte()  # remaining
            if chunkname == 'GEOM':
                name = reader.readString()
                mesh = SubElement(SubElement(libGeometries, 'geometry', id=f'{name}'), 'mesh')
                parent = reader.readString()
                vertexgroups = reader.readUByte()
                if vertexgroups > 0:
                    vertex = []
                    vertextype = reader.readString()  # POSITION
                    index = reader.readUByte()
                    shortsv = reader.readUShort()
                    scalev = reader.readFloat()
                    countv = reader.readUInt32()
                    source = SubElement(mesh, 'source', id=f'{name}-{vertextype.lower()}')
                    array = SubElement(source, 'float_array', count=f'{countv*3}', id=f'{name}-{vertextype.lower()}-array')
                    array.text = ' '.join([str(x) for x in reader.readVertex(shortsv, scalev, countv)])
                    accessor = SubElement(SubElement(source, 'technique_common'), 'accessor', count=f'{countv}', source=f'#{name}-{vertextype.lower()}-array', stride='3')
                    for param in ['X', 'Y', 'Z']:
                        SubElement(accessor, 'param', name=param, type='float')
                if vertexgroups > 1:
                    vertex = []
                    vertextype = reader.readString()  # NORMAL
                    index = reader.readUByte()
                    shortsvn = reader.readUShort()
                    scalevn = reader.readFloat()
                    countvn = reader.readUInt32()
                    source = SubElement(mesh, 'source', id=f'{name}-{vertextype.lower()}')
                    array = SubElement(source, 'float_array', count=f'{countvn*3}', id=f'{name}-{vertextype.lower()}-array')
                    array.text = ' '.join([str(x) for x in reader.readVertex(shortsvn, scalevn, countvn)])
                    accessor = SubElement(SubElement(source, 'technique_common'), 'accessor', count=f'{countvn}', source=f'#{name}-{vertextype.lower()}-array', stride='3')
                    for param in ['X', 'Y', 'Z']:
                        SubElement(accessor, 'param', name=param, type='float')
                if vertexgroups > 2:
                    vertex = []
                    vertextype = reader.readString()  # TEXCOORD(1)
                    index = reader.readUByte()
                    shortsvt = reader.readUShort()
                    scalevt = reader.readFloat()
                    countvt = reader.readUInt32()
                    vt = reader.readTexCoord(shortsvt, scalevt, countvt)
                    vt[1::2] = [1 - x for x in vt[1::2]]
                    source = SubElement(mesh, 'source', id=f'{name}-{vertextype.lower()}')
                    array = SubElement(source, 'float_array', count=f'{countvt*2}', id=f'{name}-{vertextype.lower()}-array')
                    array.text = ' '.join([str(x) for x in vt])
                    accessor = SubElement(SubElement(source, 'technique_common'), 'accessor', count=f'{countvt}', source=f'#{name}-{vertextype.lower()}-array', stride='2')
                    for param in ['S', 'T']:
                        SubElement(accessor, 'param', name=param, type='float')
                if vertexgroups > 3:
                    vertex = []
                    vertextype = reader.readString()  # TEXCOORD(2) or COLOR(1)
                    index = reader.readUByte()
                    shortsvc = reader.readUShort()
                    scalevc = reader.readFloat()
                    countvc = reader.readUInt32()
                    if vertextype == 'TEXCOORD':
                        reader.readTexCoord(shortsvc, scalevc, countvc)
                    else:
                        reader.readColor(shortsvc, scalevc, countvc)
                if vertexgroups > 4:
                    vertex = []
                    vertextype = reader.readString()  # TEXCOORD(3) or COLOR(2)
                    index = reader.readUByte()
                    shortsvc = reader.readUShort()
                    scalevc = reader.readFloat()
                    countvc = reader.readUInt32()
                    if vertextype == 'TEXCOORD':
                        reader.readTexCoord(shortsvc, scalevc, countvc)
                    else:
                        reader.readColor(shortsvc, scalevc, countvc)
                controller = SubElement(libControllers, 'controller', id=f'{name}-cont')
                skin = SubElement(controller, 'skin', source=f'#{name}')
                if reader.readUByte() == 1:  # bind_shape_matrix
                    bindshape = reader.readMatrix()
                    SubElement(skin, 'bind_shape_matrix').text = ' '.join([str(x) for x in bindshape])
                jointscount = reader.readByte()
                if jointscount > 0:
                    names, matrices = [], []
                    jointsource = SubElement(skin, 'source', id=f'{name}-joints')
                    jointarray = SubElement(jointsource, 'Name_array', id=f'{name}-joints-array', count=f'{jointscount}')
                    matricessource = SubElement(skin, 'source', id=f'{name}-matrices')
                    matricesarray = SubElement(matricessource, 'float_array', id=f'{name}-matrices-array', count=f'{jointscount*16}')
                    accessor = SubElement(SubElement(jointsource, 'technique_common'), 'accessor', source=f'#{name}-joints-array', count=f'{jointscount}', stride='1')
                    SubElement(accessor, 'param', name='JOINT', type='name')
                    accessor = SubElement(SubElement(matricessource, 'technique_common'), 'accessor', source=f'#{name}-matrices-array', count=f'{jointscount}', stride='16')
                    SubElement(accessor, 'param', name='TRANSFORM', type='float4x4')
                    for x1 in range(jointscount):  # JOINTS
                        names.append(reader.readString())  # jointname
                        matrices.append(' '.join([str(x) for x in reader.readMatrix()]))
                    jointarray.text = ' '.join(names)
                    matricesarray.text = ' '.join(matrices)
                    weightssource = SubElement(skin, 'source', id=f'{name}-weights')
                    joints = SubElement(skin, 'joints')
                    SubElement(joints, 'input', semantic='JOINT', source=f'#{name}-joints')
                    SubElement(joints, 'input', semantic='INV_BIND_MATRIX', source=f'#{name}-matrices')
                weightscount = reader.readUInt32()
                if weightscount > 0:
                    weights = []
                    vcount = []
                    data = []
                    for x1 in range(weightscount):  # WEIGHTS
                        vcount.append(0)
                        weight = reader.readWeights()
                        for pair in weight:
                            if pair[0] != 0:
                                vcount[x1] += 1
                                data.append(pair[0])
                                if pair[1]/65535 in weights:
                                    data.append(weights.index(pair[1]/65535))
                                else:
                                    weights.append(pair[1]/65535)
                                    data.append(weights.index(pair[1]/65535))
                    weightsarray = SubElement(weightssource, 'float_array', count=f'{len(weights)}', id=f'{name}-weights-array').text = ' '.join([str(x) for x in weights])
                    accessor = SubElement(SubElement(weightssource, 'technique_common'), 'accessor', count=f'{len(weights)}', source=f'#{name}-weights-array', stride='1')
                    SubElement(accessor, 'param', name='WEIGHT', type='float')
                    vertex_weights = SubElement(skin, 'vertex_weights', count=f'{weightscount}')
                    SubElement(vertex_weights, 'input', semantic='JOINT', source=f'#{name}-joints', offset='0')
                    SubElement(vertex_weights, 'input', semantic='WEIGHT', source=f'#{name}-weights', offset='1')
                    SubElement(vertex_weights, 'vcount').text = ' '.join([str(x) for x in vcount])
                    SubElement(vertex_weights, 'v').text = ' '.join([str(x) for x in data])
                for x1 in range(reader.readUByte()):  # Materials
                    material = reader.readString()
                    file = reader.readString()
                    countf = reader.readUShort()
                    mode1 = reader.readByte()
                    mode2 = reader.readByte()
                    SubElement(SubElement(mesh, 'vertices', id=f'{name}-vertices'), 'input', semantic='POSITION', source=f'#{name}-position')
                    triangles = SubElement(mesh, 'triangles', count=f'{countf}', material=material)
                    if mode1 > 0: SubElement(triangles, 'input', semantic='VERTEX', source=f'#{name}-vertices', offset='0')
                    if mode1 > 1: SubElement(triangles, 'input', semantic='NORMAL', source=f'#{name}-normal', offset='1')
                    if mode1 > 2: SubElement(triangles, 'input', semantic='TEXCOORD', source=f'#{name}-texcoord', offset='2', set='0')
                    p = SubElement(triangles, 'p')
                    poly = []
                    for x2 in range(countf):
                        for x3 in range(3):
                            if mode1 > 0:
                                poly.append(reader.readUShort() if mode2 == 2 else reader.readUByte())  # v
                            if mode1 > 1:
                                poly.append(reader.readUShort() if mode2 == 2 else reader.readUByte())  # vn
                            if mode1 > 2:
                                poly.append(reader.readUShort() if mode2 == 2 else reader.readUByte())  # vt
                            if mode1 > 3:
                                vc = reader.readUShort() if mode2 == 2 else reader.readUByte()
                    p.text = ' '.join([str(x) for x in poly])
            if chunkname == 'NODE':
                for x1 in range(reader.readUShort()):
                    name = reader.readString()
                    parent = reader.readString()
                    hasGEOM = reader.readUShort()
                    if hasGEOM == 1:  # has GEOM
                        node = SubElement(visualScene if parent == '' else visualScene.find(f'.//*[@id="{parent}"]'), 'node', id=name, type='NODE')
                        geomtype = reader.read(4).decode('utf-8')
                        if geomtype == 'CONT':
                            instance_controller = SubElement(node, 'instance_controller', url=f'#{name}-cont')
                            technique_common = SubElement(SubElement(instance_controller, 'bind_material'), 'technique_common')
                        else:
                            instance_controller = SubElement(node, 'instance_controller', url='')
                            technique_common = SubElement(SubElement(instance_controller, 'bind_material'), 'technique_common')
                        geomname = reader.readString()
                        for x2 in range(reader.readUShort()):
                            if geomtype == 'GEOM':
                                symbol = reader.readString()
                                target = reader.readString()
                                SubElement(technique_common, 'instance_material', symbol=symbol, target=f'#{target}')
                            if geomtype == 'CONT':
                                symbol = reader.readString()
                                target = reader.readString()
                                SubElement(technique_common, 'instance_material', symbol=symbol, target=f'#{target}')
                            if geomtype == 'CAME':
                                symbol = reader.readString()
                                target = reader.readString()
                    framescount = reader.readUShort()
                    if hasGEOM == 0:
                        node = SubElement(visualScene if parent == '' else visualScene.find(f'.//*[@id="{parent}"]'), 'node', id=name, type='JOINT' if name.endswith('_s') else 'NODE')
                    if framescount > 0:
                        pos, scale, rot = [], [], []
                        settings = list(bin(reader.readUByte())[2:].zfill(8))
                        for x2 in range(framescount):
                            frameid = reader.readUShort()
                            if settings[7] == '1' or frameid <= 1:
                                x = reader.readInteger(2) / 32512
                                y = reader.readInteger(2) / 32512
                                z = reader.readInteger(2) / 32512
                                w = reader.readInteger(2) / 32512
                                axisfactor = sqrt(x * x + y * y + z * z)
                                angle = 2 * atan2(axisfactor, w)
                                try: xR = x / axisfactor
                                except: xR = 0
                                try: yR = y / axisfactor
                                except: yR = 0
                                try: zR = z / axisfactor
                                except: zR = 0
                                # angle = radians(angle)
                                print(xR, yR, zR, angle, w, name)
                            if settings[4] == '1' or frameid <= 1: xP = reader.readFloat()
                            if settings[5] == '1' or frameid <= 1: yP = reader.readFloat()
                            if settings[6] == '1' or frameid <= 1: zP = reader.readFloat()
                            if settings[1] == '1' or frameid <= 1: xS = reader.readFloat()
                            if settings[2] == '1' or frameid <= 1: yS = reader.readFloat()
                            if settings[3] == '1' or frameid <= 1: zS = reader.readFloat()
                            if frameid <= 1:
                                matrix = mathutils.Matrix.Translation(mathutils.Vector((xP, yP, zP))) @ mathutils.Matrix.Rotation(angle, 4, mathutils.Vector((xR, yR, zR))) @ mathutils.Matrix.Scale(1, 4, mathutils.Vector((xS, yS, zS)))
                                SubElement(node, 'matrix', sid='transform').text = ' '.join([' '.join([str(y) for y in x[:]]) for x in matrix[:]])
                            pos.append((xP, yP, zP))
                            rot.append([angle, (xR, yR, zR)])
                            scale.append((xS, yS, zS))
                        if framescount > 1:
                            animation = SubElement(libAnimations, 'animation', id=f'{name}-anim')
                            inputSource = SubElement(animation, 'source', id=f'{name}-time-input')
                            SubElement(inputSource, 'float_array', id=f'{name}-time-input-array', count=f'{framescount}').text = ' '.join([str((1+x)/30) for x in range(framescount)])
                            accessor = SubElement(SubElement(inputSource, 'technique_common'), 'accessor', source=f'#{name}-time-input-array', count=f'{framescount}', stride='1')
                            SubElement(accessor, 'param', name='TIME', type='float')
                            output = SubElement(animation, 'source', id=f'{name}-matrix-output')
                            SubElement(output, 'float_array', id=f'{name}-matrix-output-array', count=f'{framescount*16}').text = ' '.join([' '.join([' '.join([str(y) for y in x[:]]) for x in (mathutils.Matrix.Translation(mathutils.Vector(pos[frame])) @ mathutils.Matrix.Rotation(rot[frame][0], 4, mathutils.Vector(rot[frame][1])) @ mathutils.Matrix.Scale(1, 4, mathutils.Vector(scale[frame])))[:]]) for frame in range(framescount)])
                            accessor = SubElement(SubElement(output, 'technique_common'), 'accessor', source=f'#{name}-matrix-output-array', count=f'{framescount}', stride='16')
                            SubElement(accessor, 'param', name='TRANSFORM', type='float4x4')
                            interpolationSource = SubElement(animation, 'source', id=f'{name}-interpolation')
                            SubElement(interpolationSource, 'Name_array', id=f'{name}-interpolation-array', count=f'{framescount}').text = ' '.join(['LINEAR' for x in range(framescount)])
                            accessor = SubElement(SubElement(interpolationSource, 'technique_common'), 'accessor', source=f'#{name}-interpolation-array', count=f'{framescount}', stride='1')
                            SubElement(accessor, 'param', name='INTERPOLATION', type='name')
                            sampler = SubElement(animation, 'sampler', id=f'{name}-sampler')
                            SubElement(sampler, 'input', semantic='INPUT', source=f'#{name}-time-input')
                            SubElement(sampler, 'input', semantic='OUTPUT', source=f'#{name}-matrix-output')
                            SubElement(sampler, 'input', semantic='INTERPOLATION', source=f'#{name}-interpolation')
                            SubElement(animation, 'channel', source=f'#{name}-sampler', target=f'{name}/transform')
                            # xS if settings[1] == '1' else '', yS if settings[2] == '1' else '',
                            # zS if settings[3] == '1' else '', xP if settings[4] == '1' else '',
                            # yP if settings[5] == '1' else '', zP if settings[6] == '1' else '',
                            # ' '.join([str(x) for x in [xR, yR, zR, w]]) if settings[7] == '1' else ''
            open(f'dae/{filename[:-4]}.dae', 'wb').write(tostring(ElementTree(COLLADA), pretty_print=True, xml_declaration=True))


for filename in os.listdir('scw/'):
    if filename.endswith('.scw'):
        ScwParse(open(f'scw/{filename}', 'rb').read())
