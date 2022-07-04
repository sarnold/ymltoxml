=========================
 ymltoxml (and xmltoyml)
=========================

|ci| |wheels| |release| |badge|

|pre| |pylint|

|tag| |license| |python|

A Python command line tool to convert between XML_ files and YAML_ files,
preserving attributes and comments (with minor corrections).  The default
file encoding for both types is UTF-8 without a BOM.  The main intent is
to support YAML-based development of custom mavlink_ dialects.

Quick Start
===========

Install with pip
----------------

This package is *not* yet published on PyPI, thus use one of the
following to install the latest ymltoxml on any platform::

  $ pip install -U -f https://github.com/sarnold/ymltoxml/releases/ ymltoxml

or use this command to install a specific version::

  $ pip install git+https://github.com/sarnold/ymltoxml.git@0.1.0

The full package provides the ``ymltoxml.py`` executable as well as
a reference configuration file that provides defaults for all values.

If you'd rather work from the source repository, it supports the common
idiom to install it on your system in a virtual env after cloning::

  $ python3 -m venv env
  $ source env/bin/activate
  $ pip install .
  $ ymltoxml --version
  $ ymltoxml --dump-config
  $ deactivate

The alternative to python venv is the ``tox`` test driver.  If you have it
installed already, see the example tox commands below.

Usage
-----

The current version supports minimal command options; if no options are
provided, the only required arguments are one or more files of a single
type::

  (py) user@host ymltoxml (main) $ ymltoxml
  Usage: ymltoxml [options] arg1 arg2

  Transform YAML to XML and XML to YAML.

  Options:
    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -i FILE, --infile=FILE
                          Path to input file (use with --outfile)
    -o FILE, --outfile=FILE
                          Path to output file (use with --infile)
    -v, --verbose         Display more processing info
    -d, --dump-config     Dump default configuration file to stdout


* for processing individual files/paths, use the ``--infile`` option,
  either with or without the ``--outfile`` option
* for processing multiple files, pass all files as arguments (paths
  can be relative or absolute)

  + when passing input files as arguments, the output file names/paths
    are the same as the input files but with the output extension

By default it will process one more input files as command args, typically
in the current directory, however, the ``--infile`` option will only
process a single file path, optionally with an output file path, with no
extra (file) arguments.

The main processing tweaks for yml/xml output formatting are specified
in the default configuration file; if you need to change something, you
can use your own config file in the working directory; note the local
copy must be named ``.ymltoxml.yaml``.  To get a copy of the default
configuration file, do::

  $ cd path/to/work/dir/
  $ ymltoxml --dump-config > .ymltoxml.yaml
  $ $EDITOR .ymltoxml.yaml


Features and limitations
------------------------

We only test on mavlink XML message definitions, so it probably *will not*
work at all on arbitrarily complex XML files with namespaces, etc.  The
current round-trip is not exact, due to the following:

* missing encoding is added to version tag
* leading/trailing whitespace in text elements and comments is not preserved
* elements with self-closing tags are converted to full closing tags
* empty elements on more than one line are not preserved

For the files tested (eg, mavlink) the end result is cleaner/shinier XML.

Local workflow
===============

This tool is intended to be part of larger workflow, ie, developing a
custom mavlink message dialect and generating/deploying the resulting
mavlink language interfaces.  To be more specific, for this example we
use a mavlink-compatible component running on a micro-controller, thus
the target language bindings are C and C++.

Tool requirements for the full mavlink workflow:

* initially just recent pymavlink, Python, and Tox_

Both mavlink and pymavlink require a (host) GCC toolchain for full builds,
however, the basic workflow to generate mavlink library headers requires
only Git, Python, and Tox.

.. _mavlink: https://mavlink.io/en/messages/common.html
.. _Tox: https://github.com/tox-dev/tox
.. _XML: https://en.wikipedia.org/wiki/Extensible_Markup_Language
.. _YAML: https://en.wikipedia.org/wiki/YAML

.. note:: This project uses versioningit_ to generate and maintain the
          version file, which only gets included in the sdist/wheel
          packages. In a fresh clone, running any of the tox_ commands
          should generate the current version file.

.. _versioningit: https://github.com/jwodder/versioningit


In-repo workflow with Tox
-------------------------

As long as you have git and at least Python 3.6, then the "easy" dev
workflow is to clone this repository and install Tox via your system
package manager, eg::

  $ sudo apt-get update
  $ sudo apt-get install tox


