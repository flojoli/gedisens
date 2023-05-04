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

def df_out(df,out_path):
    """saves dataframe as shapefile.

    Args:

        df (pandas dataframe): dataframe.

        out_path (string): str for the output path.

    """

    df = gpd.GeoDataFrame(df)
    df.to_file(out_path + ".shp")

