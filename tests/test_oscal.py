import pytest
from munch import Munch

import ymltoxml.oscal
from ymltoxml.utils import FileTypeError, StrYAML

defconfig_str = """\
# comments should be preserved
file_encoding: 'utf-8'
default_ext: '.yaml'
default_content_path: 'ext/oscal-content'
default_profile_path: 'nist.gov/SP800-53/rev5'
default_ssg_glob: 'nist_*.yml'
default_ssg_path: 'ext/content/controls'
input_format: null
output_format: 'json'
preserve_quotes: true
process_comments: false
mapping: 4
sequence: 6
offset: 4
"""

file_type_err = "FileTypeError: unknown input file extension"


def test_self_test(capfd):
    popts = Munch.fromYAML(defconfig_str)
    assert isinstance(popts, Munch)
    ymltoxml.oscal.self_test(popts)
    out, err = capfd.readouterr()
    print(out)
    assert 'Console tools' in out


def test_self_test_bad_file(capfd):
    yaml = StrYAML()
    cfg_dict = yaml.load(defconfig_str)

    cfg_dict['default_content_path'] = 'bogus/oscal'
    popts = Munch.fromDict(cfg_dict)
    assert isinstance(popts, Munch)
    ymltoxml.oscal.self_test(popts)
    out, err = capfd.readouterr()
    print(out)
    assert 'FileNotFoundError' in out


def test_self_test_bad_cfg(capfd):
    yaml = StrYAML()
    cfg_dict = yaml.load(defconfig_str)

    del cfg_dict['default_content_path']
    popts = Munch.fromDict(cfg_dict)
    ymltoxml.oscal.self_test(popts)
    out, err = capfd.readouterr()
    print(out)
    assert 'missing key' in out
