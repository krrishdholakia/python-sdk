import datetime
import os
from distutils.command.config import config
from typing import Any, Dict, Optional, Union
from unittest import mock

import pytest
from typing_extensions import Annotated

from airplane.config.config import task, workflow
from airplane.config.definitions import ParamDef, TaskDef, make_slug
from airplane.config.types import (
    SQL,
    ConfigVar,
    EnvVar,
    File,
    LabeledOption,
    LongText,
    ParamConfig,
    Resource,
    Schedule,
)
from airplane.exceptions import (
    InvalidAnnotationException,
    InvalidTaskConfigurationException,
    UnsupportedDefaultTypeException,
)

# pylint: disable=protected-access


def test_definition_with_defaults() -> None:
    @task()
    def my_task(param: str) -> str:
        return param

    assert my_task.__airplane == TaskDef(  # type: ignore
        func=my_task.__wrapped__,  # type: ignore
        runtime="",
        slug="my_task",
        name="My task",
        description=None,
        require_requests=False,
        allow_self_approvals=False,
        timeout=3600,
        constraints=None,
        schedules=None,
        resources=None,
        parameters=[
            ParamDef(
                arg_name="param",
                slug="param",
                name="Param",
                type="shorttext",
                description=None,
                default=None,
                required=True,
                options=None,
                regex=None,
            )
        ],
        entrypoint_func="my_task",
        env_vars=None,
    )

    @workflow()
    def MyWorkflow(param: str) -> str:  # pylint: disable=invalid-name
        return param

    assert MyWorkflow.__airplane == TaskDef(  # type: ignore
        func=MyWorkflow.__wrapped__,  # type: ignore
        runtime="workflow",
        slug="my_workflow",
        name="My workflow",
        description=None,
        require_requests=False,
        allow_self_approvals=False,
        timeout=3600,
        constraints=None,
        schedules=None,
        resources=None,
        parameters=[
            ParamDef(
                arg_name="param",
                slug="param",
                name="Param",
                type="shorttext",
                description=None,
                default=None,
                required=True,
                options=None,
                regex=None,
            )
        ],
        env_vars=None,
        entrypoint_func="MyWorkflow",
    )


@mock.patch.dict(
    os.environ,
    {
        "AIRPLANE_API_HOST": "https://api.airplane.dev",
        "AIRPLANE_TOKEN": "foo_token",
        "AIRPLANE_ENV_ID": "foo_env",
    },
)
@mock.patch("requests.get")
@mock.patch("requests.post")
def test_call(mocked_post: mock.MagicMock, mocked_get: mock.MagicMock) -> None:
    @task()
    def my_task(param: str, param_other: str) -> str:
        del param_other
        return param

    mocked_post.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "runID": "run",
        },
    )
    mocked_get.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "status": "Succeeded",
            "id": "run",
            "output": "yay",
            "paramValues": {"param_other": "bar", "param": "foo"},
        },
    )
    resp = my_task("foo", param_other="bar")
    assert resp == "yay"
    mocked_post.assert_called_with(
        "https://api.airplane.dev/v0/tasks/execute",
        json={
            "slug": "my_task",
            "paramValues": {"param_other": "bar", "param": "foo"},
            "resources": {},
        },
        headers={
            "X-Airplane-Token": "foo_token",
            "X-Airplane-Client-Kind": "sdk/python",
            "X-Airplane-Client-Version": "0.3.9",
            "X-Airplane-Env-ID": "foo_env",
        },
    )

    assert my_task.__airplane.func("param", "other_param") == "param"  # type: ignore


