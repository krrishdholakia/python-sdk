from typing import Any, Dict, List, Optional, cast

from typing_extensions import TypedDict

from airplane.api.entities import BuiltInRun
from airplane.builtins import __convert_resource_alias_to_id
from airplane.runtime import __execute_internal


def find(
    mongodb_resource: str,
    collection: str,
    filter: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
    projection: Optional[Dict[str, Any]] = None,
    sort: Optional[Dict[str, Any]] = None,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
) -> BuiltInRun[List[Dict[str, Any]]]:
    """Runs the find function against a MongoDB Airplane resource.

    Args:
        mongodb_resource: The alias of the MongoDB resource to use.
        collection: The collection to search in.
        filter: The query predicate.
        projection: The projection specification that determines which fields to return.
        sort: The sort specification for the ordering of the results.
        skip: Number of documents to skip.
        limit: The maximum number of documents to return.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the find builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[List[Dict[str, Any]]],
        __execute_internal(
            "airplane:mongodb_find",
            {
                "collection": collection,
                "filter": filter,
                "projection": projection,
                "sort": sort,
                "skip": skip,
                "limit": limit,
            },
            {"db": __convert_resource_alias_to_id(mongodb_resource)},
        ),
    )


def find_one(
    mongodb_resource: str,
    collection: str,
    filter: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
    projection: Optional[Dict[str, Any]] = None,
    sort: Optional[Dict[str, Any]] = None,
) -> BuiltInRun[Optional[Dict[str, Any]]]:
    """Runs the findOne function against a MongoDB Airplane resource.

    Args:
        mongodb_resource: The alias of the MongoDB resource to use.
        collection: The collection to search.
        filter: The query predicate.
        projection: The projection specification that determines which fields to return.
        sort: The sort specification for the ordering of the results.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the findOne builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[Optional[Dict[str, Any]]],
        __execute_internal(
            "airplane:mongodb_findOne",
            {
                "collection": collection,
                "filter": filter,
                "projection": projection,
                "sort": sort,
            },
            {"db": __convert_resource_alias_to_id(mongodb_resource)},
        ),
    )


def find_one_and_delete(
    mongodb_resource: str,
    collection: str,
    filter: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
    projection: Optional[Dict[str, Any]] = None,
    sort: Optional[Dict[str, Any]] = None,
) -> BuiltInRun[Optional[Dict[str, Any]]]:
    """Runs the findOneAndDelete function against a MongoDB Airplane resource.

    Args:
        mongodb_resource: The alias of the MongoDB resource to use.
        collection: The collection to search in.
        filter: The query predicate.
        projection: The projection specification that determines which fields to return.
        sort: The sort specification for the ordering of the results.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the findOneAndDelete builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[Optional[Dict[str, Any]]],
        __execute_internal(
            "airplane:mongodb_findOneAndDelete",
            {
                "collection": collection,
                "filter": filter,
                "projection": projection,
                "sort": sort,
            },
            {"db": __convert_resource_alias_to_id(mongodb_resource)},
        ),
    )


def find_one_and_update(
    mongodb_resource: str,
    collection: str,
    update: Dict[str, Any],
    filter: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
    projection: Optional[Dict[str, Any]] = None,
    sort: Optional[Dict[str, Any]] = None,
) -> BuiltInRun[Optional[Dict[str, Any]]]:
    """Runs the findOneAndUpdate function against a MongoDB Airplane resource.

    Args:
        mongodb_resource: The alias of the MongoDB resource to use.
        collection: The collection to search in.
        update: The update document.
        filter: The query predicate.
        projection: The projection specification that determines which fields to return.
        sort: The sort specification for the ordering of the results.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the findOneAndUpdate builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[Optional[Dict[str, Any]]],
        __execute_internal(
            "airplane:mongodb_findOneAndUpdate",
            {
                "collection": collection,
                "update": update,
                "filter": filter,
                "projection": projection,
                "sort": sort,
            },
            {"db": __convert_resource_alias_to_id(mongodb_resource)},
        ),
    )


