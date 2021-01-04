import os
import re


def parse(filename: str):
    with open(f'{_from}/{filename}', 'rb') as fh:
        file_data = fh.read()
        fh.close()

    parser = Parser(file_data)

    if _from == 'scw':
        parser.split_chunks()
    parser.parse()

    data = parser.parsed
    del file_data, parser

    return data


def write(filename: str, data):
    writer = Writer()
    writer.write(data)

    writen_data = writer.writen

    del writer

    basename = get_basename(filename)
    export_file_name = f'{basename}.{_to}'
    export_path = f'{_to}/{export_file_name}'

    mode = 'wb'
    if _to in ['dae', 'obj']:
        mode = 'w'
    with open(export_path, mode) as export_file:
        export_file.write(writen_data)
        export_file.close()

        _(f'{export_path} is saved!')


def get_basename(filename: str):
    basename = ''.join(filename.split('.')[:-1])
    return basename


def make_dir(directory_path: str):
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)


def _(*args):
    print('[SCW Tool] ', end='')
    for arg in args:
        print(arg, end=' ')
    print()


def _i(text):
    return input(f'[SCW Tool] {text}: ')


makedir = mkdir = make_dir

tools = [
    'scw2scw',
    'scw2obj',
    'scw2dae',
    'obj2scw',
    'dae2scw',
]

if __name__ == '__main__':
    for tool in tools:
        _(f'{tools.index(tool)} - {tool}')

    # <SelectTool>
    tool_index = None
    while not (tool_index in range(len(tools))):
        tool_index = _i('Select Tool')
        try:
            tool_index = int(tool_index)
        except ValueError:
            _('Prompted Value isn\'t integer!')
    # </SelectTool>

    tool = tools[tool_index]

    _from = tool.split('2')[0]
    _to = tool.split('2')[1]
    mkdir(_from)
    mkdir(_to)

    if _to == 'scw':
        from models_converter.formats.scw import Writer
    elif _to == 'obj':
        from models_converter.formats.obj import Writer
    elif _to == 'dae':
        from models_converter.formats.dae import Writer

    files = [{'filename': file, 'animations': []} for file in os.listdir(_from)]
    if _from == 'scw':
        from models_converter.formats.scw import Parser

        if _to == 'dae':
            animations = []

            for file_index in range(len(files)):
                file = files[file_index]
                filename = file['filename']

                if filename in animations:
                    continue

                basename = get_basename(filename)

                if basename.endswith('_geo'):
                    r = re.compile(f'{basename[:-4]}.*.scw')
                    matches = list(filter(r.match, os.listdir(_from)))
                    matches.remove(filename)

                    if len(matches) >= 1:
                        animations.extend(matches)

                        files[file_index]['animations'] = matches
                        _('Animations detected')

            files = [file for file in files if file['filename'] not in animations]
    elif _from == 'dae':
        from models_converter.formats.dae import Parser
    elif _from == 'obj':
        from models_converter.formats.obj import Parser

    for file in files:
        filename = file['filename']

        parsed_data = parse(filename)

        write(filename, parsed_data)

        if len(file['animations']) > 0:
            geo_group = [node['name'] for node in parsed_data['nodes']
                         if node['parent'] == 'CHARACTER' and node['name'] != 'Root'][0]

            geo_nodes = []
            for node in parsed_data['nodes']:
                if geo_group in [node['name'], node['parent']]:
                    geo_nodes.append(node)

            for animation in file['animations']:
                base_name = get_basename(animation)
                animation_data = parse(animation)

                parsed_data['nodes'] = animation_data['nodes']
                parsed_data['nodes'].extend(geo_nodes)

                write(animation, parsed_data)

    _('Done!')
