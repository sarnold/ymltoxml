#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2022 Stephen L Arnold
#
# This is free software, licensed under the LGPL-2.1 license
# available in the accompanying LICENSE file.

"""
Transform mavlink-style xml files to/from xml and yaml. Note yaml
format uses custom markup for XML attributes and comments. See the
xmltodict docs for details.
"""

import sys
from optparse import OptionParser  # pylint: disable=W0402
from pathlib import Path

import pkg_resources
import xmltodict
import yaml as yaml_loader
from munch import Munch
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO


class FileTypeError(Exception):
    """Raise when the file extension is not '.xml', '.yml', or '.yaml'"""

    __module__ = Exception.__module__


class StrYAML(YAML):
    """
    New API likes dumping straight to file/stdout, so we subclass and
    create 'inefficient' custom string dumper.
    """

    def dump(self, data, stream=None, **kw):
        stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        return stream.getvalue()


def load_config(file_encoding='utf-8'):
    """
    Load yaml configuration file and munchify the data. If local file is
    not found in current directory, the default will be loaded.

    :param file_encoding: file encoding of config file
    :type file_encoding: str
    :return: Munch cfg obj and cfg file as Path obj
    :rtype tuple:
    """
    cfgfile = Path('.ymltoxml.yaml')
    if not cfgfile.exists():
        cfgfile = Path(pkg_resources.resource_filename(__name__, 'data/ymltoxml.yaml'))
    cfgobj = Munch.fromYAML(cfgfile.read_text(encoding=file_encoding))

    return cfgobj, cfgfile


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


def restore_xml_comments(xmls):
    """
    Turn tagged comment elements back into xml comments.

    :param xmls: xml (file) output from ``unparse``
    :type xmls: str
    :return xmls: processed xml string
    :rtype: str
    """
    for rep in (("<#comment>", "<!-- "), ("</#comment>", " -->")):
        xmls = xmls.replace(*rep)
    return xmls


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

        if prog_opts['process_comments']:
            res = restore_xml_comments(xml)

    else:
        yaml = StrYAML()
        yaml.indent(
            mapping=prog_opts['mapping'],
            sequence=prog_opts['sequence'],
            offset=prog_opts['offset'],
        )

        yaml.preserve_quotes = prog_opts['preserve_quotes']
        res = yaml.dump(payload)

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
    opath = fpath
    if outpath:
        opath = Path(outpath)

    if not fpath.exists():
        print(f'Input file {fpath} not found! Skipping...')
    else:
        if debug:
            print(f'Processing data from {fpath}')

        try:
            from_yml, indata = get_input_type(fpath, prog_opts)
        except FileTypeError as exc:
            print(f'{exc} => {fpath}')
            sys.exit(1)

        outdata = transform_data(indata, prog_opts, to_xml=from_yml)

        if from_yml:
            new_opath = opath.with_suffix(prog_opts['default_xml_ext'])
            outdata = outdata + '\n'
        else:
            new_opath = opath.with_suffix(prog_opts['default_yml_ext'])

        if debug:
            print(f'Writing processed data to {new_opath}')
        new_opath.write_text(outdata, encoding=prog_opts['file_encoding'])


def main(argv=None):
    """
    Transform YAML to XML and XML to YAML.
    """
    debug = False
    cfg, pfile = load_config()
    popts = Munch.toDict(cfg)

    if argv is None:
        argv = sys.argv
    parser = OptionParser(
        usage="usage: %prog [options] arg1 arg2", version=f"%prog {VERSION}"
    )
    parser.description = 'Transform YAML to XML and XML to YAML.'
    parser.add_option(
        '-i',
        '--infile',
        metavar="FILE",
        action='store',
        dest='infile',
        help='Path to input file (use with --outfile)',
    )
    parser.add_option(
        '-o',
        '--outfile',
        metavar="FILE",
        action='store',
        dest='outfile',
        help='Path to output file (use with --infile)',
    )
    parser.add_option(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="Display more processing info",
    )
    parser.add_option(
        '-d',
        '--dump-config',
        action='store_true',
        dest="dump",
        help='Dump default configuration file to stdout',
    )

    (options, args) = parser.parse_args()

    if options.outfile and not options.infile:
        parser.error("missing --infile argument")
    if options.verbose:
        debug = True
    if options.infile and not args:
        outname = options.outfile
        process_inputs(options.infile, popts, outname, debug=debug)
        sys.exit(0)
    elif options.dump:
        sys.stdout.write(pfile.read_text(encoding=popts['file_encoding']))
        sys.exit(0)
    if not args:
        parser.print_help()
        sys.exit(1)

    if len(args) > 0:
        for filearg in args:
            process_inputs(filearg, popts, debug=debug)


VERSION = pkg_resources.get_distribution('ymltoxml').version

if __name__ == '__main__':
    main()
