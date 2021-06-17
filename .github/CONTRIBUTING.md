# Contributing

## Deployment

To deploy a new version of this SDK, first open a PR with your chages, then:

1. Bump the version number in `pyproject.toml` and `airplane/__init__.py`
2. Merge your changes to `main`
3. Run the following off of `main` to build and publish to PyPI:

```sh
poetry publish --build --username=airplane
```

4. [Draft a new release in GitHub](https://github.com/airplanedev/python-sdk/releases/new) with a link to the relevant changes. [Example releases](https://github.com/airplanedev/python-sdk/releases).