def test_decorator_with_parameters() -> None:
    schedules = [
        Schedule(
            slug="schedule_slug",
            cron="0 * * * *",
            name="At midnight ",
            description="Schedule description",
            param_values={"int_param": 5, "str_param": "hello"},
        ),
    ]
    resources = [
        Resource(slug="resource_slug", alias="db_alias"),
        Resource("just_a_slug"),
    ]

    @task(
        slug="task_slug",
        name="Name of task",
        schedules=schedules,
        resources=resources,
        description="description",
        require_requests=True,
        allow_self_approvals=True,
        timeout=1,
        constraints={"a": "b"},
    )
    def my_task() -> None:
        pass

    assert my_task.__airplane == TaskDef(  # type: ignore
        func=my_task.__wrapped__,  # type: ignore
        runtime="",
        slug="task_slug",
        name="Name of task",
        description="description",
        require_requests=True,
        allow_self_approvals=True,
        timeout=1,
        constraints={"a": "b"},
        schedules=schedules,
        resources=resources,
        parameters=[],
        entrypoint_func="my_task",
        env_vars=None,
    )
    # Description provided in decorator takes precednce
    @task(
        description="description",
    )
    def my_task_1() -> None:
        """Docstring"""

    assert my_task_1.__airplane.description == "description"  # type: ignore

    # Description provided in docstring is the default
    @task()
    def my_task_2() -> None:
        """Docstring"""

    assert my_task_2.__airplane.description == "Docstring"  # type: ignore


def test_param_configs() -> None:
    @task()
    def my_task(
        required: int,
        annotated: Annotated[
            int,
            ParamConfig(
                name="Annotated Name",
                description="annotated description",
                options=[1, 2, 3],
            ),
        ],
        optional: Optional[int],
        annotated_optional: Annotated[Optional[int], ParamConfig()],
        default: int = 1,
        annotated_default: Annotated[
            int,
            ParamConfig(
                options=[LabeledOption("label", 1), LabeledOption("label2", 2)]
            ),
        ] = 1,
    ) -> None:
        """My task description

        Args:
            required: required description
            Annotated: check that this is overriden
        """
        del (
            required,
            annotated,
            optional,
            annotated_optional,
            default,
            annotated_default,
        )

    assert my_task.__airplane == TaskDef(  # type: ignore
        func=my_task.__wrapped__,  # type: ignore
        runtime="",
        slug="my_task",
        name="My task",
        description="My task description",
        require_requests=False,
        allow_self_approvals=False,
        timeout=3600,
        constraints=None,
        schedules=None,
        resources=None,
        parameters=[
            ParamDef(
                arg_name="required",
                slug="required",
                name="Required",
                type="integer",
                description="required description",
                default=None,
                required=True,
                options=None,
                regex=None,
            ),
            ParamDef(
                arg_name="annotated",
                slug="annotated",
                name="Annotated Name",
                type="integer",
                description="annotated description",
                default=None,
                required=True,
                options=[
                    LabeledOption(label="1", value=1),
                    LabeledOption(label="2", value=2),
                    LabeledOption(label="3", value=3),
                ],
                regex=None,
            ),
            ParamDef(
                arg_name="optional",
                slug="optional",
                name="Optional",
                type="integer",
                description=None,
                default=None,
                required=False,
                options=None,
                regex=None,
            ),
            ParamDef(
                arg_name="annotated_optional",
                slug="annotated_optional",
                name="Annotated optional",
                type="integer",
                description=None,
                default=None,
                required=False,
                options=None,
                regex=None,
            ),
            ParamDef(
                arg_name="default",
                slug="default",
                name="Default",
                type="integer",
                description=None,
                default=1,
                required=False,
                options=None,
                regex=None,
            ),
            ParamDef(
                arg_name="annotated_default",
                slug="annotated_default",
                name="Annotated default",
                type="integer",
                description=None,
                default=1,
                required=False,
                options=[LabeledOption("label", 1), LabeledOption("label2", 2)],
                regex=None,
            ),
        ],
        env_vars=None,
        entrypoint_func="my_task",
    )


