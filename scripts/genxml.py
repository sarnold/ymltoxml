from pathlib import Path

import xmltodict
import yaml


def post_process(xml_str):
    """
    Turn comment elements back into xml comments.
    :param xml_str: xml (file) string output from ``unparse``
    """

    s = xml_str
    for r in (("<#comment>", "<!-- "), ("</#comment>", " -->")):
        s = s.replace(*r)
    return s


infile = Path('in.yaml')
with infile.open() as yfile:
    data = yaml.load(yfile, Loader=yaml.Loader)

outfile = Path('out.xml')
xml = xmltodict.unparse(data, short_empty_elements=False, pretty=True, indent='  ')

new_xml = post_process(xml)

with open('out.xml', 'w+') as xfile:
    xfile.write(new_xml)
    xfile.write('\n')
