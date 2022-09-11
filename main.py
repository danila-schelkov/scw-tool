import os

from models_converter.formats.universal import Scene
from models_converter.interfaces import WriterInterface, ParserInterface


TOOLS = (
    'scw2scw',
    'scw2obj',
    'scw2dae',
    'obj2scw',
    'obj2dae',
    'dae2scw',
    # 'glb2glb',
    'glb2obj',  # BETA feature
    'glb2dae',
)


def _(*args):
    print('[SCW Tool]', *args)


def _i(text):
    return input(f'[SCW Tool] {text}: ')


def parse(parser_class: type(ParserInterface), format_name: str, filename: str) -> Scene:
    with open(f'{format_name}/{filename}', 'rb') as fh:
        file_data = fh.read()
        fh.close()

    parser: ParserInterface = parser_class(file_data)
    parser.parse()

    parsed_scene = parser.scene
    del file_data, parser

    return parsed_scene


def write(writer_class: type(WriterInterface), format_name: str, filename: str, scene: Scene):
    writer: WriterInterface = writer_class()
    writer.write(scene)

    writen_data = writer.writen

    del writer

    export_file_name = f'{os.path.splitext(filename)[0]}.{format_name}'
    export_path = f'{format_name}/{export_file_name}'

    mode = 'wb'
    if format_name in ('dae', 'obj'):
        mode = 'w'
    with open(export_path, mode) as export_file:
        export_file.write(writen_data)
        export_file.close()

        _(f'{export_path} is saved!')


def get_parser_class(format_name: str) -> type(ParserInterface):
    if format_name == 'scw':
        from models_converter.formats.scw import Parser
    elif format_name == 'dae':
        from models_converter.formats.collada import Parser
    elif format_name == 'obj':
        from models_converter.formats.wavefront import Parser
    elif format_name == 'glb':
        from models_converter.formats.gltf import Parser
    else:
        raise TypeError('Unsupported format: ' + format_name)

    return Parser


def get_writer_class(format_name: str) -> type(WriterInterface):
    if format_name == 'scw':
        from models_converter.formats.scw import Writer
    elif format_name == 'obj':
        from models_converter.formats.wavefront import Writer
    elif format_name == 'dae':
        from models_converter.formats.collada import Writer
    elif format_name == 'glb':
        from models_converter.formats.gltf import Writer
    else:
        raise TypeError('Unsupported format: ' + format_name)

    return Writer


def print_tools() -> None:
    """Prints tools in format 'index - tool_name'.

    :return:
    """
    for tool in TOOLS:
        _(f'{TOOLS.index(tool)} - {tool}')


def select_tool() -> str:
    """Runs infinite loop to select tool.

    :return: selected tool name
    """

    tool_index = None
    while not (tool_index in range(len(TOOLS))):
        tool_index = _i('Select tool')
        try:
            tool_index = int(tool_index)
        except ValueError:
            _('Prompted Value isn\'t integer!')

    return TOOLS[tool_index]


def collect_files_info(_from: str, _to: str) -> list:
    import re

    files = [{'filename': file, 'animations': []} for file in os.listdir(_from)]
    if _from in ('scw', 'glb') and _to in ('dae', 'glb', 'obj'):
        animations = []

        for file_index in range(len(files)):
            file = files[file_index]
            filename = file['filename']

            if filename in animations:
                continue

            basename = os.path.splitext(filename)[0]

            if basename.endswith('_geo'):
                r = re.compile(f'{basename[:-4]}.*.{_from}')
                matches = list(filter(r.match, os.listdir(_from)))
                matches.remove(filename)

                for match in matches:
                    match_basename = os.path.splitext(match)[0]

                    if match_basename.endswith('_geo'):
                        r = re.compile(f'{match_basename[:-4]}.*.{_from}')
                        another_matches = list(filter(r.match, os.listdir(_from)))
                        matches = [animation for animation in matches if animation not in another_matches]

                if len(matches) >= 1:
                    animations.extend(matches)

                    files[file_index]['animations'] = matches
                    _(f'Animations for "{filename}" detected')

        files = [
            file for file in files
            if file['filename'] not in animations
        ]

    if _to == 'obj':
        files = [
            {'filename': file['filename'], 'animations': []} for file in files
        ]

    return files


def main() -> None:
    print_tools()
    tool = select_tool()

    _from, _to = tool.split('2')
    os.makedirs(_from, exist_ok=True)
    os.makedirs(_to, exist_ok=True)

    parser_class = get_parser_class(_from)
    writer_class = get_writer_class(_to)

    files = collect_files_info(_from, _to)

    for file in files:
        filename = file['filename']

        scene = parse(parser_class, _from, filename)

        write(writer_class, _to, filename, scene)

        if len(file['animations']) > 0:
            for animation_filename in file['animations']:
                animation_scene = parse(parser_class, _from, animation_filename)
                scene.import_nodes(animation_scene)

                write(writer_class, _to, animation_filename, scene)

    _('Done!')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
