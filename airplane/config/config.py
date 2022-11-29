import functools
from typing import Any, Callable, Dict, List, Optional

from airplane.api.entities import Run
from airplane.config.definitions import TaskDef
from airplane.config.types import EnvVar, FuncT, Resource, Schedule
from airplane.runtime import execute


def task(
    slug: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    require_requests: bool = False,
    allow_self_approvals: bool = True,
    timeout: int = 3600,
    constraints: Optional[Dict[str, str]] = None,
    resources: Optional[List[Resource]] = None,
    schedules: Optional[List[Schedule]] = None,
    env_vars: Optional[List[EnvVar]] = None,
) -> Callable[[FuncT], Callable[..., Run]]:
    """Decorator used to define an Airplane task.

    This decorator inspects the decorated function to create an Airplane task. The task's parameters
    are deduced from the function's arguments and type hints.

    Additional parameter metadata can be provided by attaching an airplane.ParamConfig to a
    typing.Annotated typehint (for versions of Python prior to 3.9, typing_extensions.Annotated
    can be used).

    The following map enumerates the supported Python types and equivalent Airplane
    parameter types (Airplane parameter details https://docs.airplane.dev/platform/parameters)::

        str: short text
        airplane.LongText: long text
        airplane.SQL: SQL
        bool: boolean
        int: integer
        float: number
        airplane.File: file
        datetime.date: date
        datetime.datetime: datetime
        airplane.ConfigVar: config variable

    Example:
        Sample task::

            @airplane.task()
            def add_two_numbers(first_number: int, second_number: int) -> int:
                return first_number + second_number

        Sample task with parameter annotation::

            @airplane.task()
            def capitalize_string(
                input: Annotated[str, airplane.ParamConfig(name="User string")]
            ) -> str:
                return input.capitalize()
    Args:
        slug:
            Human-friendly identifier used to reference this task. Must be unique
            across tasks and workflows. Defaults to function name.
        name:
            Task name displayed on the Airplane app. Defaults to funcion name in sentence case.
        description:
            Task description displayed on the Airplane app. If not provided, the description
            will be pulled from the docstring of the decorated function.
        require_requests:
            Whether or not this task requires a request to execute.
        allow_self_approvals:
            Whether or not this task allows self approvals.
        timeout:
            How long a task can run (in seconds) for before it is automatically cancelled.
        constraints:
            Constraints for which agents are allowed to execute this task's runs, only
            applicable for users with self hosted agents.
        resources:
            Resources to attach to this task. Resources can be accessed through environment
            variables or built-ins. Resources accessed by this task must be explicitly attached
            in the task's definition.
        schedules:
            Schedules to attach to this task. Schedules allow users to automatically run
            task on a recurring schedule.
        env_vars:
            Enviornment variables to attach to this task. Environment variables allow users
            to configure constant values or reference config variables.
    """

    def decorator(func: FuncT) -> Callable[..., Run]:
        """Assigns an __airplane attribute to a function to mark it as an Airplane object"""

        config = TaskDef.build(
            func=func,
            runtime="",
            slug=slug,
            name=name,
            description=description,
            require_requests=require_requests,
            allow_self_approvals=allow_self_approvals,
            timeout=timeout,
            constraints=constraints,
            resources=resources,
            schedules=schedules,
            env_vars=env_vars,
        )

        @functools.wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Run:
            kwargs.update(zip(func.__code__.co_varnames, args))
            return execute(config.slug, kwargs)

        # pylint: disable=protected-access
        wrapped.__airplane = config  # type: ignore
        return wrapped

    return decorator
