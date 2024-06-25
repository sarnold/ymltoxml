import pytest
from munch import Munch

from yaml_tools.utils import FileTypeError, StrYAML
from yaml_tools.yagrep import process_inputs

defconfig_str = """\
# comments should be preserved
file_encoding: 'utf-8'
default_yml_ext: '.yaml'
default_separator: '/'
input_format: null
output_format: 'json'
csv_delimiter: null
default_csv_hdr: null
preserve_quotes: true
process_comments: false
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

args_obj = Munch.fromDict(
    {
        "get": False,
        "filter": False,
        "text": "foo",
    }
)

testdata = [
    (
        "rules",
        True,
        False,
        "disable_compression",
    ),
    (
        "rules",
        False,
        True,
        "disable_compression",
    ),
    (
        "rules",
        False,
        False,
        "[]",
    ),
]


@pytest.mark.parametrize("a,b,c,expected", testdata)
def test_process_inputs(a, b, c, expected, capfd, tmp_path):
    args_obj.text = a
    args_obj.filter = b
    args_obj.lookup = c
    debug = False
    yaml = StrYAML()
    inp = tmp_path / "in.yml"
    inp.write_text(yaml_str, encoding="utf-8")

    popts = yaml.load(defconfig_str)
    process_inputs(inp, args_obj, popts, debug)
    out, err = capfd.readouterr()
    assert expected in out
    assert "policy" not in out


def test_process_inputs_filter_debug(capfd, tmp_path):
    args_obj.text = "low"
    args_obj.filter = True
    args_obj.lookup = False
    debug = True
    yaml = StrYAML()
    inp = tmp_path / "in.yml"
    inp.write_text(yaml_str, encoding="utf-8")

    popts = yaml.load(defconfig_str)
    popts['output_format'] = 'json'
    process_inputs(inp, args_obj, popts, debug)
    out, err = capfd.readouterr()
    assert "disable_compression" in out
    assert "Searching in" in out


def test_bad_file(capfd, tmp_path):
    args_obj.text = "low"
    yaml = StrYAML()
    popts = yaml.load(defconfig_str)
    inp2 = tmp_path / "in.ymml"
    inp2.write_text(yaml_str, encoding="utf-8")

    process_inputs(inp2, args_obj, popts)
    out, err = capfd.readouterr()
    assert file_type_err in out