def find_one_and_replace(
    mongodb_resource: str,
    collection: str,
    replacement: Dict[str, Any],
    filter: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
    projection: Optional[Dict[str, Any]] = None,
    sort: Optional[Dict[str, Any]] = None,
    upsert: Optional[bool] = None,
) -> BuiltInRun[Optional[Dict[str, Any]]]:
    """Runs the findOneAndReplace function against a MongoDB Airplane resource.

    Args:
        mongodb_resource: The alias of the MongoDB resource to use.
        collection: The collection to search in.
        replacement: The replacement document.
        filter: The query predicate.
        projection: The projection specification that determines which fields to return.
        sort: The sort specification for the ordering of the results.
        upsert: Replaces the document or inserts the replacement if no document is found.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the findOneAndReplace builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[Optional[Dict[str, Any]]],
        __execute_internal(
            "airplane:mongodb_findOneAndReplace",
            {
                "collection": collection,
                "replacement": replacement,
                "filter": filter,
                "projection": projection,
                "sort": sort,
                "upsert": upsert,
            },
            {"db": __convert_resource_alias_to_id(mongodb_resource)},
        ),
    )


class InsertOneOutput(TypedDict):
    """The output of the mongodb.insert_one builtin."""

    InsertedID: str


def insert_one(
    mongodb_resource: str,
    collection: str,
    document: Dict[str, Any],
) -> BuiltInRun[InsertOneOutput]:
    """Runs the insertOne function against a MongoDB Airplane resource.

    Args:
        mongodb_resource: The alias of the MongoDB resource to use.
        collection: The collection to insert in.
        document: The document to insert.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the insertOne builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[InsertOneOutput],
        __execute_internal(
            "airplane:mongodb_insertOne",
            {
                "collection": collection,
                "document": document,
            },
            {"db": __convert_resource_alias_to_id(mongodb_resource)},
        ),
    )


class InsertManyOutput(TypedDict):
    """The output of the mongodb.insert_many builtin."""

    InsertedIDs: List[str]


def insert_many(
    mongodb_resource: str,
    collection: str,
    documents: List[Dict[str, Any]],
) -> BuiltInRun[InsertManyOutput]:
    """Runs the insertMany function against a MongoDB Airplane resource.

    Args:
        mongodb_resource: The alias of the MongoDB resource to use.
        collection: The collection to insert in.
        documents: The documents to insert.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the insertMany builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[InsertManyOutput],
        __execute_internal(
            "airplane:mongodb_insertMany",
            {
                "collection": collection,
                "documents": documents,
            },
            {"db": __convert_resource_alias_to_id(mongodb_resource)},
        ),
    )


class UpdateOutput(TypedDict):
    """The output of the mongodb.update_one and mongodb.udpate_many builtins."""

    MatchedCount: int
    ModifiedCount: int
    UpsertedCount: int
    UpsertedID: Optional[str]


def update_one(
    mongodb_resource: str,
    collection: str,
    update: Dict[str, Any],
    filter: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
    upsert: Optional[bool] = None,
) -> BuiltInRun[UpdateOutput]:
    """Runs the updateOne function against a MongoDB Airplane resource.

    Args:
        mongodb_resource: The alias of the MongoDB resource to use.
        collection: The collection to update in.
        update: The update document.
        filter: The query predicate.
        upsert: Updates the document or inserts the update if no document is found.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the updateOne builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[UpdateOutput],
        __execute_internal(
            "airplane:mongodb_updateOne",
            {
                "collection": collection,
                "update": update,
                "filter": filter,
                "upsert": upsert,
            },
            {"db": __convert_resource_alias_to_id(mongodb_resource)},
        ),
    )


