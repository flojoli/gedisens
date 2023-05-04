import numpy as np
import pandas as pd

def get_beam(shot_number,h5):
    """Looks for the beam with which shot was obtained.

    Args:

        shot_number (int)

        h5 (hdf5)

    Returns: string of beam name for given shot number

    """

    for beam in ["BEAM0000","BEAM0001","BEAM0010","BEAM0011",
                 "BEAM0101","BEAM0110","BEAM1000","BEAM1011"]:

        if shot_number in h5[beam]['shot_number'][:]:
            break

        else:
            print("Beam: not found and set to nan.")
            beam = np.nan
            continue

    return beam


def _get_waveform_series(df,dz,data_name):
    """Creates a pandas series with x and y data.

       function can only handle dataframe with single shot.

    Args:

        df (pandas dataframe): pandas dataframe containing data.

        dz (int): integer containing vertical step size.

        data_src (str): either Amp or Pulse

    Returns: dataframe with x and y axis values

    """

    x_vector = [df.iloc[:1, i].values[0]
                for i in range(1, len(df.columns))]
    x_vector = pd.Series(x_vector, name=data_name)

    y_vector = [(dz * i) + dz/2
                  for i in range(1, len(df.columns))]
    y_vector = pd.Series(y_vector, name="Elevation")

    return x_vector, y_vector


def get_structure_params(shot_number, h5, layer):
    """Get pavd, pai or cover for ONE gedi shot.

       L2B files passed to function in order to check in which file the
       shotnumber can be found

    Args:

        shot_number (uint64): converted to np.unit64

        h5 (h5 file): file containing pavd,pai, canopy cover

        feature (str) : string of which feature to get
                        pavd, pai, cover

    Returns: list with shot number, shot elevation, feature

    """

    # do we really need that?
    shot_number = np.uint64(shot_number)

    layer = f"{layer}_z"

    try:
        beam = get_beam(shot_number, h5)
        # get index of shot
        shot_number_id = list(
            h5[beam]["shot_number"][:]).index(shot_number)

        shotElev = h5[beam]["geolocation/elev_lowestmode"][()][shot_number_id]
        shotLats = h5[beam]["geolocation/lat_lowestmode"][()][shot_number_id]
        shotLons = h5[beam]["geolocation/lon_lowestmode"][()
                                                              ][shot_number_id]
        shotLayer = h5[beam][layer][()][shot_number_id]
        shotFHD = h5[beam]["fhd_normal"][()][shot_number_id]
        dz = h5[beam]["ancillary/dz"][0]
        structure_param = []

        for i, e in enumerate(range(len(shotLayer))):
            # Append tuple of shot number, elevation, and PAVD
            structure_param.append(
                (shot_number,  shotElev + dz * i, shotLayer[i], shotFHD))

        return structure_param

    except:
        print("next file")

    return

def get_max_height(df):
    """Determines upper and lower boundary of max height of profile.
    
    For Layer calculation RH90 is used as max height.

    Args: 

        df (pandas dataframe): pandas dataframe containing data.  
    
    Returns: dataframe with upper and lower bound of upper 5/6.
        
    """

    df["max_height_upper"] = df.RH_90.round().astype(int)
    df["max_height_lower"] = np.ceil(df.max_height_upper * 5/6).astype(int)

    return df

