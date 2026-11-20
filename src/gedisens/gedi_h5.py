"""Reading information from GEDI HDF5 granules (L1B, L2A, L2B).

The functions expect an opened file, e.g. ``h5py.File(path)``.
Install h5py with ``pip install gedisens[h5]``.
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)

GEDI_BEAMS = (
    "BEAM0000",
    "BEAM0001",
    "BEAM0010",
    "BEAM0011",
    "BEAM0101",
    "BEAM0110",
    "BEAM1000",
    "BEAM1011",
)


def get_beam(shot_number, h5):
    """Looks for the beam with which shot was obtained.

    Args:

        shot_number (int): GEDI shot number.

        h5 (hdf5): opened GEDI granule.

    Returns: string of beam name for given shot number, None if the shot
             is not in the file.

    """
    shot_number = np.uint64(shot_number)
    for beam in GEDI_BEAMS:
        if beam in h5 and shot_number in h5[beam]["shot_number"][:]:
            return beam
    logger.info("Shot %s not found in %s.", shot_number, h5)
    return None


def get_structure_params(shot_number, h5, layer):
    """Get pavd, pai or cover for ONE gedi shot.

    L2B files passed to function in order to check in which file the
    shot number can be found.

    Args:

        shot_number (int): GEDI shot number.

        h5 (hdf5): opened L2B file containing pavd, pai, canopy cover.

        layer (str): which feature to get: pavd, pai or cover.

    Returns: list with shot number, shot elevation, feature and fhd for
             each height bin, None if the shot is not in the file.

    """
    shot_number = np.uint64(shot_number)
    beam = get_beam(shot_number, h5)
    if beam is None:
        return None

    grp = h5[beam]
    idx = int(np.flatnonzero(grp["shot_number"][:] == shot_number)[0])
    elev = grp["geolocation/elev_lowestmode"][idx]
    profile = grp[f"{layer}_z"][idx]
    fhd = grp["fhd_normal"][idx]
    dz = grp["ancillary/dz"][0]

    return [
        (shot_number, elev + dz * i, value, fhd)
        for i, value in enumerate(profile)
    ]
