"""gedisens: compare vertical forest structure from ALS and GEDI LiDAR."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gedisens")
except PackageNotFoundError:  # running from a source checkout
    __version__ = "unknown"
