# Airplane Python SDK [![PyPI](https://img.shields.io/pypi/v/airplanesdk)](https://pypi.org/project/airplanesdk/) [![PyPI - License](https://img.shields.io/pypi/l/airplanesdk)](./LICENSE) [![Docs](https://img.shields.io/badge/Docs-Python%20SDK-blue)](https://docs.airplane.dev/reference/runtime-api-and-airplane-sdk/python-sdk)

An SDK for writing Airplane tasks in Python.

## Usage

First, install the SDK:

```sh
pip install airplanesdk
```

Next, you can use the SDK to produce outputs which will be separated from your logs:

```python
import airplane

airplane.write_output("Show me what you got")

# You can also separate outputs into groups by attaching names:
airplane.write_named_output("saying", "Show me what you got")
airplane.write_named_output("saying", "Welcome to the club, pal")
airplane.write_named_output("name", "Summer")
```

This SDK can be used to programmatically kick off tasks and fetch their output:

```python
# You can get a task's ID from the URL bar, f.e.
# https://app.airplane.dev/tasks/1oMt2mZC1DjkOZXxHH8BV57xrmF
task_id = "..."
resp = airplane.run(task_id, {
  # Optionally provide parameters to your task, using the same name
  # as when templating a parameter into your task's CLI args.
  "DryRun": True,
})

# run() will return the run's status (Succeeded, Failed, Cancelled) and a
# dict of outputs, by name.
#
# Default outputs are available as `resp["outputs"]["output"]`.
print(resp["outputs"])
```

## Contributing

### Deployment

To deploy a new version of this SDK:

1. Bump the version number in `pyproject.toml` and `airplane/__init__.py`
2. Run the following to build and publish to PyPI:

```sh
poetry publish --build --username=airplane
```
