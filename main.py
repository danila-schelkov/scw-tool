import os
import re

from models_converter.formats.universal import Scene
from models_converter.interfaces import WriterInterface, ParserInterface


def parse(file_name: str) -> Scene:
    with open(f'{_from}/{file_name}', 'rb') as fh:
        file_data = fh.read()
        fh.close()

    parser: ParserInterface = Parser(file_data)
    parser.parse()

    parsed_scene = parser.scene
    del file_data, parser

    return parsed_scene


def write(file_name: str, data):
    writer: WriterInterface = Writer()
    writer.write(data)

    writen_data = writer.writen

    del writer

    export_file_name = f'{get_basename(file_name)}.{_to}'
    export_path = f'{_to}/{export_file_name}'

    mode = 'wb'
    if _to in ('dae', 'obj'):
        mode = 'w'
    with open(export_path, mode) as export_file:
        export_file.write(writen_data)
        export_file.close()

        _(f'{export_path} is saved!')


def get_basename(file_name: str):
    return ''.join(file_name.split('.')[:-1])


def make_dir(directory_path: str):
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)


def _(*args):
    print('[SCW Tool]', *args)


def _i(text):
    return input(f'[SCW Tool] {text}: ')


makedir = mkdir = make_dir

tools = [
    'scw2scw',
    'scw2obj',
    'scw2dae',
    'obj2scw',
    'obj2dae',
    'dae2scw',
    # 'glb2glb',
    'glb2obj',  # BETA feature
    'glb2dae',
]

if __name__ == '__main__':
    for tool in tools:
        _(f'{tools.index(tool)} - {tool}')

    # select tool
    tool_index = None
    while not (tool_index in range(len(tools))):
        tool_index = _i('Select Tool')
        try:
            tool_index = int(tool_index)
        except ValueError:
            _('Prompted Value isn\'t integer!')

    tool = tools[tool_index]

    _from = tool.split('2')[0]
    _to = tool.split('2')[1]
    mkdir(_from)
    mkdir(_to)

    if _to == 'scw':
        from models_converter.formats.scw import Writer
    elif _to == 'obj':
        from models_converter.formats.wavefront import Writer
    elif _to == 'dae':
        from models_converter.formats.collada import Writer
    elif _to == 'glb':
        from models_converter.formats.gltf import Writer

    if _from == 'scw':
        from models_converter.formats.scw import Parser
    elif _from == 'dae':
        from models_converter.formats.collada import Parser
    elif _from == 'obj':
        from models_converter.formats.wavefront import Parser
    elif _from == 'glb':
        from models_converter.formats.gltf import Parser

    files = [{'filename': file, 'animations': []} for file in os.listdir(_from)]
    if _from in ('scw', 'glb') and _to in ('dae', 'glb'):
        animations = []

        for file_index in range(len(files)):
            file = files[file_index]
            filename = file['filename']

            if filename in animations:
                continue

            basename = get_basename(filename)

            if basename.endswith('_geo'):
                r = re.compile(f'{basename[:-4]}.*.{_from}')
                matches = list(filter(r.match, os.listdir(_from)))
                matches.remove(filename)

                for match in matches:
                    match_basename = get_basename(match)

                    if match_basename.endswith('_geo'):
                        r = re.compile(f'{match_basename[:-4]}.*.{_from}')
                        another_matches = list(filter(r.match, os.listdir(_from)))
                        matches = [animation for animation in matches if animation not in another_matches]

                if len(matches) >= 1:
                    animations.extend(matches)

                    files[file_index]['animations'] = matches
                    _(f'Animations for "{filename}" detected')

        files = [file for file in files if file['filename'] not in animations]

    if _to == 'obj':
        files = [file for file in files if file['filename'].endswith('_geo.' + _from)]

    for file in files:
        filename = file['filename']

        scene = parse(filename)

        write(filename, scene)

        if len(file['animations']) > 0:
            nodes_to_remove_names = ['Root']
            node_to_remove_index = 0

            while node_to_remove_index < len(nodes_to_remove_names):
                node_to_remove_name = nodes_to_remove_names[node_to_remove_index]

                node = None
                for node_index in range(len(scene.get_nodes())):
                    node = scene.get_nodes()[node_index]

                    if node.get_name() == node_to_remove_name:
                        break
                if node.get_name() != node_to_remove_name:
                    continue
                for child_node in scene.get_nodes():
                    if child_node.get_parent() == node_to_remove_name:
                        nodes_to_remove_names.append(child_node.get_name())

                scene.get_nodes().remove(node)
                node_to_remove_index += 1

            for animation in file['animations']:
                base_name = get_basename(animation)
                animation_scene = parse(animation)

                scene.get_nodes().extend(animation_scene.get_nodes())

                write(animation, scene)

    _('Done!')
