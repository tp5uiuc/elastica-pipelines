# Elastica Pipelines

[![PyPI](https://img.shields.io/pypi/v/elastica-pipelines.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/elastica-pipelines.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/elastica-pipelines)][python version]
[![License](https://img.shields.io/pypi/l/elastica-pipelines)][license]

[![Read the documentation at https://elastica-pipelines.readthedocs.io/](https://img.shields.io/readthedocs/elastica-pipelines/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/tp5uiuc/elastica-pipelines/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/tp5uiuc/elastica-pipelines/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/elastica-pipelines/
[status]: https://pypi.org/project/elastica-pipelines/
[python version]: https://pypi.org/project/elastica-pipelines
[read the docs]: https://elastica-pipelines.readthedocs.io/
[tests]: https://github.com/tp5uiuc/elastica-pipelines/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/tp5uiuc/elastica-pipelines
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Features

- TODO

## Requirements

- TODO

## Installation

You can install _Elastica Pipelines_ via [pip] from [PyPI]:

```console
$ pip install elastica-pipelines
```

## Usage

Please see the [Command-line Reference] for details.

### IO

[![Python3][api-py3]](https://www.python.org/) ![Python3 API: Alpha][dev-alpha]

[api-py3]: https://img.shields.io/badge/language-Python3-yellowgreen "Python3 API"
[dev-alpha]: https://img.shields.io/badge/phase-alpha-yellowgreen "Status: Alpha"

```py
from elastica_pipelines import io

# ...

# Read only access to data written by Elastica++
series = io.series("elastica_metadata.h5")

# use series like a python Mapping
for t, records in series.iterations():
    print("Iteration: {0} at time {1}".format(t.iteration, t.time))

    # Records contain systems such as CosseratRods, Spheres which
    # are also python Mapping
    for uuid, rod in records.cosserat_rods().items():
        print("  Rod '{0}' attributes:".format(uuid))
        # even rod is a Mapping
        print("  {0}".format(rod.keys()))
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_Elastica Pipelines_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/tp5uiuc/elastica-pipelines/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/tp5uiuc/elastica-pipelines/blob/main/LICENSE
[contributor guide]: https://github.com/tp5uiuc/elastica-pipelines/blob/main/CONTRIBUTING.md
[command-line reference]: https://elastica-pipelines.readthedocs.io/en/latest/usage.html