def update_many(
    mongodb_resource: str,
    collection: str,
    update: Dict[str, Any],
    filter: Optional[Dict[str, Any]] = None,  # pylint: disable=redefined-builtin
    upsert: Optional[bool] = None,
) -> BuiltInRun[UpdateOutput]:
    """Runs the updateMany function against a MongoDB Airplane resource.

    Args:
        mongodb_resource: The alias of the MongoDB resource to use.
        collection: The collection to update in.
        update: The update document.
        filter: The query predicate.
        upsert: Updates the documents or inserts the update if no document is found.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the updateMany builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[UpdateOutput],
        __execute_internal(
            "airplane:mongodb_updateMany",
            {
                "collection": collection,
                "update": update,
                "filter": filter,
                "upsert": upsert,
            },
            {"db": __convert_resource_alias_to_id(mongodb_resource)},
        ),
    )


class DeleteOutput(TypedDict):
    """The output of the mongodb.delete_one and mongodb.delete_many builtins."""

    DeletedCount: int


def delete_one(
    mongodb_resource: str,
    collection: str,
    filter: Dict[str, Any],  # pylint: disable=redefined-builtin
) -> BuiltInRun[DeleteOutput]:
    """Runs the deleteOne function against a MongoDB Airplane resource.

    Args:
        mongodb_resource: The alias of the MongoDB resource to use.
        collection: The collection to delete in.
        filter: The query predicate.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the deleteOne builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[DeleteOutput],
        __execute_internal(
            "airplane:mongodb_deleteOne",
            {
                "collection": collection,
                "filter": filter,
            },
            {"db": __convert_resource_alias_to_id(mongodb_resource)},
        ),
    )


def delete_many(
    mongodb_resource: str,
    collection: str,
    filter: Dict[str, Any],  # pylint: disable=redefined-builtin
) -> BuiltInRun[DeleteOutput]:
    """Runs the deleteMany function against a MongoDB Airplane resource.

    Args:
        mongodb_resource: The alias of the MongoDB resource to use.
        collection: The collection to delete in.
        filter: The query predicate.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the deleteMany builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[DeleteOutput],
        __execute_internal(
            "airplane:mongodb_deleteMany",
            {
                "collection": collection,
                "filter": filter,
            },
            {"db": __convert_resource_alias_to_id(mongodb_resource)},
        ),
    )


def aggregate(
    mongodb_resource: str,
    collection: str,
    pipeline: List[Dict[str, Any]],
) -> BuiltInRun[List[Dict[str, Any]]]:
    """Runs the aggregate function against a MongoDB Airplane resource.

    Args:
        mongodb_resource: The alias of the MongoDB resource to use.
        collection: The collection to aggregate in.
        pipeline: The sequence of data aggregation operations.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the aggregate builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[List[Dict[str, Any]]],
        __execute_internal(
            "airplane:mongodb_aggregate",
            {
                "collection": collection,
                "pipeline": pipeline,
            },
            {"db": __convert_resource_alias_to_id(mongodb_resource)},
        ),
    )


def count_documents(
    mongodb_resource: str,
    collection: str,
    filter: Dict[str, Any],  # pylint: disable=redefined-builtin
) -> BuiltInRun[float]:
    """Runs the countDocuments function against a MongoDB Airplane resource.

    Args:
        mongodb_resource: The alias of the MongoDB resource to use.
        collection: The collection to count in.
        filter: The query predicate.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the countDocuments builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[float],
        __execute_internal(
            "airplane:mongodb_countDocuments",
            {
                "collection": collection,
                "filter": filter,
            },
            {"db": __convert_resource_alias_to_id(mongodb_resource)},
        ),
    )


def distinct(
    mongodb_resource: str,
    collection: str,
    field: str,
    filter: Dict[str, Any],  # pylint: disable=redefined-builtin
) -> BuiltInRun[List[Any]]:
    """Runs the distinct function against a MongoDB Airplane resource.

    Args:
        mongodb_resource: The alias of the MongoDB resource to use.
        collection: The collection to search.
        field: The field for which to return distinct values.
        filter: The query predicate.

    Returns:
        The id, task id, param values, status and outputs of the executed run.

    Raises:
        HTTPError: If the distinct builtin cannot be executed properly.
        RunTerminationException: If the run fails or is cancelled.
    """

    return cast(
        BuiltInRun[List[Any]],
        __execute_internal(
            "airplane:mongodb_distinct",
            {
                "collection": collection,
                "field": field,
                "filter": filter,
            },
            {"db": __convert_resource_alias_to_id(mongodb_resource)},
        ),
    )
