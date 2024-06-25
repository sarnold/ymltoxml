import pytest

from yaml_tools.utils import FileTypeError, StrYAML
from yaml_tools.yasort import get_input_yaml, process_inputs

defconfig_str = """\
# comments should be preserved
file_encoding: 'utf-8'
default_yml_ext: '.yaml'
output_dirname: 'sorted-out'
default_parent_key: 'controls'
default_sort_key: 'rules'
has_parent_key: true
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


def test_process_inputs(tmp_path):
    yaml = StrYAML()
    d = tmp_path / "out"
    d.mkdir()
    inp = tmp_path / "in.yml"
    inp.write_text(yaml_str, encoding="utf-8")

    popts = yaml.load(defconfig_str)
    popts['output_dirname'] = d
    process_inputs(inp, popts)
    assert len(list(d.iterdir())) == 1
    # for child in d.iterdir(): print(child)


def test_process_inputs_debug(tmp_path):
    yaml = StrYAML()
    d = tmp_path / "out"
    d.mkdir()
    inp = tmp_path / "in.yml"
    inp.write_text(yaml_str, encoding="utf-8")

    popts = yaml.load(defconfig_str)
    popts['output_dirname'] = d
    process_inputs(inp, popts, True)
    assert len(list(d.iterdir())) == 1


def test_bad_file(capfd, tmp_path):
    yaml = StrYAML()
    popts = yaml.load(defconfig_str)
    inp2 = tmp_path / "in.ymml"
    inp2.write_text(yaml_str, encoding="utf-8")

    process_inputs(inp2, popts)
    out, err = capfd.readouterr()
    assert file_type_err in out

    with pytest.raises(FileTypeError):
        get_input_yaml(inp2, popts)
