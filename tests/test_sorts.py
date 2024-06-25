import pytest

from yaml_tools.utils import StrYAML, sort_from_parent
from yaml_tools.yasort import sort_list_data

defconfig_str = """\
# comments should be preserved
file_encoding: 'utf-8'
default_yml_ext: '.yaml'
output_dirname: 'sorted-out'
default_parent_key: 'controls'
default_sort_key: 'rules'
has_parent_key: true
preserve_quotes: true
process_comments: true
mapping: 4
sequence: 6
offset: 4
"""

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

inner_sort_out = """\
policy: Security Requirements Guide - General Purpose Operating System
title: Security Requirements Guide - General Purpose Operating System
id: srg_gpos
version: v2r3
source: https://public.cyber.mil/stigs/downloads/
controls_dir: srg_gpos
levels:
- id: high
- id: medium
- id: low
controls:  # sequences can have nodes that are mappings
- id: Variables
  levels:
  - high
  - medium
  - low
  title: Variables
  rules:
  - login_banner_text=dod_banners            # this should be first
  - sshd_approved_ciphers=stig
  - sshd_approved_macs=stig
  - sshd_idle_timeout_value=10_minutes
  - var_account_disable_post_pw_expiration=35
  - var_accounts_authorized_local_users_regex=rhel8
  - var_auditd_action_mail_acct=root
  - var_auditd_space_left_action=email
  - var_auditd_space_left_percentage=25pc
  - var_authselect_profile=sssd
  - var_password_hashing_algorithm=SHA512
  - var_password_pam_dictcheck=1
  - var_sshd_disable_compression=no            # this should be last
"""

outer_sort_out = """\
policy: Security Requirements Guide - General Purpose Operating System
title: Security Requirements Guide - General Purpose Operating System
id: srg_gpos
version: v2r3
source: https://public.cyber.mil/stigs/downloads/
controls_dir: srg_gpos
levels:
    - id: high
    - id: medium
    - id: low
controls:  # sequences can have nodes that are mappings
    - id: Variables
      levels:
          - high
          - medium
          - low
      title: Variables
      rules:
          - login_banner_text=dod_banners    # this should be first
          - sshd_approved_ciphers=stig
          - sshd_approved_macs=stig
          - sshd_idle_timeout_value=10_minutes
          - var_account_disable_post_pw_expiration=35
          - var_accounts_authorized_local_users_regex=rhel8
          - var_auditd_action_mail_acct=root
          - var_auditd_space_left_action=email
          - var_auditd_space_left_percentage=25pc
          - var_authselect_profile=sssd
          - var_password_hashing_algorithm=SHA512
          - var_password_pam_dictcheck=1
          - var_sshd_disable_compression=no    # this should be last
"""


def test_sort_from():
    yaml = StrYAML()

    data = yaml.load(yaml_str)
    check = yaml.load(inner_sort_out)
    popts = yaml.load(defconfig_str)

    data_sorted = sort_from_parent(data, popts)
    assert data_sorted == check

    popts['has_parent_key'] = False
    popts['default_sort_key'] = 'controls'

    data_noparent = sort_from_parent(data, popts)
    # yaml.dump(data_noparent, sys.stdout)


def test_sort_list():
    yaml = StrYAML()

    data = yaml.load(yaml_str)
    check = outer_sort_out
    popts = yaml.load(defconfig_str)

    data_sorted = sort_list_data(data, popts)
    assert data_sorted == check


def test_sort_format():
    yaml = StrYAML()

    data = yaml.load(inner_sort_out)
    popts = yaml.load(defconfig_str)
    yaml.indent(
        mapping=popts['mapping'],
        sequence=popts['sequence'],
        offset=popts['offset'],
    )
    yaml.preserve_quotes = popts['preserve_quotes']

    assert yaml.dump(data) == outer_sort_out
