"""A builder factory."""

from . import builder, naive, ukkonen, mccreight


def builder_factory(name: str = None) -> type[builder.Builder]:
    """Return the specified builder (default: ukkonen)."""
    if name == "naive":
        return naive.Builder
    if name == "mccreight":
        return mccreight.Builder
    return ukkonen.Builder


BUILDERS = ["naive", "ukkonen", "mccreight"]
