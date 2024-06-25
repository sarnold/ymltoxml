"""
The main init, run, and self-test functions for oscal extract.
"""

import argparse
import csv
import importlib
import sys
from collections import deque
from pathlib import Path

from munch import Munch
from natsort import os_sorted
from nested_lookup import nested_lookup

from .templates import xform_id
from .utils import (
    VERSION,
    FileTypeError,
    SortedSet,
    get_filelist,
    load_config,
    text_file_reader,
)

# pylint: disable=R0801


def csv_append_id_data(in_ids, prog_opts, uargs):  # pragma: no cover
    """
    Append/update column data using ID sets and write a new csv file using
    the given filename with ``.modified`` appended to the filename stem.
    """
    mpath = Path(uargs.munge)
    opath = Path('.').joinpath(mpath.stem)
    new_opath = opath.with_suffix('.modified.csv')
    delim = prog_opts['csv_delimiter'] if prog_opts['csv_delimiter'] else ','
    if uargs.verbose:
        print(f'Writing munged csv data to {new_opath}')

    writer = csv.writer(
        open(new_opath, 'w', newline='', encoding='utf-8'),
        delimiter=delim,
    )
    reader = csv.reader(
        open(uargs.munge, 'r', newline='', encoding='utf-8'),
        delimiter=delim,
    )
    headers = next(reader)
    for hdr in prog_opts['new_csv_hdrs']:
        headers.append(hdr)
    writer.writerow(headers)

    for ctl in reader:
        ctl = csv_row_match(in_ids, ctl)
        writer.writerow(ctl)


def csv_row_match(in_ids, ctl):
    """
    Extracted ctl munging from ``csv_append_id_data`` loop for testing.

    :param: ctl
    :type ctl: csv row data
    :return ctl: munged ctl
    """
    ctl_id = xform_id(ctl[0])
    sub_ids = [s for s in in_ids if ctl_id in s]
    if ctl_id in in_ids:
        ctl.append('Y')
    elif sub_ids != []:
        ctl.append(sub_ids[0])
    else:
        ctl.append('N')
    ctl.append(ctl_id)
    return ctl


def load_input_data(filepath, prog_opts, use_ssg=False, debug=False):
    """
    Find and gather the inputs, ie, content file(s) and user control IDs,
    into a tuple of lists (id_list, file_tuple_list). Load up the queues
    and return a tuple of both queues and the list of normalized user IDs
    from ``filepath``.
    """
    id_queue = deque()
    ctl_queue = deque()
    file_tuples = []
    in_list = text_file_reader(filepath, prog_opts)

    in_ids = [xform_id(x) for x in in_list] if in_list[0].islower() else in_list
    if debug:
        print(f'Normalized input Ids: {in_ids}')

    if use_ssg:
        prog_opts['default_content_path'] = prog_opts['default_ssg_path']
        prog_opts['default_profile_glob'] = prog_opts['default_ssg_glob']

    if debug:
        print(f"Loading content from: {prog_opts['default_content_path']}")

    ctl_files = get_filelist(
        prog_opts['default_content_path'],
        prog_opts['default_profile_glob'],
        debug,
    )

    for file in ctl_files:
        file_tuples.append((file, Path(file).name))
    if debug:
        print(f'Using control file(s): {file_tuples}')

    for path in file_tuples:
        if debug:
            print(f'Extracting IDs from {path[1]}')

        try:
            indata = text_file_reader(Path(path[0]), prog_opts)
        except FileTypeError as exc:
            print(f'{exc} => {Path(path[0])}')

        if not use_ssg:
            path_ids = [
                xform_id(x)
                for x in nested_lookup('id', indata)
                if x.islower() and '_' not in x and '-' in x
            ]
        else:
            path_ids = [x for x in nested_lookup('id', indata) if x.isupper()]

        id_queue.append((path[1], path_ids))

        for ctl_id in nested_lookup(prog_opts['default_lookup_key'], indata)[0]:
            ctl_queue.append((ctl_id['id'], ctl_id))

    if debug:
        print(f'ID queue Front: {id_queue[0]}')
        print(f'Control queue Front: {ctl_queue[0]}')

    return in_ids, id_queue, ctl_queue


def munge_file(filepath, prog_opts, uargs):
    """
    Munge a CSV file by appending columns.
    """
    input_ids = text_file_reader(filepath, prog_opts)
    csv_append_id_data(input_ids, prog_opts=prog_opts, uargs=uargs)


def process_data(filepath, prog_opts, uargs):
    """
    Process inputs, print some output.
    """
    input_ids, id_queue, ctl_queue = load_input_data(
        filepath, prog_opts, use_ssg=uargs.ssg, debug=uargs.verbose
    )
    in_list, not_in_list = id_set_match(input_ids, id_queue, uargs=uargs)

    if not uargs.quiet:
        print(f'\nControl queue has {len(ctl_queue)} items')

    rpt_attr = uargs.attribute if uargs.attribute else prog_opts['default_control_attr']
    if uargs.verbose:
        print(f'Checking input IDs: {in_list}')
    print(f'\nID;{rpt_attr}')
    for ctl in ctl_queue:
        if ctl[0] in in_list:
            print(f'{ctl[0]};{ctl[1][rpt_attr]}')