def test_str_param() -> None:
    @task()
    def my_task(
        required: str,
        required_long: LongText,
        required_sql: SQL,
        optional: Optional[str] = "foo",
        default: Annotated[
            str,
            ParamConfig(
                options=["foo", "bar"],
            ),
        ] = "foo",
    ) -> None:
        del (
            required,
            optional,
            default,
        )

    assert my_task.__airplane.parameters == [  # type: ignore
        ParamDef(
            arg_name="required",
            slug="required",
            name="Required",
            type="shorttext",
            description=None,
            default=None,
            required=True,
            options=None,
            regex=None,
        ),
        ParamDef(
            slug="required_long",
            arg_name="required_long",
            name="Required long",
            type="longtext",
            description=None,
            default=None,
            required=True,
            options=None,
            regex=None,
        ),
        ParamDef(
            slug="required_sql",
            arg_name="required_sql",
            name="Required sql",
            type="sql",
            description=None,
            default=None,
            required=True,
            options=None,
            regex=None,
        ),
        ParamDef(
            slug="optional",
            arg_name="optional",
            name="Optional",
            type="shorttext",
            description=None,
            default="foo",
            required=False,
            options=None,
            regex=None,
        ),
        ParamDef(
            slug="default",
            arg_name="default",
            name="Default",
            type="shorttext",
            description=None,
            default="foo",
            required=False,
            options=[
                LabeledOption(label="foo", value="foo"),
                LabeledOption(label="bar", value="bar"),
            ],
            regex=None,
        ),
    ]


def test_date_param() -> None:
    @task(
        schedules=[
            Schedule(
                slug="slug",
                cron="* * * * *",
                param_values={
                    "required": datetime.date(
                        2019,
                        1,
                        1,
                    )
                },
            )
        ],
    )
    def my_task(
        required: datetime.date,
        optional: Optional[datetime.date] = datetime.date(2019, 8, 5),
        default: Annotated[
            datetime.date,
            ParamConfig(
                options=[datetime.date(2019, 8, 5), datetime.date(2019, 8, 6)],
            ),
        ] = datetime.date(2019, 8, 5),
        default_labeled: Annotated[
            datetime.date,
            ParamConfig(
                options=[
                    LabeledOption(label="foo", value=datetime.date(2019, 8, 5)),
                    LabeledOption(label="bar", value=datetime.date(2019, 8, 6)),
                ],
            ),
        ] = datetime.date(2019, 8, 5),
    ) -> None:
        del (
            required,
            optional,
            default,
            default_labeled,
        )

    assert my_task.__airplane.schedules == [  # type: ignore
        Schedule(
            slug="slug",
            cron="* * * * *",
            name=None,
            description=None,
            param_values={"required": "2019-01-01"},
        )
    ]
    assert my_task.__airplane.parameters == [  # type: ignore
        ParamDef(
            slug="required",
            arg_name="required",
            name="Required",
            type="date",
            description=None,
            default=None,
            required=True,
            options=None,
            regex=None,
        ),
        ParamDef(
            slug="optional",
            arg_name="optional",
            name="Optional",
            type="date",
            description=None,
            default="2019-08-05",
            required=False,
            options=None,
            regex=None,
        ),
        ParamDef(
            slug="default",
            arg_name="default",
            name="Default",
            type="date",
            description=None,
            default="2019-08-05",
            required=False,
            options=[
                LabeledOption(label="2019-08-05", value="2019-08-05"),
                LabeledOption(label="2019-08-06", value="2019-08-06"),
            ],
            regex=None,
        ),
        ParamDef(
            slug="default_labeled",
            arg_name="default_labeled",
            name="Default labeled",
            type="date",
            description=None,
            default="2019-08-05",
            required=False,
            options=[
                LabeledOption(label="foo", value="2019-08-05"),
                LabeledOption(label="bar", value="2019-08-06"),
            ],
            regex=None,
        ),
    ]


