import os


def get_basename(filename: str):
    filename = filename.split('.')[:-1]
    basename = ''.join(filename)
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

    if _from == 'scw':
        from models_converter.formats.scw import Parser
    elif _to == 'scw':
        from models_converter.formats.scw import Writer

    if _to == 'obj':
        from models_converter.formats.obj_write import Writer
    elif _to == 'dae':
        from models_converter.formats.dae_write import Writer

    if _from == 'dae':
        from models_converter.formats.dae_read import Parser
    elif _from == 'obj':
        from models_converter.formats.obj_read import Parser

    for file in os.listdir(_from):
        with open(f'{_from}/{file}', 'rb') as fh:
            file_data = fh.read()
            fh.close()
        base_name = get_basename(file)

        parser = Parser(file_data)

        if _from == 'scw':
            parser.split_chunks()
        parser.parse()

        parsed_data = parser.parsed
        del file_data, parser

        writer = Writer()
        writer.write(parsed_data)

        writen_data = writer.writen

        del writer

        export_file_name = f'{base_name}.{_to}'
        export_path = f'{_to}/{export_file_name}'

        mode = 'wb'
        if _to in ['dae', 'obj']:
            mode = 'w'
        with open(export_path, mode) as export_file:
            export_file.write(writen_data)
            export_file.close()

            _(f'{export_path} is saved!')

    _('Done!')
