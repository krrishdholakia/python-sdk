import inflection
from slugify import slugify  # type: ignore


def make_slug(string: str) -> str:
    """Turns a string into a slug"""
    for target, replacement in [
        ("‒", "_"),  # figure dash
        ("–", "_"),  # en dash
        ("—", "_"),  # em dash
        ("―", "_"),  # horizontal bar
        ("&", "_and_"),
        ("@", "_at_"),
        ("%", "_percent_"),
    ]:
        string = string.replace(target, replacement)
    return slugify(inflection.underscore(string)).replace("-", "_")[:50]
