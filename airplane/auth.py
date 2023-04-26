from airplane.api.client import api_client_from_env


def id_token(audience: str) -> str:
    """Generates a short-lived ID token from Airplane's OpenID Connect provider.

    These short-lived ID tokens can be used to "prove" their identity and authenticate
    with a target API (such as AWS, GCP, or your own API). ID tokens contain subject and claim
    information specific to the task and runner.

    https://docs.airplane.dev/platform/oidc

    Args:
        audience: Intended audience for the token.

    Raises:
        HTTPError: If the ID token could not be created.
    """
    return api_client_from_env().generate_id_token(audience)
