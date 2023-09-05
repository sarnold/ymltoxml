Changelog
=========

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

Other
~~~~~
- Merge pull request #11 from sarnold/docs-cleanup. [Steve Arnold]

  Docs cleanup
- Merge pull request #10 from sarnold/comments. [Steve Arnold]

  Refactor libs, add tests, preserve comments in sorted list


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

Other
~~~~~
- Merge pull request #9 from sarnold/sort-opts. [Steve Arnold]

  wire up sorting opts


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
- Merge pull request #8 from sarnold/new-refactor. [Steve Arnold]

  code migration and cleanup
- Adjust importlib version cutoff in reqs. [Stephen L Arnold]
- Move some shared code to separate module, update pre-commit cfg.
  [Stephen L Arnold]
- Merge pull request #6 from sarnold/cfg-update. [Steve Arnold]

  add config options and munch type stubs
- Merge pull request #5 from sarnold/option-parse. [Steve Arnold]

  refactor arg handling


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
- Merge pull request #4 from sarnold/pre-commit. [Steve Arnold]

  readme and pre-commit updates
- Merge pull request #3 from sarnold/doc-updates. [Steve Arnold]

  Add sphinx doc build/workflow
- Add docs workflow, fix broken doc link, update ci workflow. [Stephen L
  Arnold]
- Merge pull request #2 from sarnold/script-ref. [Steve Arnold]

  Script refactor plus packaging and workflows
- Cleanup metadata/packaging and workflow files. [Stephen L Arnold]
- Add more CI workflows for wheels, pylint, release. [Stephen L Arnold]


0.0.0 (2022-06-19)
------------------
- Merge pull request #1 from sarnold/cleanup-poc. [Steve Arnold]

  Cleanup poc
- Initial commit with test scripts and tox driver. [Stephen L Arnold]
- Initial commit. [Steve Arnold]
