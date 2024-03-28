"""Console script for searching YAML or XML files."""

import argparse
import sys
from pathlib import Path

import dpath
from munch import Munch
from nested_lookup import nested_lookup

from .utils import VERSION as __version__
from .utils import (
    FileTypeError,
    load_config,
    text_data_writer,
    text_file_reader,
)

# pylint: disable=R0801


def process_inputs(filepath, grep_args, prog_opts, debug=False):
    """
    Handle file arguments and process them. Return any input data for use
    with ``dpath`` search.

    :param filepath: filename as path str
    :type filepath: str
    :param prog_opts: configuration options
    :type prog_opts: dict
    :param debug: enable extra processing info
    :return: data and source type boolean or None
    :handles FileTypeError: if input file is not yaml or xml
    """

    def glob_filter(x):
        """
        Basic search glob to use with dpath functions.
        """
        if grep_args.text in str(x):
            return True
        return False

    fpath = Path(filepath)
    path_sep = prog_opts['default_separator']

    if not fpath.exists():
        print(f'Input file {fpath} not found! Skipping...')
    else:
        if debug:
            print(f'Searching in {fpath}...')

        try:
            indata = text_file_reader(fpath, prog_opts)
        except FileTypeError as exc:
            print(f'{exc} => {fpath}')
            return None
        if debug:
            print(indata)

        if grep_args.filter:
            result = dpath.search(indata, '**', afilter=glob_filter, separator=path_sep)
        elif grep_args.lookup:
            result = nested_lookup(grep_args.text, indata)
        else:
            result = dpath.values(indata, grep_args.text, separator=path_sep)

        text_data_writer(result, prog_opts)


def main(argv=None):  # pragma: no cover
    """
    Process args and execute search.
    """
    if argv is None:
        argv = sys.argv

    cfg, pfile = load_config(Path(__file__).stem)
    popts = Munch.toDict(cfg)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='''Search in YAML files for keys and values.
            The default search with no options is path-based, thus it
            may return empty results without a path or wildcard. Use
            the filter argument to find the path(s) to a key using a
            substring search.''',
        usage='%(prog)s [-h] [--version] [-v] [-d] [-s] [-f | -l] TEXT FILE [FILE ...]',
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
        help='save active config to default filename (.yagrep.yml) and exit',
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f",
        "--filter",
        action='store_true',
        help="Filter out data not matching input string (no paths)",
    )
    group.add_argument(
        "-l",
        "--lookup",
        action='store_true',
        help="Lookup by key and return list of values for any matches",
    )
    parser.add_argument(
        'text',
        nargs='?',
        metavar="TEXT",
        type=str,
        help="Text string to look for (one-only, required)",
    )
    parser.add_argument(
        'file',
        nargs='*',
        metavar="FILE",
        type=str,
        help="Look in file(s) for text string (at least one, required)",
    )

    args = parser.parse_args()

    if args.save:
        cfg_data = pfile.read_bytes()
        def_config = Path('.yagrep.yml')
        def_config.write_bytes(cfg_data)
        sys.exit(0)
    if args.dump:
        sys.stdout.write(pfile.read_text(encoding=popts['file_encoding']))
        sys.exit(0)
    # we need to help argparse here, since it has trouble parsing the 2
    # postional args as required when both are missing, even with help from
    # nargs behavior (we also need customized usage msg above to replace the
    # default error text with the following print() statement)
    if not args.file or not args.text:
        parser.print_usage()
        print("yagrep: error: the following arguments are required: TEXT *and* FILE")
        sys.exit(1)

    for filearg in args.file:
        process_inputs(filearg, args, popts, args.verbose)


if __name__ == '__main__':
    main()
