from mcib3d.image3d import ImageHandler
from mcib3d.image3d.processing import MaximaFinder

from stacks import CellStack
from neigh import nearest_neighborhood, neighborhood_mean


def local_max(cs, seed):
    # type: (CellStack, list) -> list
    """
Search for the local maximum around the seed

    :param cs: CellStack in which to search

    :param seed: starting 3D point in list of coordinates

    :return: 3D coordinates of the local max in stack
    """

    max_v = cs.get_voxel(seed)
    max_pos = seed
    new_max_found = True
    while new_max_found:
        new_max_found = False
        for pos in nearest_neighborhood(max_pos):
            try:
                v = cs.get_voxel(pos)
                if v > max_v:
                    max_pos = pos
                    max_v = v
                    new_max_found = True
            except IndexError as e:
                pass

    return max_pos


def local_mean(cellstack, r0, r1, r2, weight=0.5):
    # type: (CellStack, int, int, int, float) -> float
    """
Calculate a threshold value computing the center/background mean and weighting the sum
Reference at: https://github.com/mcib3d/mcib3d-core/blob/master/src/main/java/mcib3d/image3d/Segment3DSpots.java

    :param cellstack: Image as CellStack

    :param r0: Radius of the center (estimate)

    :param r1: Radius of the background. It's calculated as the spherical cap between r0 and r1

    :param weight: Weight of the center mean

    :return: Wighted mean
    """
    mspot = neighborhood_mean(cellstack, r0)
    print('Mean spot: ' + str(mspot))
    mback = neighborhood_mean(cellstack, r2, r1)
    print('Mean back: ' + str(mback))
    return mspot * weight + (1 - weight) * mback


def find_maxima(cs, rad, thresh):
    # type: (CellStack, int, float) -> list
    """
Find maxima in the entire stack with given radius. Exclude peaks below thresh

    :param cs: CellStack

    :param rad: Maxima search radius

    :param thresh: Intensity threshold

    :return: List of maxima 3D coordinates
    """

    imh = ImageHandler.wrap(cs.duplicate())
    radXY = rad
    radZ = rad * cs.scaleZ

    # in MaximaFinder thresh is the noise tolerance value
    mf = MaximaFinder(imh, radXY, radZ, thresh)
    peaks_array = mf.getListPeaks()
    peaks = []
    # check toArray() call functioning
    for p in peaks_array.toArray():
        if p.getValue() >= thresh:
            point = p.getPosition()
            peaks.append([l for l in point.getArray()])

    peaks_list = list(map(lambda x: [int(i) for i in x], peaks))
    peaks_list.append(cs.center)
    return peaks_list

