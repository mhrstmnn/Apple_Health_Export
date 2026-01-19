import os


data_file_path = os.path.join('.', 'data', 'Export.xml')


def get_output_file_path(filename: str, suffix: str, subdirectory_name='') -> str:
    if not subdirectory_name:
        subdirectory_name = suffix
    directory_path = os.path.join('.', 'out', subdirectory_name)
    os.makedirs(directory_path, exist_ok=True)
    return os.path.join(directory_path, filename + '.' + suffix)


def get_argparse_description(output_description: str) -> str:
    return '\n'.join([
        'this is one of two scripts to parse and convert health data after exporting it from Apple\'s Health app:',
        f'this script parses an XML file ("{data_file_path}") and converts it into {output_description}'
    ])
