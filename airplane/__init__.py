"""airplane - An SDK for writing Airplane tasks in Python"""

from airplane import email, mongodb, rest, slack, sql
from airplane._version import __version__
from airplane.api.client import APIClient
from airplane.api.types import Run, RunStatus
from airplane.exceptions import InvalidEnvironmentException, RunPendingException
from airplane.output import append_output, set_output, write_named_output, write_output
from airplane.runtime import execute

# Deprecated
from airplane.runtime.standard import run
