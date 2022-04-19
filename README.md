# Airplane Python SDK [![PyPI](https://img.shields.io/pypi/v/airplanesdk)](https://pypi.org/project/airplanesdk/) [![PyPI - License](https://img.shields.io/pypi/l/airplanesdk)](./LICENSE) [![Docs](https://img.shields.io/badge/Docs-airplane-blue)](https://docs.airplane.dev/creating-tasks/python)

SDK for writing [Airplane](https://airplane.dev) tasks in Python.

## Getting started

```sh
pip install airplanesdk
```

## Usage

To write a Python task in Airplane, create a `.py` file and export a function like so:

```py
import airplane

def main(params):
  return f"Hello, {params['name']}"
```

You can configure the parameters that your task will receive in the [Airplane UI](http://app.airplane.dev/). They'll be passed through the `params` argument to your function as a dictionary keyed by the slugs you see in the UI.

To execute your task, first [install the Airplane CLI](https://docs.airplane.dev/platform/airplane-cli).

Once installed, execute your task locally:

```sh
airplane dev ./path/to/file.py -- --name=World
```

If that looks good, deploy your task to Airplane and give it a [run in the UI](https://app.airplane.dev/library)!

```sh
airplane deploy ./path/to/file.py
```
