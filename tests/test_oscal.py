import csv

import pytest
from munch import Munch

import yaml_tools.oscal
from yaml_tools.oscal import csv_row_match, process_data
from yaml_tools.templates import xform_id
from yaml_tools.utils import FileTypeError, StrYAML, text_file_reader

defconfig_str = """\
# comments should be preserved
file_encoding: 'utf-8'
default_ext: '.yaml'
default_content_path: 'ext/oscal-content/nist.gov/SP800-53/rev5'
default_profile_glob: '*resolved-profile_catalog.yaml'
default_profile_name: 'PRIVACY'
default_ssg_glob: 'nist_ocp4.yml'
default_ssg_path: 'ext/content/controls'
default_lookup_key: 'controls'
default_control_attr: 'status'
default_csv_hdr: null
new_csv_hdrs: ['OE expanded', 'Green ID']
csv_delimiter: null
input_format: null
output_format: 'json'
output_path: null
preserve_quotes: true
process_comments: false
mapping: 4
sequence: 6
offset: 4
"""

file_type_err = "FileTypeError: unknown input file extension"

yaml_str = """\
policy: NIST
title: Configuration Recommendations for Yocto- and OpenEmbedded-based Linux Variants
id: nist_openembedded
version: Revision 5
source: https://csrc.nist.gov/files/pubs/sp/800/53/r5/upd1/final/docs/sp800-53r5-control-catalog.xlsx
levels:
- id: low
- id: moderate
- id: high
controls:
- id: AC-11(1)
  status: pending
  notes: |-
    This can be a really long note.
  rules:
  - rule1
  - rule2
  description: |-
    A description of the control.
  title: >-
    AC-11(1) - CONTROL NAME
  levels:
  - high
  - moderate
- id: AC-12
  status: pending
  notes: |-
    Another really long note.
  rules:
  - rule3
  - rule4
  description: |-
    A description of another control.
  title: >-
    AC-12 - ANOTHER CONTROL NAME
  levels:
  - high
  - moderate
"""

args_obj = Munch.fromDict(
    {
        "sort": False,
        "ssg": True,
        "verbose": False,
        "munge": None,
        "quiet": True,
        "attribute": 'rules',
    }
)

testdata = [
    (
        False,
        False,
        False,
        "ID;rules",
    ),
    (
        False,
        False,
        True,
        "Input control IDs",
    ),
]

testdata2 = [
    (
        False,
        True,
        True,
        "test2.yaml",
    ),
    (
        True,
        True,
        True,
        "Normalized input",
    ),
]


def test_csv_row_match():
    file = 'tests/data/controls.csv'
    infile = 'tests/data/OE-expanded-profile-all-ids.txt'

    yaml = StrYAML()
    popts = yaml.load(defconfig_str)

    in_list = text_file_reader(infile, popts)
    in_ids = [xform_id(x) for x in in_list] if in_list[0].isupper() else in_list

    print(in_ids[14])

    reader = csv.reader(open(file, 'r', newline='', encoding='utf-8'))
    headers = next(reader)
    assert len(headers) == 7
    print(headers)

    for ctl in reader:
        # print(len(ctl))
        ctl = csv_row_match(in_ids, ctl)
        print(ctl)
        assert len(ctl) == len(headers) + 2
        assert xform_id(ctl[0]) == ctl[-1]
        # print(len(ctl))


@pytest.mark.parametrize("a,b,c,expected", testdata)
def test_process_data(a, b, c, expected, capfd, tmp_path):
    args_obj.sort = a
    args_obj.ssg = b
    args_obj.verbose = c
    yaml = StrYAML()
    infile = 'tests/data/OE-expanded-profile-ids.txt'
    data_file = tmp_path / "test.yaml"
    data_file.write_text(yaml_str, encoding="utf-8")

    popts = yaml.load(defconfig_str)
    popts['default_content_path'] = tmp_path
    popts['default_profile_glob'] = 'test.yaml'

    process_data(infile, popts, args_obj)
    process_data(infile, popts, args_obj)
    out, err = capfd.readouterr()
    print(out)
    assert expected in out


@pytest.mark.parametrize("a,b,c,expected", testdata2)
def test_process_data_alt(a, b, c, expected, capfd, tmp_path):
    args_obj.sort = a
    args_obj.ssg = b
    args_obj.verbose = c
    args_obj.attribute = 'rules'
    yaml = StrYAML()
    infile = 'tests/data/OE-expanded-profile-ids.txt'
    data_file = tmp_path / "test2.yaml"
    data_file.write_text(yaml_str, encoding="utf-8")

    popts = yaml.load(defconfig_str)
    popts['default_ssg_path'] = tmp_path
    popts['default_ssg_glob'] = 'test2.yaml'

    process_data(infile, popts, args_obj)
    process_data(infile, popts, args_obj)
    out, err = capfd.readouterr()
    print(out)
    assert expected in out


# def test_process_data_munge(capfd, tmp_path):
# args_obj.sort = False
# args_obj.ssg = True
# args_obj.verbose = True
# args_obj.munge = 'tests/data/catalog.csv'
# yaml = StrYAML()
# infile = 'tests/data/OE-expanded-profile-ids.txt'
# data_file = tmp_path / "test3.yaml"
# data_file.write_text(yaml_str, encoding="utf-8")

# popts = yaml.load(defconfig_str)
# popts['default_ssg_path'] = tmp_path
# popts['default_ssg_glob'] = 'test3.yaml'

# process_data(infile, popts, args_obj)
# out, err = capfd.readouterr()
# print(out)


def test_self_test(capfd):
    popts = Munch.fromYAML(defconfig_str)
    assert isinstance(popts, Munch)
    yaml_tools.oscal.self_test(popts)
    out, err = capfd.readouterr()
    print(out)
    assert 'Console tools' in out


def test_self_test_bad_file(capfd):
    yaml = StrYAML()
    cfg_dict = yaml.load(defconfig_str)

    cfg_dict['default_content_path'] = 'bogus/oscal'
    popts = Munch.fromDict(cfg_dict)
    assert isinstance(popts, Munch)
    yaml_tools.oscal.self_test(popts)
    out, err = capfd.readouterr()
    print(out)
    assert 'FileNotFoundError' in out


def test_self_test_bad_cfg(capfd):
    yaml = StrYAML()
    cfg_dict = yaml.load(defconfig_str)

    del cfg_dict['default_content_path']
    popts = Munch.fromDict(cfg_dict)
    yaml_tools.oscal.self_test(popts)
    out, err = capfd.readouterr()
    print(out)
    assert 'missing key' in out
