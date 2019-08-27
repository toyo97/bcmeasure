from ij import IJ
from ij.gui import OvalRoi, Plot
from ij.plugin import LutLoader
from ij.process import StackStatistics, LUT
from mcib3d.image3d import ImageHandler

import stacks


def nearest_neighborhood(center):
    # type: (list) -> list
    """
Generates the 26 neighbors of a given 3D point (center excluded)
    """
    interval = [-1, 0, 1]

    for dz in interval:
        for dy in interval:
            for dx in interval:
                if not (dx == 0 and dy == 0 and dz == 0):
                    yield [center[0] + dx, center[1] + dy, center[2] + dz]


def local_max(cs, seed):
    # type: (stacks.CellStack, list) -> list
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


def neighborhood_mean(cs, r1, r0=0):
    # type: (stacks.CellStack, int, int) -> float
    """
Returns the mean of the values inside a sphere (or sphere cap if r0 != 0 provided) around the center
Reference at: https://github.com/mcib3d/mcib3d-core/blob/master/src/main/java/mcib3d/image3d/ImageHandler.java

    :param r1: external radius

    :param r0: internal radius (if sphere cap it must be gt 0)
    """
    cal = cs.getCalibration()
    cal.pixelDepth = 1 / cs.scaleZ

    imh = ImageHandler.wrap(cs)

    if r0 == 0:
        neigh = imh.getNeighborhoodSphere(cs.center[0], cs.center[1], cs.center[2], r1, r1, r1*cs.scaleZ)
        mean = neigh.getMean()
    else:
        neigh = imh.getNeighborhoodLayer(cs.center[0], cs.center[1], cs.center[2], r0, r1)
        mean = neigh.getMean()

    return mean


def local_mean(cellstack, r0, r1, weight=0.5):
    # type: (stacks.CellStack, int, int, float) -> float
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
    mback = neighborhood_mean(cellstack, r1, r0)
    print('Mean back: ' + str(mback))
    return mspot * weight + (1 - weight) * mback


def radial_distribution_3D(cs, max_rad):
    # type: (stacks.CellStack, int) -> list
    """
Compute the 3D radial distribution in the given radius
Reference https://github.com/mcib3d/mcib3d-core/blob/master/src/main/java/mcib3d/image3d/ImageHandler.java

    :return: Values of (half) the gaussian in list of length max_rad+1
    """
    tab = []
    for r in range(max_rad + 1):
        mean = neighborhood_mean(cs, r + 1, r)
        tab.append(mean)

    return tab


def plot_rad3d(tab):
    r = len(tab) - 1
    idx = list(range(-r, r + 1))
    val = tab[::-1] + tab[1:]

    return Plot("3D radial distribution", "rad", "mean", idx, val)


def radius_thresh(rad3d, thresh):
    # type: (list, float) -> int
    """
Find the radius of the cell from the 3D radial distribution counting the values above the given threshold

    :param rad3d: Radial distribution obtained with radial_distribution_3D

    :param thresh: Threshold value

    :return: Radius
    """
    r = 0
    for r, v in enumerate(rad3d):
        if v < thresh:
            break

    return r


def apply_lut(cs, cmap):
    # type: (stacks.CellStack, str) -> None
    """
Apply a different Look Up Table according to the given cmap name

    :param cmap: Can be 'fire'
    """
    stats = StackStatistics(cs)
    ll = LutLoader()
    if cmap == 'fire':
        cm = ll.open('luts/fire.lut')
        lut = LUT(cm, stats.min, stats.max)
        cs.setLut(lut)
    else:
        IJ.error('Invalid color map: ' + cmap + '\nDefault LUT applied')


def circle_roi(cs, r):
    # type: (stacks.CellStack, int) -> None
    """
Draw a circle roi with center and radius of the cell
    """
    d = r * 2
    x, y = cs.center[0] - r, cs.center[1] - r
    cs.setRoi(OvalRoi(x, y, d, d))
