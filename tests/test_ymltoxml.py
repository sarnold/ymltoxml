import pytest

from yaml_tools.utils import FileTypeError, StrYAML
from yaml_tools.ymltoxml import get_input_type, process_inputs

defconfig_str = """\
file_encoding: 'utf-8'
default_xml_ext: '.xml'
default_yml_ext: '.yaml'
process_comments: true
preserve_quotes: true
mapping: 2
sequence: 4
offset: 2
short_empty_elements: false
pretty: true
indent: '  '
"""

file_type_err = "FileTypeError: unknown input file extension"


def test_process_inputs(xml_file, yml_file):
    yaml = StrYAML()
    popts = yaml.load(defconfig_str)

    process_inputs(xml_file, popts)
    process_inputs(yml_file, popts)


def test_process_inputs_debug(xml_file, yml_file):
    yaml = StrYAML()
    popts = yaml.load(defconfig_str)

    process_inputs(xml_file, popts, debug=True)
    process_inputs(yml_file, popts, debug=True)


def test_process_no_comments(xml_file, yml_file):
    yaml = StrYAML()
    popts = yaml.load(defconfig_str)
    popts['process_comments'] = False

    process_inputs(xml_file, popts)
    process_inputs(yml_file, popts)


def test_bad_file(capfd, tmp_path):
    yaml = StrYAML()
    popts = yaml.load(defconfig_str)
    inp2 = tmp_path / "in.ymml"
    inp2.write_text("name: null", encoding="utf-8")

    process_inputs(inp2, popts)
    out, err = capfd.readouterr()
    assert file_type_err in out

    with pytest.raises(FileTypeError):
        get_input_type(inp2, popts)
