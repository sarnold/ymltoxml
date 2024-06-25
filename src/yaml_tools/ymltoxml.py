# Copyright 2022 Stephen L Arnold
#
# This is free software, licensed under the LGPL-2.1 license
# available in the accompanying LICENSE file.

"""
Transform mavlink-style xml files to/from xml and yaml. Note yaml
format uses custom markup for XML attributes and comments. See the
xmltodict docs for details.
"""

import argparse
import sys
from pathlib import Path

import xmltodict
import yaml as yaml_loader
from munch import Munch

from .utils import VERSION as __version__
from .utils import (
    FileTypeError,
    load_config,
    restore_xml_comments,
    str_yaml_dumper,
)


def get_input_type(filepath, prog_opts):
    """
    Check filename extension, open and process by file type, return type
    flag and data from appropriate loader.

    :param filepath: filename as Path obj
    :param prog_opts: configuration options
    :type prog_opts: dict
    :return tuple: destination type flag and file data
    :raises FileTypeError: if the input file is not xml or yml
    """
    to_xml = False
    data_in = None

    if filepath.name.lower().endswith(('.yml', '.yaml')):
        with filepath.open() as infile:
            data_in = yaml_loader.safe_load(infile)
        to_xml = True
    elif filepath.name.lower().endswith('.xml'):
        with filepath.open('r+b') as infile:
            data_in = xmltodict.parse(
                infile, process_comments=prog_opts['process_comments']
            )
    else:
        raise FileTypeError("FileTypeError: unknown input file extension")
    return to_xml, data_in


def transform_data(payload, prog_opts, to_xml=True):
    """
    Produce output data from dict-ish object using ``direction``.

    :param payload: input from xmltodict or yaml loader.
    :param prog_opts: configuration options
    :type prog_opts: dict
    :param to_xml: output direction, ie, if to_xml is True then output is XML.
    :type to_xml: bool
    :return res: output file data in specified format.
    """
    res = ''
    if to_xml:
        xml = xmltodict.unparse(
            payload,
            short_empty_elements=prog_opts['short_empty_elements'],
            pretty=prog_opts['pretty'],
            indent=prog_opts['indent'],
        )
        res = xml
        if prog_opts['process_comments']:
            res = restore_xml_comments(xml)

    else:
        res = str_yaml_dumper(payload, prog_opts)

    return res


def process_inputs(filepath, prog_opts, outpath=None, debug=False):
    """
    Handle file arguments and process them.

    :param filepath: filename as Path obj
    :param prog_opts: configuration options
    :type prog_opts: dict
    :param outpath: output file name/path if provided
    :type outpath: str
    :param debug: enable extra processing info
    :return None:
    :handlles FileTypeError: input file is not xml or yml
    """
    fpath = Path(filepath)
    opath = Path(outpath) if outpath else fpath

    if not fpath.exists():
        print(f'Input file {fpath} not found! Skipping...')
    else:
        if debug:
            print(f'Processing data from {fpath}')

        try:
            from_yml, indata = get_input_type(fpath, prog_opts)
        except FileTypeError as exc:
            print(f'{exc} => {fpath}')
            return

        outdata = transform_data(indata, prog_opts, to_xml=from_yml)

        if from_yml:
            new_opath = opath.with_suffix(prog_opts['default_xml_ext'])
            outdata = outdata + '\n'
        else:
            new_opath = opath.with_suffix(prog_opts['default_yml_ext'])

        if debug:
            print(f'Writing processed data to {new_opath}')
        new_opath.write_text(outdata, encoding=prog_opts['file_encoding'])


def main(argv=None):  # pragma: no cover
    """
    Transform YAML to XML and XML to YAML.
    """
    debug = False
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Transform YAML to XML and XML to YAML',
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
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
        help='save active config to default filename (.ymltoxml.yml) and exit',
    )
    parser.add_argument(
        '-i',
        '--infile',
        nargs='?',
        metavar="FILE",
        type=str,
        help="Path to single input file (use with --outfile)",
    )
    parser.add_argument(
        '-o',
        '--outfile',
        nargs='?',
        metavar="FILE",
        type=str,
        help="Path to single output file (use with --infile)",
    )
    parser.add_argument(
        'file',
        nargs='*',
        metavar="FILE",
        type=str,
        help="Process input file(s) to target extension",
    )

    args = parser.parse_args()
    if len(argv) == 1:
        parser.print_help()
        sys.exit(1)
    if args.outfile and not args.infile:
        parser.error("missing infile argument")
    if args.verbose:
        debug = True

    pcfg, pfile = load_config(debug=debug)
    popts = Munch.toDict(pcfg)

    if args.save:
        cfg_data = pfile.read_bytes()
        def_config = Path('.ymltoxml.yml')
        def_config.write_bytes(cfg_data)
        sys.exit(0)
    if args.dump:
        sys.stdout.write(pfile.read_text(encoding=popts['file_encoding']))
        sys.stdout.flush()
        sys.exit(0)

    if args.infile:
        if args.outfile:
            process_inputs(args.infile, popts, args.outfile, debug=debug)
        else:
            process_inputs(args.infile, popts, debug=debug)

    if args.file:
        for filearg in args.file:
            process_inputs(filearg, popts, debug=debug)


if __name__ == '__main__':
    main()
