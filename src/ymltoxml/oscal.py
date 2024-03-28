"""
The main init, run, and self-test functions for oscal extract.
"""

import argparse
import importlib
import sys
from pathlib import Path

from munch import Munch

from .utils import VERSION, load_config


def self_test(opts):
    """
    Basic sanity check using ``import_module``.
    """
    print("Python version:", sys.version)
    print("-" * 80)

    modlist = ['ymltoxml.__init__', 'ymltoxml.oscal', 'ymltoxml.utils']
    for modname in modlist:
        try:
            print(f'Checking module {modname}')
            mod = importlib.import_module(modname)
            print(mod.__doc__)

        except (NameError, KeyError, ModuleNotFoundError) as exc:
            print("FAILED: %s", repr(exc))

    try:
        print(f'Checking if {opts.default_content_path} exists')
        try:
            ret = Path(opts.default_content_path).resolve(strict=True)
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

    ucfg, _ = load_config(Path(__file__).stem)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Extract data from OSCAL content repo',
    )
    parser.add_argument('--version', action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument(
        '-t', '--test', help='run sanity checks and exit', action='store_true'
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="display more processing info",
    )
    parser.add_argument(
        '-d',
        '--dump-config',
        help="dump active configuration to stdout and exit",
        action='store_true',
        dest="dump",
    )
    parser.add_argument(
        '-n',
        '--nist-path',
        metavar="PATH",
        type=str,
        help="path to NIST oscal-content directory",
        dest="nist",
    )
    parser.add_argument(
        'file',
        nargs='?',
        metavar="FILE",
        type=str,
        default=None,
        help="path to input file",
    )

    args = parser.parse_args()

    if args.dump:
        sys.stdout.write(Munch.toYAML(ucfg))
        sys.exit(0)
    if args.test:
        self_test(ucfg)
        sys.exit(0)
    if not args.file:
        parser.print_usage()
        print("oscal: error: the following arguments are required: FILE")
        sys.exit(1)

    nist_path = args.nist if args.nist else ucfg.default_content_path
    if args.verbose:
        print(f"Using path to oscal: {nist_path}")
        if args.file:
            print(f"Using input file: {args.file}")


if __name__ == "__main__":
    main()  # pragma: no cover
