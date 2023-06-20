from typing_extensions import Annotated

import airplane


@airplane.task(resources=[airplane.Resource("demo_db", alias="db")])
def python_sdk_standard(name: str = "") -> str:
    """This task uses the standard Python SDK to execute a SQL query and display the results."""
    print(f"Looking up companies like '{name}'")
    run = airplane.sql.query(
        "db",
        """
        select id, company_name from accounts
        where (company_name ilike :name or id::text ilike :name)
        order by company_name
        """,
        query_args={"name": f"%{name}%"},
    )
    companies = run.output["Q1"]

    airplane.display.text(f"Found **{len(companies)}** companies.")
    airplane.display.json(companies)
    airplane.display.table(
        companies,
        columns=[
            airplane.display.TableColumn(name="ID", slug="id"),
            airplane.display.TableColumn(name="Name", slug="company_name"),
        ],
    )

    if len(companies) == 0:
        raise Exception("Found no companies")  # pylint: disable=broad-exception-raised
    if len(companies) == 1:
        return companies[0]

    values = airplane.prompt(
        {
            "company": Annotated[
                str,
                airplane.ParamConfig(
                    options=[
                        airplane.LabeledOption(c["company_name"], c["id"])
                        for c in companies
                    ]
                ),
            ]
        }
    )
    return values["company"]
