from org.python.modules import math

from stacks import CellStack
from mcib3d.image3d import ImageHandler
from mcib3d.geom import Point3D


def euclid_distance(x, xi, scaleZ):
    return math.sqrt((x[0]-xi[0])**2 + (x[1]-xi[1])**2 + (x[2]-xi[2])**2 / scaleZ**2)


def gaussian_kernel(distance, bandwidth):
    val = (1/(bandwidth*math.sqrt(2*math.pi))) * math.exp(-0.5 * (distance / bandwidth) ** 2)
    return val


def mean_shift(cs, radius, peaks, sigma, thresh):
    # type: (CellStack, int, list, float, float) -> list

    imh = ImageHandler.wrap(cs)

    # copy peaks list
    X = list(peaks)

    past_X = []
    n_iterations = 20
    for it in range(n_iterations):
        for i, x in enumerate(X):
            point_x = Point3D(x[0], x[1], x[2])

            # for each point x in X, find the neighboring points N(x) of x.
            neighbors = imh.getNeighborhoodLayerList(x[0], x[1], x[2], 0, radius)

            # for each point x in X, calculate the mean shift m(x).
            numerator = [0]*3
            denominator = 0
            neigh_arr = neighbors.toArray()

            for neighbor in neigh_arr:
                # discard neighbors below certain thresh
                if neighbor.getValue() >= thresh:

                    # neighbor is a Voxel3D Object, getPosition is a Point3D. For reference,
                    # see https://github.com/mcib3d/mcib3d-core/blob/master/src/main/java/mcib3d/geom/Voxel3D.java

                    neigh_pos = [p for p in neighbor.getPosition().getArray()]
                    distance = point_x.distance(neighbor)
                    weight = gaussian_kernel(distance, sigma)
                    inc = list(map(lambda n: n*(weight * neighbor.getValue()), neigh_pos))
                    numerator = list(map(lambda a, b: a+b, numerator, inc))
                    denominator += weight*neighbor.getValue()

            # print("Denominator: " + str(denominator))
            new_x = list(map(lambda n: int(n/denominator), numerator))

            # for each point x in X, update x = m(x).
            X[i] = new_x

        past_X.append(list(X))

    return X


def ms_center(cs, radius, peaks, sigma, thresh):
    # type: (CellStack, int, list, float, float) -> list

    print('[msc] Peaks: ' + str(peaks))
    centroids = mean_shift(cs, radius, peaks, sigma, thresh)
    print('[msc] Centroids: ' + str(centroids))
    dist = list(map(lambda x: euclid_distance(x, cs.center, cs.scaleZ), centroids))
    min_d = min(dist)
    index = 0
    for i, d in enumerate(dist):
        if d == min_d:
            index = i
            break

    return centroids[index]
