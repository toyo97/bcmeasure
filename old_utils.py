import os

import markers as mrk
from ij import IJ, ImagePlus, ImageStack, ImageJ
from net.imglib2 import RandomAccess
from net.imglib2.img.display.imagej import ImageJFunctions as IL
from ij.plugin import LutLoader
from ij.process import LUT, StackStatistics

from filters import gaussianIJ, medianIJ, meanIJ
from stacks import CellStack, gen_cell_stacks
from utils import local_max, local_mean
from rad3d import radial_distribution_3D, radius_thresh
from neigh import nearest_neighborhood


def get_ra_pos(r):
    # type: (RandomAccess) -> list
    """
Shorthand to obtain the position of a ImgLib2 RandomAccess
    """
    return [r.getIntPosition(0), r.getIntPosition(1), r.getIntPosition(2)]


def local_max_imglib2(stack, seed):
    # type: (ImageStack, list) -> list
    """
Search for the local maximum around the seed

    :param stack: ImageStack in which to search

    :param seed: starting 3D point in list of coordinates

    :return: 3D coordinates of the local max in stack
    """

    # ImageJ ImagePlus image
    imp = ImagePlus(str(seed), stack)
    # wrapped in an ImgLib2 Img
    img = IL.wrap(imp)
    r = img.randomAccess()

    # r is an ImgLib2 Sampler which initially points to seed
    r.setPosition(seed)
    max_r = r.copyRandomAccess()
    new_max_found = True
    while new_max_found:
        max_pos = get_ra_pos(max_r)
        new_max_found = False
        for pos in nearest_neighborhood(max_pos):
            try:
                r.setPosition(pos)
                curr = r.get()
                if curr > max_r.get():
                    max_r = r.copyRandomAccess()
                    new_max_found = True
            except:
                # border neighborhood
                pass
        max_pos = get_ra_pos(max_r)
    return max_pos


def neighborhood_mean_imglib2(cellstack, r1, r0=0):
    # type: (CellStack, int, int) -> float
    """
Returns the mean of the values inside a sphere (or sphere cap if r0 != 0 provided) around the center
Reference at: https://github.com/mcib3d/mcib3d-core/blob/master/src/main/java/mcib3d/image3d/ImageHandler.java

    :param r1: external radius

    :param r0: internal radius (if sphere cap it must be gt 0)
    """
    pix = []
    scale_z = cellstack.scaleZ
    ratio = 1 / scale_z
    ratio2 = ratio * ratio
    x = cellstack.center[0]
    y = cellstack.center[1]
    z = cellstack.center[2]

    w = cellstack.roi3D['width']
    h = cellstack.roi3D['height']
    d = cellstack.roi3D['depth']
    rz = int(r1 * scale_z)

    img = IL.wrap(cellstack)
    ra = img.randomAccess()
    sum = 0
    count = 0
    for k in range(z - rz, x + rz + 1):
        for j in range(y - r1, y + r1 + 1):
            for i in range(x - r1, x + r1 + 1):
                if 0 <= i < w and 0 <= j < h and 0 <= k < d:
                    dist = ((x - i) * (x - i)) + ((y - j) * (y - j)) + ((z - k) * (z - k) * ratio2)
                    if r1 * r1 >= dist >= r0 * r0:
                        ra.setPosition([i, j, k])
                        sum += int(ra.get())
                        count += 1

    return sum / count


# *** TESTING ***

def test_local_max_easy():
    ImageJ()

    img_path = '/home/zemp/bcfind_GT/SST_11_12.tif'
    img_name, img_ext = os.path.splitext(img_path)
    marker_path = img_name + '.csv'
    markers = mrk.read_marker(marker_path, to_int=True)

    imp = IJ.openImage(img_path)

    for cs in gen_cell_stacks(imp, markers, 70, 0.4):
        if not cs.onBorder:
            v = cs.get_voxel(cs.center)
            print('Seed {} {}'.format(cs.center, v))

            sigma = 2
            # gaussianIJ(cs, sigma)
            meanIJ(cs, sigma)
            # medianIJ(cs, sigma)

            loc_max = local_max(cs, cs.center)
            print('Local max {} {}'.format(loc_max, cs.get_voxel(loc_max)))
            cs.center = loc_max

            loc_mean = local_mean(cs, 20, 50, 0.7)
            print('Local mean: ' + str(loc_mean))

            # TODO implement radialDistribution using neighborhood mean
            #  see https://github.com/mcib3d/mcib3d-core/blob/master/src/main/java/mcib3d/image3d/ImageHandler.java

            tab = radial_distribution_3D(cs, 40)
            print(tab[:30])

            radius = radius_thresh(tab, loc_mean)
            print('Radius: '+str(radius))

            stats = StackStatistics(cs)
            ll = LutLoader()
            cm = ll.open('luts/fire.lut')
            print(cm)
            lut = LUT(cm, stats.min, stats.max)
            cs.setLut(lut)
            cs.show()

            break


if __name__ == '__main__':
    test_local_max_easy()
