import pandas as pd
import geopandas as gpd

def shp2df(fn):
    """Reads data from file assuming shapefile format.

    Args:

        fn (shapefile): Filename of file containing the data.

    Returns: pandas dataframe containing the data.

    """

    gdf = gpd.read_file(fn)

    df = pd.DataFrame(gdf)

    return df
