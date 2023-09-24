"""A builder factory."""

from typing import Type

from . import builder, naive, mccreight, ukkonen


def builder_factory(name: str = "mccreight") -> Type[builder.Builder]:
    """Return the specified builder (default: mccreight)."""
    if name == "mccreight":
        return mccreight.Builder
    if name == "ukkonen":
        return ukkonen.Builder
    if name == "naive":
        return naive.Builder
    return mccreight.Builder


BUILDERS = ["naive", "mccreight", "ukkonen"]
