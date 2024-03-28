"""Console script for sorting YAML lists."""

import argparse
import sys
from pathlib import Path

from munch import Munch
from ruamel.yaml import YAML

from .utils import VERSION as __version__
from .utils import (
    FileTypeError,
    StrYAML,
    load_config,
    replace_angles,
    replace_curlys,
    sort_from_parent,
)

# pylint: disable=R0801


def get_input_yaml(filepath, prog_opts):
    """
    Check filename extension, open and munge the contents, return data
    (where in this context we "munge" the curly braces to make it valid
    YAML).

    :param filepath: filename as Path obj
    :param prog_opts: configuration options
    :type prog_opts: dict
    :return data_in: file data
    :raises FileTypeError: if the input file is not yaml
    """

    data_in = None
    yaml = YAML()

    if filepath.name.lower().endswith(('.yml', '.yaml')):
        with open(filepath, encoding=prog_opts['file_encoding']) as f_path:
            file_data = f_path.read()
        munged_data = replace_curlys(str(file_data))
        data_in = yaml.load(munged_data)
    else:
        raise FileTypeError("FileTypeError: unknown input file extension")
    return data_in


def sort_list_data(payload, prog_opts):
    """
    Set YAML formatting and sort keys from config, produce output data
    from input dict-ish object.

    :param payload: Dict obj representing YAML input data
    :param prog_opts: configuration options
    :type prog_opts: dict
    :return res: yaml dump of sorted input
    """
    yaml = StrYAML()
    yaml.indent(
        mapping=prog_opts['mapping'],
        sequence=prog_opts['sequence'],
        offset=prog_opts['offset'],
    )
    yaml.preserve_quotes = prog_opts['preserve_quotes']

    payload_sorted = sort_from_parent(payload, prog_opts)

    return yaml.dump(payload_sorted)


def process_inputs(filepath, prog_opts, debug=False):
    """
    Handle file arguments and process them. Write new (sorted) files to
    the 'sorted-out/' directory in the current working directory.

    :param filepath: filename as Path obj
    :param prog_opts: configuration options
    :type prog_opts: dict
    :param debug: enable extra processing info
    :return None:
    :handles FileTypeError: if input file is not yml
    """

    fpath = Path(filepath)
    outdir = Path(prog_opts['output_dirname'])
    opath = outdir.joinpath(fpath.stem)

    if not fpath.exists():
        print(f'Input file {fpath} not found! Skipping...')
    else:
        if debug:
            print(f'Processing data from {fpath}')

        try:
            indata = get_input_yaml(fpath, prog_opts)
        except FileTypeError as exc:
            print(f'{exc} => {fpath}')
            return
        if debug:
            print(indata)

        outdata = sort_list_data(indata, prog_opts)

        restored_data = replace_angles(outdata)

        new_opath = opath.with_suffix(prog_opts['default_yml_ext'])
        if debug:
            print(f'Writing processed data to {new_opath}')
        new_opath.write_text(restored_data, encoding=prog_opts['file_encoding'])


def main(argv=None):  # pragma: no cover
    """
    Read/write YAML files with sorted list(s).
    """
    debug = False
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Sort YAML lists and write new files.',
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display more processing info",
    )
    parser.add_argument(
        '-d',
        '--dump-config',
        action='store_true',
        dest="dump",
        help='Dump default configuration file to stdout',
    )
    parser.add_argument(
        '-s',
        '--save-config',
        action='store_true',
        dest="save",
        help='save active config to default filename (.yasort.yml) and exit',
    )
    parser.add_argument(
        'file',
        nargs='*',
        metavar="FILE",
        type=str,
        help="Process input file(s) to target directory",
    )

    args = parser.parse_args()

    cfg, pfile = load_config(Path(__file__).stem)
    popts = Munch.toDict(cfg)
    outdir = popts['output_dirname']

    if args.save:
        cfg_data = pfile.read_bytes()
        def_config = Path('.yasort.yml')
        def_config.write_bytes(cfg_data)
        sys.exit(0)
    if args.dump:
        sys.stdout.write(pfile.read_text(encoding=popts['file_encoding']))
        sys.exit(0)
    if args.verbose:
        debug = True
    if not args.file:
        parser.print_help()
        sys.exit(1)
    if debug:
        print(f'Creating output directory {outdir}')
    Path(outdir).mkdir(exist_ok=True)
    for filearg in args.file:
        process_inputs(filearg, popts, debug=debug)


if __name__ == '__main__':
    main()