def ssg_ctrl_from_nist(in_id, prog_opts, uargs):
    """
    Create a new control in SSG format using the given ID. Give it some
    levels if it exists in the relevant NIST profiles
    """


def id_set_match(in_ids, id_q, uargs):
    """
    Quick set match analysis of ID sets.
    """
    in_set = SortedSet(in_ids)
    q_size = len(id_q)

    for _ in range(q_size):
        pname, id_list = id_q.popleft()
        if uargs.verbose:
            print(f"\n{pname} control IDs -> {len(id_list)}")
        id_set = SortedSet(id_list)

        if uargs.verbose:
            print(f"Input set is in {pname} set: {id_set > in_set}")
        common_set = id_set & in_set
        if uargs.verbose:
            print(f"Num input controls in {pname} set -> {len(common_set)}")
        not_in_set = in_set - id_set
        if uargs.verbose:
            print(f"Num input controls not in {pname} set -> {len(not_in_set)}")
            print(f"Input control IDs not in {pname} set: {list(not_in_set)}")

    # this requires a single filename in the search glob resulting in a control
    # ID queue size of 1 (as well as the sort-ids argument)
    if q_size == 1 and uargs.sort:
        sort_in = (
            [xform_id(x) for x in common_set] if in_ids[0].isupper() else common_set
        )
        sort_out = (
            [xform_id(x) for x in not_in_set] if in_ids[0].isupper() else not_in_set
        )
        print(f'\nInput IDs in {pname}:')
        for ctl in os_sorted(sort_in):
            print(ctl)
        print(f'\nInput IDs not in {pname}:')
        for ctl in os_sorted(sort_out):
            print(ctl)

    return list(common_set), list(not_in_set)


def self_test(ucfg):
    """
    Basic sanity check using ``import_module``.
    """
    print("Python version:", sys.version)
    print("-" * 80)

    modlist = ['yaml_tools.__init__', 'yaml_tools.oscal', 'yaml_tools.utils']
    for modname in modlist:
        try:
            print(f'Checking module {modname}')
            mod = importlib.import_module(modname)
            print(mod.__doc__)

        except (NameError, KeyError, ModuleNotFoundError) as exc:
            print("FAILED: %s", repr(exc))

    try:
        print(f'Checking if {ucfg.default_content_path} exists')
        try:
            ret = Path(ucfg.default_content_path).resolve(strict=True)
            print(f'  Resolved: {ret}')
        except (FileNotFoundError, RuntimeError) as exc:
            print(f"  {repr(exc)}")
    except (AttributeError, KeyError) as exc:
        print("Config is missing key 'default_content_path'! ")
        print(f"  {repr(exc)}")

    print("-" * 80)


def main(argv=None):  # pragma: no cover
    """
    Collect and process command options/arguments and then process data.
    """
    if argv is None:
        argv = sys.argv

    cfg, pfile = load_config(Path(__file__).stem)
    popts = Munch.toDict(cfg)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Extract data from OSCAL or SSG content sources',
    )
    parser.add_argument('--version', action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument(
        '-t', '--test', help='run sanity checks and exit', action='store_true'
    )
    parser.add_argument(
        '-u',
        '--use-ssg',
        help='use ssg content sources instead of oscal defaults',
        action='store_true',
        dest="ssg",
    )
    parser.add_argument(
        '-s',
        '--sort-ids',
        help='use sorted IDs in output report',
        action='store_true',
        dest="sort",
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='display more processing info',
    )
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='display less processing info',
    )
    parser.add_argument(
        '-m',
        '--munge-file',
        metavar="FILE",
        type=str,
        help="Data file munge using input control ID sets",
        dest="munge",
        default=None,
    )
    parser.add_argument(
        '-r',
        '--report-attribute',
        metavar="ATTR",
        type=str,
        help="Control report output using attribute ATTR",
        dest="attribute",
        default="status",
    )
    parser.add_argument(
        '-D',
        '--dump-config',
        help='dump active configuration to stdout and exit',
        action='store_true',
        dest='dump',
    )
    parser.add_argument(
        '-S',
        '--save-config',
        action='store_true',
        dest="save",
        help='save active config to default filename (.oscal.yml) and exit',
    )
    parser.add_argument(
        'file',
        nargs='?',
        metavar="FILE",
        type=str,
        help="path to input file with control IDs",
    )

    args = parser.parse_args()

    if args.save:
        cfg_data = pfile.read_bytes()
        Path(f'.oscal{cfg.default_ext}').write_bytes(cfg_data)
        sys.exit(0)
    if args.dump:
        sys.stdout.write(Munch.toYAML(cfg))
        sys.exit(0)
    if args.test:
        self_test(cfg)
        sys.exit(0)
    if not args.file:
        parser.print_usage()
        print("oscal: error: the following arguments are required: FILE")
        sys.exit(1)
    infile = args.file
    if not Path(infile).exists():
        print(f'Input file {infile} not found!')
        sys.exit(1)
    if args.munge:
        munge_file(infile, popts, args)

    if args.verbose:
        print(f"Path to content: {cfg.default_content_path}")
        print(f"Content file glob: {cfg.default_profile_glob}")
    if not args.quiet:
        print(f"Processing input file: {infile}")

    process_data(infile, popts, args)


if __name__ == "__main__":
    main()  # pragma: no cover
