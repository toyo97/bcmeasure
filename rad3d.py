from ij.gui import Plot

from neigh import neighborhood_mean
from stacks import CellStack


def radial_distribution_3D(cs, max_rad):
    # type: (CellStack, int) -> list
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
