"""
Simple consumer test.
"""

from yaml_tools.utils import text_data_writer, text_file_reader

OPTS = {
    'file_encoding': 'utf-8',
    'output_format': 'csv',
    'default_csv_hdr': None,
}


# read in some json "column data"
data = text_file_reader('tests/data/controls.yml', OPTS)
# spit out CSV records
ret = text_data_writer(data, OPTS)
