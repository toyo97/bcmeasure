from mcib3d.image3d import ImageHandler


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


def neighborhood_mean(cs, r1, r0=0):
    # type: (CellStack, int, int) -> float
    """
Returns the mean of the values inside a sphere (or sphere cap if r0 != 0 provided) around the center
Reference at: https://github.com/mcib3d/mcib3d-core/blob/master/src/main/java/mcib3d/image3d/ImageHandler.java

    :param r1: external radius

    :param r0: internal radius (if sphere cap it must be gt 0)
    """
    imh = ImageHandler.wrap(cs)

    if r0 == 0:
        neigh = imh.getNeighborhoodSphere(cs.center[0], cs.center[1], cs.center[2], r1, r1, r1*cs.scaleZ)
        mean = neigh.getMean()
    else:
        neigh = imh.getNeighborhoodLayer(cs.center[0], cs.center[1], cs.center[2], r0, r1)
        mean = neigh.getMean()

    return mean
