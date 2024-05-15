Changelog
=========


0.4.0 (2024-05-15)
------------------

New
~~~
- Add ID set analysis to oscal module, update tests and default cfg.
  [Steve Arnold]
- Add analysis script using SSG nist control files. [Steve Arnold]

  * update project files for new dependencies
- Add file reader to handle csv, json, yaml, and simple text files.
  [Steve Arnold]

  * for each type, parse into a list of objects and return the list
  * where simple text files are something like the control IDs
    in tests/data

Changes
~~~~~~~
- Add more control status reporting, update oscal yaml config. [Steve
  Arnold]
- Cleanup deps and docstrings, add set compare to demo script. [Steve
  Arnold]
- Still more readme cleanup. [Steve Arnold]
- Commit initail name changes; package, imports, readme. [Steve Arnold]
- Make sure yagrep uses new output func, cleanup readme. [Steve Arnold]
- Bump tox workflow deps and cleanup/improve readme. [Steve Arnold]
- Bump all workflow action versions. [Steve Arnold]
- Add another text_file_reader consumer and cleanup some lint. [Steve
  Arnold]

Fixes
~~~~~
- Account for longer ID strings, update changelog and repolite cfgs.
  [Steve Arnold]

  * update tests and older analysis script
  * bump requirements-sync.txt for new repolite release
- Cleanup docstrings after sphinx checks. [Steve Arnold]

Other
~~~~~
- Dev: add csv file munge option, cleanup oscal files. [Steve Arnold]

  * add munge file arg to pass in csv data to compare and append
    a column for id set status, eg, whether ids in the input list
    are present in the csv data, and then mark the new column Y/N
  * short-circuit munge file arg and feed it single column of
    control IDs
- Add small set of test IDs from openembedded profile. [Steve Arnold]


0.3.0 (2024-03-12)
------------------

New
~~~
- Add new console script, update reqs and packaging. [Steve Arnold]

Changes
~~~~~~~
- Cleanup new feature bits and update documentation. [Steve Arnold]

  * use dpath.values for initial path search, and either dpath or
    nested_lookup for extracting values
  * update readme for new script, update all the usage bits
  * add new tests and update existing tests
  * expand and cleanup tox file
- Add new feature tests, update existing tests. [Steve Arnold]

Fixes
~~~~~
- Re-order yasort arg handling, update analyze script. [Steve Arnold]


0.2.2 (2023-09-05)
------------------

New
~~~
- Add a changelog file and gitchangelog cfg, add to docs build. [Stephen
  L Arnold]

Changes
~~~~~~~
- Bump changelog for release, add tox cmd to (re)generate changes.
  [Stephen L Arnold]
- Cleanup docstrings and readme usage. [Stephen L Arnold]
- Still more readme cleanup. [Stephen L Arnold]

Fixes
~~~~~
- Clean up docstrings in utils. [Stephen L Arnold]


0.2.1 (2023-07-16)
------------------

New
~~~
- Wire up sorting opts, cleanup config file, update readme. [Stephen L
  Arnold]

  * add sdist artifact to release workflow

Fixes
~~~~~
- Ci: update artifact conditional. add inspection step. [Stephen L
  Arnold]


0.2.0 (2023-07-15)
------------------

New
~~~
- Add sorting script and default config, cleanup lint. [Stephen L
  Arnold]
- Add more project docs to sphinx build. [Stephen L Arnold]

  * filter out/remove local file links for docs build
- Add more config options, update tool deps and readme. [Stephen L
  Arnold]

  * allow more user-facing config options, add munch-stubs for mypy
  * update tool deps and cfgs to use new type stubs
  * update readme usage description

Changes
~~~~~~~
- Readme cleanup, add note about yasort script. [Stephen L Arnold]
- Dbg: run tox bare-ass in github runner for workflow debug. [Stephen L
  Arnold]
- Update readme with new usage output. [Stephen L Arnold]

Fixes
~~~~~
- Use new path to source rst for github readme rendering. [Stephen L
  Arnold]
- Replace sys.argv with option parser, wire up options and args.
  [Stephen L Arnold]

  * yes, optparse is deprected so may be replaced in the future

Other
~~~~~
- Adjust importlib version cutoff in reqs. [Stephen L Arnold]
- Move some shared code to separate module, update pre-commit cfg.
  [Stephen L Arnold]


0.1.0 (2022-06-22)
------------------

New
~~~
- Add sphinx api-doc build, update readme and doc strings. [Stephen L
  Arnold]
- Add arg to dump default config yaml to stdout. [Stephen L Arnold]

Changes
~~~~~~~
- Update readme and usage output. [Stephen L Arnold]
- Flatten cfg file, use single cfg object, cleanup doc strings. [Stephen
  L Arnold]

Fixes
~~~~~
- Replace old thing/new thing => use importlib for cfg file. [Stephen L
  Arnold]

  * use external importlib pkgs first
  * make mypy ignore one of the 2 importlib imports
  * install pkg for command-line test

Other
~~~~~
- Add docs workflow, fix broken doc link, update ci workflow. [Stephen L
  Arnold]
- Cleanup metadata/packaging and workflow files. [Stephen L Arnold]
- Add more CI workflows for wheels, pylint, release. [Stephen L Arnold]


0.0.0 (2022-06-19)
------------------
- Initial commit with test scripts and tox driver. [Stephen L Arnold]
- Initial commit. [Steve Arnold]
