# Flask-MongoEngine

[![PyPI version](https://badge.fury.io/py/flask-mongoengine-3.svg)](https://badge.fury.io/py/flask-mongoengine-3)
[![CI Tests](https://github.com/idoshr/flask-mongoengine/actions/workflows/tests.yml/badge.svg)](https://github.com/idoshr/flask-mongoengine/actions/workflows/tests.yml)
[![Documentation Status](https://readthedocs.org/projects/flask-mongoengine-3/badge/?version=latest)](https://flask-mongoengine-3.readthedocs.io/en/latest/?badge=latest)
[![Maintainability](https://api.codeclimate.com/v1/badges/6fb8ae00b1008f5f1b20/maintainability)](https://codeclimate.com/github/idoshr/flask-mongoengine/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/6fb8ae00b1008f5f1b20/test_coverage)](https://codeclimate.com/github/idoshr/flask-mongoengine/test_coverage)
![PyPI - Downloads](https://img.shields.io/pypi/dm/flask-mongoengine-3)

Flask-MongoEngine is a Flask extension that provides integration with [MongoEngine],
[WtfForms] and [FlaskDebugToolbar].

## Installation

By default, Flask-MongoEngine will install integration only between [Flask] and
[MongoEngine]. Integration with [WTFForms] and [FlaskDebugToolbar] are optional and
should be selected as extra option, if required. This is done by users request, to
limit amount of external dependencies in different production setup environments.

All methods end extras described below are compatible between each other and can be
used together.

### Installation with MongoEngine only support

```bash
# For Flask >= 2.0.0
pip install flask-mongoengine-3
```

We still maintain special case for [Flask] = 1.1.4 support (the latest version in 1.x.x
branch). To install flask-mongoengine with required dependencies use ``legacy``
extra option.

```bash
# With Flask 1.1.4 dependencies
pip install flask-mongoengine-3[legacy]
```

### Installation with WTFForms and Flask-WTF support

Flask-mongoengine can be installed with [Flask-WTF] and [WTFForms] support. This
will extend project dependencies with [Flask-WTF], [WTFForms] and related packages.

```bash
# With Flask-WTF and WTFForms dependencies
pip install flask-mongoengine-3[wtf]
```

### Installation with Flask Debug Toolbar support

Flask-mongoengine provide beautiful extension to [FlaskDebugToolbar] allowing to monitor
all database requests. To use this extension [FlaskDebugToolbar] itself required. If
you need to install flask-mongoengine with related support, use:

```bash
# With FlaskDebugToolbar dependencies
pip install flask-mongoengine-3[toolbar]
```

### Installation with all features together

```bash
# With Flask-WTF, WTFForms and FlaskDebugToolbar dependencies
pip install flask-mongoengine-3[wtf,toolbar]
```

## Flask configuration

Flask-mongoengine does not provide any configuration defaults. User is responsible
for setting up correct database settings, to exclude any possible misconfiguration
and data corruption.

There are several options to set connection. Please note, that all except
recommended are deprecated and may be removed in future versions, to lower code base
complexity and bugs. If you use any deprecated connection settings approach, you should
update your application configuration.

Please refer to [complete connection settings description] for more info.

## Usage and API documentation

Full project documentation available on [read the docs].

## Contributing and testing

We are welcome for contributors and testers! Check [Contribution guidelines].

## License

Flask-MongoEngine is distributed under [BSD 3-Clause License].

[MongoEngine]: https://github.com/MongoEngine/mongoengine

[WTFForms]: https://github.com/pallets-eco/wtforms

[Flask-WTF]: https://github.com/pallets-eco/flask-wtf

[FlaskDebugToolbar]: https://github.com/pallets-eco/flask-debugtoolbar

[read the docs]: https://flask-mongoengine-3.readthedocs.io/en/latest/

[Flask]: https://github.com/pallets/flask

[BSD 3-Clause License]: LICENSE.md

[Contribution guidelines]: CONTRIBUTING.md

[complete connection settings description]: https://flask-mongoengine-3.readthedocs.io/en/latest/flask_config.html
