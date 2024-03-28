import json
import sys
from difflib import SequenceMatcher as SM
from pathlib import Path

import pytest
from munch import Munch

from ymltoxml import utils
from ymltoxml.templates import ID_TEMPLATE, generate_control, xform_id
from ymltoxml.utils import (
    FileTypeError,
    StrYAML,
    get_cachedir,
    get_filelist,
    load_config,
    pystache_render,
    text_data_writer,
    text_file_reader,
)

# from pystache import Renderer, TemplateSpec


defconfig_str = """\
# comments should be preserved
file_encoding: 'utf-8'
default_ext: '.yaml'
default_separator: '/'
default_oscal_path: 'ext/oscal-content'
default_profile_path: 'nist.gov/SP800-53/rev5'
input_format: null
output_format: 'json'
preserve_quotes: true
process_comments: true
mapping: 4
sequence: 6
offset: 4
"""

file_type_err = "FileTypeError: unknown input file extension"

yaml_str = """\
policy: Security Requirements Guide - General Purpose Operating System
title: Security Requirements Guide - General Purpose Operating System
id: srg_gpos
version: 'v2r3'
source: https://public.cyber.mil/stigs/downloads/
controls_dir: srg_gpos
levels:
- id: high
- id: medium
- id: low
controls:  # sequences can have nodes that are mappings
    -   id: Variables
        levels:
            - high
            - medium
            - low
        title: Variables
        rules:
            - var_sshd_disable_compression=no  # this should be last
            - var_password_hashing_algorithm=SHA512
            - var_password_pam_dictcheck=1
            - sshd_approved_macs=stig
            - sshd_approved_ciphers=stig
            - sshd_idle_timeout_value=10_minutes
            - var_accounts_authorized_local_users_regex=rhel8
            - var_account_disable_post_pw_expiration=35
            - var_auditd_action_mail_acct=root
            - var_auditd_space_left_percentage=25pc
            - var_auditd_space_left_action=email
            - login_banner_text=dod_banners  # this should be first
            - var_authselect_profile=sssd
"""


def test_data_writer(capfd):
    yaml = StrYAML()
    popts = yaml.load(defconfig_str)
    data = yaml.load(yaml_str)
    assert isinstance(data, dict)

    text_data_writer(data, popts)
    out, err = capfd.readouterr()
    assert json.loads(out)

    popts['output_format'] = 'yaml'
    text_data_writer(data, popts)
    out, err = capfd.readouterr()
    assert yaml.load(out) == data

    popts['output_format'] = 'raw'
    text_data_writer(data, popts)
    out, err = capfd.readouterr()
    assert isinstance(out, str)
    assert out.startswith("{'policy': 'Security Requirements Guide")
    print(len(out))


def test_file_reader(capfd, tmp_path):
    yaml = StrYAML()
    popts = yaml.load(defconfig_str)
    popts['process_comments'] = False

    test_files = [
        'tests/data/catalog.csv',
        'tests/data/catalog.json',
        'tests/data/catalog.yaml',
        'tests/data/OE-expanded-profile-ids.txt',
    ]
    file_data = []

    for file in test_files:
        out = text_file_reader(file, popts)
        assert isinstance(out, list)
        assert len(out) is 15 or 49
        file_data.append(out)

    # similarity ratio measure is a float in the range [0, 1]
    sim_01 = SM(None, str(file_data[0]), str(file_data[1])).ratio()
    print(sim_01)
    assert sim_01 > 0.999
    sim_12 = SM(None, str(file_data[1]), str(file_data[2])).ratio()
    print(sim_12)
    assert sim_12 > 0.999


def test_file_reader_raises(capfd, tmp_path):
    yaml = StrYAML()
    popts = yaml.load(defconfig_str)
    inp2 = tmp_path / "in.ymml"
    inp2.write_text(yaml_str, encoding="utf-8")

    with pytest.raises(FileTypeError):
        text_file_reader(inp2, popts)


def test_get_cachedir():
    test_dir = 'test_cache'
    dir1 = get_cachedir()
    assert dir1.endswith('yml_cache')
    dir2 = get_cachedir(test_dir)
    assert dir2.endswith('test_cache')


def test_get_filelist():
    test_path = Path('docs') / 'source' / 'index.rst'
    files = get_filelist('docs/source', '*.rst')
    assert isinstance(files, list)
    assert len(files) == 6
    assert str(test_path) in files


def test_get_filelist_debug():
    test_path = Path('docs') / 'source' / 'index.rst'
    files = get_filelist('docs/source', '*.rst', debug=True)
    assert isinstance(files, list)
    assert len(files) == 6
    assert str(test_path) in files


def test_gen_control():
    yaml = StrYAML()
    popts = yaml.load(defconfig_str)
    ctx = {
        'caps': 'AC-1',
        'status': 'pending',
        'notes': 'A note.',
        'rules_list': [],
        'description': 'Describe something.',
        'name': 'A control name.',
        'levels_list': [],
    }
    out = generate_control(ctx)
    print(out)
    assert 'pending' in out

    back_in = yaml.load(out)
    print(back_in[0])


def test_render_simple():
    """
    Test rendering pystache template.
    """
    simple_tpl = """Hi {{thing}}!"""
    actual = pystache_render(simple_tpl, {'thing': 'pizza'})
    assert actual == 'Hi pizza!'


def test_str_dumper():
    my_yaml = StrYAML()
    assert isinstance(my_yaml, StrYAML)
    assert hasattr(my_yaml, 'dump')


def test_xform_id():
    doc_ids = ['AC-1', 'AC-2(11)', 'AC-2(11)(a)', 'AC-05(02)(a)(01)']
    sort_ids = ['ac-1', 'ac-2.11', 'ac-2.11.a', 'ac-05.02.a.01']
    print("")
    for x, y in zip(doc_ids, sort_ids):
        print(xform_id(x), y)
        assert xform_id(x) == y
        assert xform_id(y) == x


def test_load_debug_config():
    popts, pfile = load_config(debug=True)

    assert isinstance(pfile, Path)
    assert isinstance(popts, Munch)
    assert hasattr(popts, 'default_xml_ext')
    assert pfile.stem == 'ymltoxml' or '.ymltoxml'


def test_load_ymltoxml_config():
    popts, pfile = load_config()

    assert isinstance(pfile, Path)
    assert isinstance(popts, Munch)
    assert hasattr(popts, 'default_xml_ext')
    assert pfile.stem == 'ymltoxml' or '.ymltoxml'


def test_load_yasort_config():
    popts, pfile = load_config('yasort')

    assert isinstance(pfile, Path)
    assert isinstance(popts, Munch)
    assert hasattr(popts, 'has_parent_key')
    assert pfile.stem == 'yasort' or '.yasort'


def test_load_yagrep_config():
    popts, pfile = load_config('yagrep')

    assert isinstance(pfile, Path)
    assert isinstance(popts, Munch)
    assert hasattr(popts, 'default_separator')
    assert pfile.stem == 'yagrep' or '.yagrep'


def test_load_oscal_config():
    popts, pfile = load_config('oscal')

    assert isinstance(pfile, Path)
    assert isinstance(popts, Munch)
    assert hasattr(popts, 'default_ssg_path')
    assert pfile.stem == 'oscal' or '.oscal'