def test_datetime_param() -> None:
    @task()
    def my_task(
        required: datetime.datetime,
        optional: Optional[datetime.datetime] = datetime.datetime(2019, 8, 5),
        default: Annotated[
            datetime.datetime,
            ParamConfig(
                options=[datetime.datetime(2019, 8, 5), datetime.datetime(2019, 8, 6)],
            ),
        ] = datetime.datetime(2019, 8, 5),
        default_labeled: Annotated[
            datetime.datetime,
            ParamConfig(
                options=[
                    LabeledOption(label="foo", value=datetime.datetime(2019, 8, 5)),
                    LabeledOption(label="bar", value=datetime.datetime(2019, 8, 6)),
                ],
            ),
        ] = datetime.datetime(2019, 8, 5),
    ) -> None:
        del (
            required,
            optional,
            default,
            default_labeled,
        )

    assert my_task.__airplane.parameters == [  # type: ignore
        ParamDef(
            slug="required",
            arg_name="required",
            name="Required",
            type="datetime",
            description=None,
            default=None,
            required=True,
            options=None,
            regex=None,
        ),
        ParamDef(
            slug="optional",
            arg_name="optional",
            name="Optional",
            type="datetime",
            description=None,
            default="2019-08-05T00:00:00Z",
            required=False,
            options=None,
            regex=None,
        ),
        ParamDef(
            slug="default",
            arg_name="default",
            name="Default",
            type="datetime",
            description=None,
            default="2019-08-05T00:00:00Z",
            required=False,
            options=[
                LabeledOption(
                    label="2019-08-05T00:00:00Z", value="2019-08-05T00:00:00Z"
                ),
                LabeledOption(
                    label="2019-08-06T00:00:00Z", value="2019-08-06T00:00:00Z"
                ),
            ],
            regex=None,
        ),
        ParamDef(
            slug="default_labeled",
            arg_name="default_labeled",
            name="Default labeled",
            type="datetime",
            description=None,
            default="2019-08-05T00:00:00Z",
            required=False,
            options=[
                LabeledOption(label="foo", value="2019-08-05T00:00:00Z"),
                LabeledOption(label="bar", value="2019-08-06T00:00:00Z"),
            ],
            regex=None,
        ),
    ]


def test_configvar_param() -> None:
    @task()
    def my_task(
        required: ConfigVar,
        optional: Optional[ConfigVar] = ConfigVar(name="foo", value="bar"),
        default: Annotated[
            ConfigVar,
            ParamConfig(
                options=[
                    ConfigVar(name="foo", value="bar"),
                    ConfigVar(name="baz", value="ban"),
                ],
            ),
        ] = ConfigVar(name="foo", value="bar"),
        default_labeled: Annotated[
            ConfigVar,
            ParamConfig(
                options=[
                    LabeledOption(
                        label="foo", value=ConfigVar(name="foo", value="bar")
                    ),
                    LabeledOption(
                        label="bar", value=ConfigVar(name="baz", value="ban")
                    ),
                ],
            ),
        ] = ConfigVar(name="foo", value="bar"),
    ) -> None:
        del (
            required,
            optional,
            default,
            default_labeled,
        )

    assert my_task.__airplane.parameters == [  # type: ignore
        ParamDef(
            slug="required",
            arg_name="required",
            name="Required",
            type="configvar",
            description=None,
            default=None,
            required=True,
            options=None,
            regex=None,
        ),
        ParamDef(
            slug="optional",
            arg_name="optional",
            name="Optional",
            type="configvar",
            description=None,
            default="foo",
            required=False,
            options=None,
            regex=None,
        ),
        ParamDef(
            slug="default",
            arg_name="default",
            name="Default",
            type="configvar",
            description=None,
            default="foo",
            required=False,
            options=[
                LabeledOption(label="foo", value="foo"),
                LabeledOption(label="baz", value="baz"),
            ],
            regex=None,
        ),
        ParamDef(
            slug="default_labeled",
            arg_name="default_labeled",
            name="Default labeled",
            type="configvar",
            description=None,
            default="foo",
            required=False,
            options=[
                LabeledOption(label="foo", value="foo"),
                LabeledOption(label="bar", value="baz"),
            ],
            regex=None,
        ),
    ]