After cloning this repository, you can run the repo checks with the
``tox`` command.  It will build a virtual python environment with
all the dependencies and run the specified commands, eg:

::

  $ git clone https://github.com/sarnold/ymltoxml
  $ cd ymltoxml/
  $ tox -e py

There are no actual unittests yet, but the above will run the base ``tox``
command against one of the mavlink dialect files. Note this will run the
round-trip test command using the your (default) system Python; to specify
the Python version and host OS type, run something like::

  $ tox -e py39-linux

Full list of additional ``tox`` commands:

* ``tox -e style`` will run flake8 style checks
* ``tox -e lint`` will run pylint (somewhat less permissive than PEP8/flake8 checks)
* ``tox -e mypy`` will run mypy import and type checking
* ``tox -e isort`` will run isort import checks
* ``tox -e clean`` will remove temporary test files

To build/lint the api docs, use the following tox commands:

* ``tox -e docs`` build the documentation using sphinx and the api-doc plugin
* ``tox -e docs-lint`` build the docs and run the sphinx link checking


Making Changes & Contributing
=============================

We use the gitchangelog_ action to generate our github Release page, as
well as the gitchangelog message format to help it categorize/filter
commits for a tidier release page. Please use the appropriate ACTION
modifiers in any Pull Requests.

This repo is also pre-commit_ enabled for various linting and format
checks.  The checks run automatically on commit and will fail the
commit (if not clean) with some checks performing simple file corrections.

If other checks fail on commit, the failure display should explain the error
types and line numbers. Note you must fix any fatal errors for the
commit to succeed; some errors should be fixed automatically (use
``git status`` and ``git diff`` to review any changes).

See the following pages for more information on gitchangelog and pre-commit.

.. inclusion-marker-1

* generate-changelog_
* pre-commit-config_
* pre-commit-usage_

.. _generate-changelog:  docs/source/dev/generate-changelog.rst
.. _pre-commit-config: docs/source/dev/pre-commit-config.rst
.. _pre-commit-usage: docs/source/dev/pre-commit-usage.rst
.. inclusion-marker-2

You will need to install pre-commit before contributing any changes;
installing it using your system's package manager is recommended,
otherwise install with pip into your usual virtual environment using
something like::

  $ sudo emerge pre-commit  --or--
  $ pip install pre-commit

then install it into the repo you just cloned::

  $ git clone https://github.com/sarnold/ymltoxml
  $ cd ymltoxml/
  $ pre-commit install

It's usually a good idea to update the hooks to the latest version::

    pre-commit autoupdate


.. _gitchangelog: https://github.com/sarnold/gitchangelog-action
.. _pre-commit: http://pre-commit.com/


.. |ci| image:: https://github.com/sarnold/ymltoxml/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/sarnold/ymltoxml/actions/workflows/ci.yml
    :alt: CI Status

.. |wheels| image:: https://github.com/sarnold/ymltoxml/actions/workflows/wheels.yml/badge.svg
    :target: https://github.com/sarnold/ymltoxml/actions/workflows/wheels.yml
    :alt: Wheel Status

.. |badge| image:: https://github.com/sarnold/ymltoxml/actions/workflows/pylint.yml/badge.svg
    :target: https://github.com/sarnold/ymltoxml/actions/workflows/pylint.yml
    :alt: Pylint Status

.. |release| image:: https://github.com/sarnold/ymltoxml/actions/workflows/release.yml/badge.svg
    :target: https://github.com/sarnold/ymltoxml/actions/workflows/release.yml
    :alt: Release Status

.. |pylint| image:: https://raw.githubusercontent.com/sarnold/ymltoxml/badges/main/pylint-score.svg
    :target: https://github.com/sarnold/ymltoxml/actions/workflows/pylint.yml
    :alt: Pylint score

.. |license| image:: https://img.shields.io/github/license/sarnold/ymltoxml
    :target: https://github.com/sarnold/ymltoxml/blob/master/LICENSE
    :alt: License

.. |tag| image:: https://img.shields.io/github/v/tag/sarnold/ymltoxml?color=green&include_prereleases&label=latest%20release
    :target: https://github.com/sarnold/ymltoxml/releases
    :alt: GitHub tag

.. |python| image:: https://img.shields.io/badge/python-3.6+-blue.svg
    :target: https://www.python.org/downloads/
    :alt: Python

.. |pre| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
