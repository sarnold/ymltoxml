"""
Template bits for generating SSG-style controls in YAML.
"""

import re

from .utils import pystache_render

PROFILES = ['LOW', 'MODERATE', 'HIGH', 'PRIVACY']

IMPACT_LVLS = ['low', 'moderate', 'high']

CTL_FIELD_MAP = {
    'id': 'Control Identifier',
    'name': 'Control (or Control Enhancement) Name',
    'notes': 'Discussion',
    'description': 'Control Text',
    'status': 'pending',
    'levels': None,
}

PREAMBLE = '''
policy: NIST
title: Configuration Recommendations for Yocto- and OpenEmbedded-based Linux Variants
id: nist_openembedded
version: Revision 5
source: https://csrc.nist.gov/files/pubs/sp/800/53/r5/upd1/final/docs/sp800-53r5-control-catalog.xlsx
levels:
- id: low
- id: moderate
- id: high
'''

ID_TEMPLATE = '''
controls:
  - id: {{caps}}
    status: {{status}}
    notes: |-
      {{notes}}
    rules: []
    description: |-
      {{description}}
    title: >-
      {{caps}} - {{name}}
    levels: []
'''


def generate_control(context):
    """
    Render an ID template string given a context dict.
    """
    id_yaml = pystache_render(ID_TEMPLATE, context)
    return id_yaml


def xform_id(string, strip_trailing_zeros=False):
    """
    Transform control ID strings, add leading zeros in forward direction:

    AC-12(2) <==> ac-12.02
    """
    if string[0].isupper():
        idp = re.compile(r'[)(-]')  # regex character class id separators
        slist = [x for x in idp.split(string) if x != '']
        if strip_trailing_zeros:
            slist = [x for x in idp.split(string) if x not in ('00', '')]
        slist_with_dots = [slist[0].lower() + f"-{int(slist[1]):02d}"]
        slist_with_dots += [
            f".{s}" if s.isalpha() else f".{int(s):02d}" for s in slist[2:]
        ]
        new_id = ''.join(slist_with_dots)
    else:
        slist = string.upper().split('.')
        slist_with_parens = [slist[0]]
        slist_with_parens += [f"({s.lower()})" for s in slist[1:]]
        new_id = ''.join(slist_with_parens)
    return new_id
