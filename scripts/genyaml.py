from pathlib import Path

import xmltodict
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO


class StrYAML(YAML):
    """
    New API likes dumping straight to file/stdout, so we subclass and
    create 'inefficient' custom string dumper.  <shrug>
    """

    def dump(self, data, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()


with open('in.xml', 'r+b') as xfile:
    payload = xmltodict.parse(xfile, process_comments=True)

yaml = StrYAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.preserve_quotes = True  # type: ignore

res = yaml.dump(payload)

Path('out.yaml').write_text(res)
