import textwrap
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Union

import deprecation

from airplane._version import __version__
from airplane.api.client import api_client_from_env


def text(content: str, dedent: bool = True) -> None:
    """Appends a display to the run that renders the provided markdown text.

    See the [CommonMark docs](https://commonmark.org/help/) for an introduction
    to markdown formatting.

    Args:
        content: Text to render as markdown
        dedent: Whether or not to omit leading whitespace from content.

    Raises:
        HTTPError: If the display could not be created.
    """
    if dedent:
        content = textwrap.dedent(content)
    api_client_from_env().create_text_display(content)


@deprecation.deprecated(
    deprecated_in="0.3.14",
    current_version=__version__,
    details="Use text(content, dedent) instead.",
)
def markdown(content: str, dedent: bool = True) -> None:
    """Appends a display to the run that renders the provided markdown text.

    See the [CommonMark docs](https://commonmark.org/help/) for an introduction
    to markdown formatting.

    Args:
        content: Text to render as markdown
        dedent: Whether or not to omit leading whitespace from content.

    Raises:
        HTTPError: If the display could not be created.
    """
    text(content, dedent)


def json(
    payload: Union[Dict[str, Any], List[Any], int, str, float, bool, None],
) -> None:
    """Appends a display to the run that renders a JSON payload.

    Args:
        payload: JSON payload to render

    Raises:
        HTTPError: If the display could not be created.
    """
    api_client_from_env().create_json_display(payload)


@dataclass(frozen=True)
class TableColumn:
    """Column for a table display.

    Attributes:
        slug: Identifier used to reference this column.
        name: Column display name. Defaults to slug.
    """

    slug: str
    name: Optional[str] = None


def table(
    rows: List[Dict[str, Any]], columns: Optional[List[Union[str, TableColumn]]] = None
) -> None:
    """Appends a display to the run that renders a table.

    Each row should be an object mapping header slugs to values. Columns that are not
    specified will default to `null`. The selection, ordering, and naming of columns
    can be customized via `opts.columns`.

    Args:
        rows:
            The list of rows to render in the table.
        columns:
            The list of columns to include in the table.

            The order of columns in this list determines the order of columns when rendering the
            table. Each column can optionally specify a human-readable name that will be used when
            rendering the table. The name defaults to the slug.

            Columns found in `rows` that not included in `columns` will not be rendered.

            If not specified, columns are inferred automatically from the provided rows:
            - The set of columns is the union of all keys across all rows.
            - The column order is inferred from the key order of the first row. All other columns
              not present in the first row are ordered after.
            - Columns are named by their slug.

    Raises:
        HTTPError: If the display could not be created.
        ValueError: If columns have empty or duplicate slugs.
    """
    table_columns: List[TableColumn]
    if columns is None:
        # Use a list to maintain dict key order.
        slugs = []
        all_slugs = set()
        for row in rows:
            for key in row.keys():
                if key not in all_slugs:
                    slugs.append(key)
                    all_slugs.add(key)
        table_columns = [TableColumn(slug=s) for s in slugs]
    else:
        table_columns = [
            TableColumn(slug=column) if isinstance(column, str) else column
            for column in columns
        ]
        if any(c.slug == "" for c in table_columns):
            raise ValueError("Column slugs cannot be empty")
        slug_set = {c.slug for c in table_columns}
        if len(columns) != len(slug_set):
            raise ValueError("Column slugs must be unique")
        rows = _filter_row_keys(rows, slug_set)
    api_client_from_env().create_table_display(
        columns=[{"slug": c.slug, "name": c.name} for c in table_columns], rows=rows
    )


def _filter_row_keys(
    rows: List[Dict[str, Any]], columns: Set[str]
) -> List[Dict[str, Any]]:
    filtered_rows = []
    for row in rows:
        filtered_rows.append(dict((c, row[c]) for c in columns if c in row))
    return filtered_rows