def test_errors() -> None:
    with pytest.raises(InvalidAnnotationException, match=r"Missing type annotation.*"):

        @task()
        def no_annotation(param):  # type: ignore
            del param

    with pytest.raises(InvalidAnnotationException, match=r"Invalid type annotation.*"):

        @task()
        def unsupported_annotation(param: Dict[str, str]):  # type: ignore
            del param

    with pytest.raises(InvalidAnnotationException, match=r"Unsupported Union.*"):

        @task()
        def unsupported_union(param: Union[str, int]):  # type: ignore
            del param

    with pytest.raises(
        InvalidAnnotationException, match=r"Found multiple ParamConfig.*"
    ):

        @task()
        def multiple_param_configs(param: Annotated[str, ParamConfig(), ParamConfig()]):  # type: ignore
            del param

    with pytest.raises(
        UnsupportedDefaultTypeException, match=r"File defaults are not.*"
    ):

        @task()
        def unsupported_default(param: File = File("foo", "bar")):  # type: ignore
            del param

    with pytest.raises(
        InvalidTaskConfigurationException, match=r"Environment variable name*"
    ):
        EnvVar(name="foo=bar")

    with pytest.raises(InvalidTaskConfigurationException, match=r"Exactly one of*"):
        EnvVar(name="foo", config_var_name="foo", value="foo")

    with pytest.raises(InvalidTaskConfigurationException, match=r"Exactly one of*"):
        EnvVar(name="foo")

    with pytest.raises(
        InvalidTaskConfigurationException, match=r"has duplicate parameter slugs*"
    ):

        @task()
        def duplicate_param_slugs(
            param: str, param2: Annotated[str, ParamConfig(slug="param")]
        ) -> None:
            del param, param2

    with pytest.raises(
        InvalidTaskConfigurationException, match=r"has duplicate schedule slugs*"
    ):

        @task(
            schedules=[
                Schedule(slug="foo", cron="* * * * *"),
                Schedule(slug="foo", cron="* * * * *"),
            ]
        )
        def duplicate_schedule_slugs() -> None:
            pass

    with pytest.raises(
        InvalidTaskConfigurationException, match=r"has duplicate env var names*"
    ):

        @task(
            env_vars=[
                EnvVar(name="foo", value="bar"),
                EnvVar(name="foo", value="baz"),
            ]
        )
        def duplicate_env_var_names() -> None:
            pass


def test_run() -> None:
    @task()
    def my_task(
        int_: int,
        file: File,
        intNonDefaultSlug: int,  # pylint: ignore=invalid-name
        str_optional: Optional[str],
        int_default: int = 1,
        config_var: ConfigVar = ConfigVar("name", "value"),
        date: datetime.date = datetime.date(2019, 1, 1),
        date_time: datetime.datetime = datetime.datetime(2019, 1, 1, 1),
    ) -> Dict[str, Any]:
        return {
            "int_": int_,
            "file": file,
            "intNonDefaultSlug": intNonDefaultSlug,
            "str_optional": str_optional,
            "int_default": int_default,
            "config_var": config_var,
            "date": date,
            "date_time": date_time,
        }

    res = my_task.__airplane.run(  # type: ignore
        {
            "int": 10,
            "file": {
                "__airplaneType": "upload",
                "id": "upload_id",
                "url": "upload_url",
            },
            "int_non_default_slug": 11,
        }
    )
    assert res == {
        "int_": 10,
        "file": File("upload_id", "upload_url"),
        "intNonDefaultSlug": 11,
        "str_optional": None,
        "int_default": 1,
        "config_var": ConfigVar("name", "value"),
        "date": datetime.date(2019, 1, 1),
        "date_time": datetime.datetime(2019, 1, 1, 1),
    }

    res = my_task.__airplane.run(  # type: ignore
        {
            "int": 10,
            "file": {
                "__airplaneType": "upload",
                "id": "upload_id",
                "url": "upload_url",
            },
            "int_non_default_slug": 11,
            "int_default": 123,
            "date": "2010-10-10",
        }
    )
    assert res == {
        "int_": 10,
        "file": File("upload_id", "upload_url"),
        "intNonDefaultSlug": 11,
        "str_optional": None,
        "int_default": 123,
        "config_var": ConfigVar("name", "value"),
        "date": datetime.date(2010, 10, 10),
        "date_time": datetime.datetime(2019, 1, 1, 1),
    }


@pytest.mark.parametrize(
    "string,expected",
    [
        # no-op
        ("test", "test"),
        # removes casing
        ("TEST", "test"),
        # trims leading/trailing special characters
        ("-a-", "a"),
        # trims all whitespace
        (
            " test that it trims space\t ",
            "test_that_it_trims_space",
        ),
        # removes special characters
        ("foo-–—―&@%bar", "foo_and_at_percent_bar"),
        # trims underscores
        ("_test_foo_bar_", "test_foo_bar"),
        # truncates long strings
        ("a" * 100, "a" * 50),
        # trim duplicate __'s
        ("test____test", "test_test"),
    ],
)
def test_make_slug(string: str, expected: str) -> None:
    assert make_slug(string) == expected
