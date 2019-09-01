from ij import ImagePlus


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
    x0 = max(xc - int(dim / 2), 0)
    y0 = max(yc - int(dim / 2), 0)
    z0 = max(zc - int(dim * scaleZ / 2), 0)

    # Returns the dimensions of this image (width, height, nChannels, nSlices, nFrames) as a 5 element int array
    dimensions = imp.getDimensions()
    imp_width = dimensions[0]
    imp_height = dimensions[1]
    imp_depth = dimensions[3]

    x1 = min(xc + int(dim / 2), imp_width)
    y1 = min(yc + int(dim / 2), imp_height)
    z1 = min(zc + int(dim * scaleZ / 2), imp_depth)

    w = x1 - x0
    h = y1 - y0
    d = z1 - z0
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
        # type: (list) -> bool
        """
    Handy method to check if a 3D point is inside the cell stack

        :param pos: Point to be checked

        :return: True if the point is contained
        """
        w = self.roi3D['width']
        h = self.roi3D['height']
        d = self.roi3D['depth']

        if 0 <= pos[0] < w and 0 <= pos[1] < h and 0 <= pos[2] < d:
            return True
        else:
            return False

    def get_voxel(self, pos):
        # type: (list) -> int
        """
    Random access to any voxel inside the cell stack

        :param pos: 3D coordinates of the requested voxel

        :return: Voxel intensity (int value)

        :raise: IndexError if coordinates out of cell stack
        """
        if self.contains(pos):
            self.setPosition(pos[2] + 1)
            return self.getPixel(pos[0], pos[1])[0]
        else:
            raise IndexError("3D coordinates out of bounds")

    def set_calibration(self):
        """
    Set pixel depth value according to default value scaleZ
    NOTE: to be clear, pixelDepth >= 1, scaleZ <= 1 (the latter is the proportion resZ/resXY -res := resolution-)
        """
        cal = self.getCalibration()
        cal.pixelDepth = 1 / self.scaleZ











