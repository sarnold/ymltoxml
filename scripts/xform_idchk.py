"""
Simple consumer test.
"""

from natsort import os_sorted

from yaml_tools.templates import xform_id
from yaml_tools.utils import text_file_reader

OPTS = {
    'file_encoding': 'utf-8',
    'output_format': 'raw',
    'default_csv_hdr': None,
}

# read in some json "column data"
data = text_file_reader('tests/data/OE-expanded-profile-all-ids.txt', OPTS)
if data[0].isupper():
    lc_ids = [xform_id(x) for x in data]

# spit out lowercase id format
for ctl in os_sorted(lc_ids):
    print(ctl)
