# Contributing

## Development

Install Python with [`pyenv`](https://github.com/pyenv/pyenv#installation) (`brew install pyenv`):

```sh
$ pyenv install
```

Set up a virtual environment and install dependencies with [`poetry`](https://python-poetry.org/docs/) (`brew install poetry`):

```sh
$ poetry env use python3.7
$ poetry install
# Spawn a shell within the virtual environment:
$ poetry shell
```

Run the test suite:

```sh
$ pre-commit run --all-files
```

You can optionally install pre-commit hooks that lint/test whenever you commit:

```sh
$ pre-commit install
```

## Deployment

To deploy a new version of this SDK, first open a PR with your changes, then:

1. Bump the version number in `pyproject.toml` and `airplane/_version.py`
2. Merge your changes to `main`
3. Run the following off of `main` to build and publish to PyPI using your PyPI account (if necessary, request for access to the airplanesdk PyPI project first from an existing owner):

```sh
poetry publish --build --username=<username>
```

4. [Draft a new release in GitHub](https://github.com/airplanedev/python-sdk/releases/new) with a link to the relevant changes. [Example releases](https://github.com/airplanedev/python-sdk/releases).
