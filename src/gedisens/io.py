"""Reading and writing vector data."""

from pathlib import Path

import geopandas as gpd


def read_vector(fn):
    """Reads data from a vector file (shapefile, GeoPackage, ...).

    Args:

        fn (str or Path): filename of file containing the data.

    Returns: geopandas dataframe containing the data, Shot_Numbe as str.

    """
    gdf = gpd.read_file(fn)
    if "Shot_Numbe" in gdf.columns:
        gdf["Shot_Numbe"] = gdf["Shot_Numbe"].astype(str)
    return gdf


def write_vector(df, out_path):
    """Saves dataframe as GeoPackage.

    GeoPackage is used instead of shapefile so long column names such as
    upper_percentage are kept.

    Args:

        df (geopandas dataframe): data with geometry.

        out_path (str or Path): output file, .gpkg is added if no suffix
                                is given.

    Returns: path of the written file.

    """
    out_path = Path(out_path)
    if not out_path.suffix:
        out_path = out_path.with_suffix(".gpkg")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    gpd.GeoDataFrame(df).to_file(out_path)
    return out_path
