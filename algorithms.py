import os

import markers as mrk
from ij import IJ, ImagePlus, ImageStack, ImageJ
from net.imglib2 import RandomAccess
from net.imglib2.img.display.imagej import ImageJFunctions as IL

from stacks import get_cells_vstacks


# TODO define method to obtain local coordinates in cell stacks that are partially out of image borders
#  (i.e. CellStack.onBorder == True)


def get_ra_pos(r):
    # type: (RandomAccess) -> list
    """
Shorthand to obtain the position of a ImgLib2 RandomAccess
    """
    return [r.getIntPosition(0), r.getIntPosition(1), r.getIntPosition(2)]


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


def local_max(stack, seed):
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


# NN testing
if __name__ == '__main__':
    ImageJ()
    img_path = '/home/zemp/bcfind_GT/SST_11_12.tif'
    img_name, img_ext = os.path.splitext(img_path)
    marker_path = img_name + '.csv'
    markers = mrk.read_marker(marker_path, to_int=True)

    imp = IJ.openImage(img_path)
    cells_vstacks = get_cells_vstacks(imp.getImageStack(), markers, 70, 0.4)

    cell_imp = stack = None
    for cell in cells_vstacks:
        if not cell.onBorder:
            stack = cell
            cell_imp = ImagePlus('cell at {}'.format(stack.get_center()), stack)
            cell_imp.show()
            break

    img = IL.wrap(imp)
    r2 = img.randomAccess()
    r2.setPosition(stack.get_center())
    print('Seed val: {}'.format(r2.get()))

    cell_img = IL.wrap(cell_imp)
    r = cell_img.randomAccess()
    r.setPosition([35, 35, 14])

    print(r.get())
    print(local_max(stack, [35, 35, 14]))
