from ij import ImagePlus

import utils


def gen_cell_stacks(imp, seeds, cube_dim, scaleZ=1.0):
    """
Generate all the cells stacks in the given image at the given coordinates (seeds)
    """
    for pos in seeds:
        yield CellStack(imp, pos[0], pos[1], pos[2], cube_dim, scaleZ)


def relative_center(xc, yc, zc, roi_3D):
    # type: (int, int, int, dict) -> list
    """
Calculate the center of the cell relatively to its roi

    :param roi_3D: region of interest of the cell obtained with dump_3DRoi()

    :return: 3D coordinates
    """
    return [xc - roi_3D['x0'], yc - roi_3D['y0'], zc - roi_3D['z0']]


def dump_3DRoi(imp, xc, yc, zc, dim, scaleZ=1.):
    # type: (ImagePlus, int, int, int, int, float) -> dict
    """
Create a dict for rapid access to stack dimensions

    :param scaleZ: Depth of a voxel (1 if image is isotropic, less otherwise)

    :return: dict, Key values are: x0, y0, z0, width, height, depth
    """
    x0 = xc - int(dim / 2)
    y0 = yc - int(dim / 2)
    z0 = zc - int(dim * scaleZ / 2)

    x0 = x0 if x0 >= 0 else 0
    y0 = y0 if y0 >= 0 else 0
    z0 = z0 if z0 >= 0 else 0

    # Returns the dimensions of this image (width, height, nChannels, nSlices, nFrames) as a 5 element int array
    dimensions = imp.getDimensions()
    imp_width = dimensions[0]
    imp_height = dimensions[1]
    imp_depth = dimensions[3]

    w = dim if x0 + dim - 1 < imp_width else imp_width - x0
    h = dim if y0 + dim - 1 < imp_height else imp_height - y0
    d = int(dim * scaleZ) if z0 + int(dim * scaleZ) - 1 < imp_depth else imp_depth - z0
    # z0 is the z coordinate, NOT the slice (slices go from 1 to stack size)

    roi = {
        'x0': x0,
        'y0': y0,
        'z0': z0,
        'width': w,
        'height': h,
        'depth': d
    }
    return roi


def is_on_border(roi3D, dim, scaleZ):
    if dim == roi3D['width'] and dim == roi3D['height'] and dim*scaleZ == roi3D['depth']:
        return False
    else:
        return True


class CellStack(ImagePlus):
    def __init__(self, imp, xc, yc, zc, dim, scaleZ=1.):
        # type: (ImagePlus, int, int, int, int, float) -> CellStack
        """
ImagePlus containing one cell as stack

        :param imp: Original ImageJ ImagePlus

        :param xc: X coord of the cell center

        :param yc: Y coord of the cell center

        :param zc: Z coord of the cell center

        :param dim: Dimension of the cube roi around the cell

        :param scaleZ: Depth of a voxel (1 if image is isotropic)
        """
        self.dim = dim
        self.seed = [xc, yc, zc]
        self.roi3D = dump_3DRoi(imp, xc, yc, zc, dim, scaleZ)
        self.center = relative_center(xc, yc, zc, self.roi3D)
        self.scaleZ = scaleZ
        self.onBorder = is_on_border(self.roi3D, dim, scaleZ)

        title = str(self.seed) + ' in ' + imp.title
        stack = imp.getImageStack().crop(self.roi3D['x0'],
                                         self.roi3D['y0'],
                                         self.roi3D['z0'],
                                         self.roi3D['width'],
                                         self.roi3D['height'],
                                         self.roi3D['depth'])
        super(ImagePlus, self).__init__(title, stack)

    def contains(self, pos):

        w = self.roi3D['width']
        h = self.roi3D['height']
        d = self.roi3D['depth']

        if 0 <= pos[0] < w and 0 <= pos[1] < h and 0 <= pos[2] < d:
            return True
        else:
            return False

    def get_voxel(self, pos):
        if self.contains(pos):
            self.setPosition(pos[2] + 1)
            return self.getPixel(pos[0], pos[1])[0]
        else:
            raise IndexError("3D coordinates out of bounds")

    def get_stats(self, weight=0.5, recenter=True):

        # find local max around seed (naive method)
        stats = {'loc_max': utils.local_max(self, self.center)}

        if recenter:
            self.center = stats['loc_max']

        # compute weighted local mean to find a thresh value
        stats['loc_mean'] = utils.local_mean(self, 20, 50, weight)

        # compute 3D radial distribution
        tab = utils.radial_distribution_3D(self, 40)
        stats['rad3D'] = tab

        # compute radius
        radius = utils.radius_thresh(tab, stats['loc_mean'])
        stats['radius'] = radius

        return stats










