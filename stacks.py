from ij import VirtualStack, ImageStack, IJ, ImagePlus
from ij.gui import Roi


def square_roi(xc, yc, dim):
    # type: (int, int, int) -> Roi
    """
Generate the square (2D) ij.gui.Roi centered in (xc,yc) with given side size
NOTE: It can go out of the original image border!
    """
    x = xc - int(dim / 2)
    y = yc - int(dim / 2)
    # Roi corrects itself if out of borders when set on image
    return Roi(x, y, dim, dim)


def calculate_slices(stack, zc, depth):
    # type: (ImageStack, int, int) -> (int, int)
    """
Calculate the starting slice and the size of the stack
    :param stack: ij.ImageStack, Stack of the original image
    :param zc: Z index of the cell center
    :param depth: Depth of the resulting stack
    :return: Starting slice and size
    """
    z0 = zc - int(depth / 2)
    z0 = z0 if z0 >= 1 else 1

    z1 = zc + int(depth / 2)
    z1 = z1 if z1 <= stack.getSize() else stack.getSize()
    return z0, z1 - z0 + 1


def get_cells_vstacks(stack, markers, cube_dim, voxel_depth=1.0):
    cells_vstacks = []
    # for each marker append the virtual stack crop of the cell to cells_vstacks
    for xc, yc, zc in markers:
        IJ.log('Processing cell at {},{},{} ...'.format(xc, yc, zc))
        cells_vstacks.append(CellVirtualStack(stack, xc, yc, zc, cube_dim, voxel_depth))
    return cells_vstacks


class CellVirtualStack(VirtualStack):
    def __init__(self, stack, xc, yc, zc, dim, voxel_depth=1):
        # type: (ImageStack, int, int, int, int, float) -> CellVirtualStack
        """
Constructor of the VirtualStack pointing to the cell at the given coordinates
        :param stack: ij.ImageStack, Stack of the original image
        :param xc: X coord of the cell center
        :param yc: Y coord of the cell center
        :param zc: Z coord of the cell center
        :param dim: Dimension of the cube roi around the cell
        """
        self.z_start, size = calculate_slices(stack, zc, int(dim * voxel_depth))
        self.cell_roi = square_roi(xc, yc, dim)

        # set width and height according to actual roi crop (which may differ from cell_roi dimensions)
        ip = stack.getProcessor(1)
        ip.setRoi(self.cell_roi)
        crop = ip.crop()
        width = crop.getWidth()
        height = crop.getHeight()

        # attribute to identify cells on image borders
        if width != dim or height != dim or size != int(dim * voxel_depth):
            self.onBorder = True
        else:
            self.onBorder = False

        super(VirtualStack, self).__init__(width, height, size)

        self.stack = stack
        self.xc = xc
        self.yc = yc
        self.zc = zc

    def getProcessor(self, n):
        # Modify the same slice at index n every time it is requested
        z = self.z_index(n)
        ip = self.stack.getProcessor(z)
        ip.setRoi(self.cell_roi)
        crop = ip.crop()
        return crop

    def z_index(self, n):
        """
Calculates the slice corresponding to the original stack
        :param n: Requested index (from 1 to nSlices)
        """
        return self.z_start + n - 1

    def get_center(self):
        """
Cell center coordinates
        :return: list of 3D coords
        """
        return [self.xc, self.yc, self.zc]


# *** Non-Virtual CellStack ***

def gen_cell_stacks(imp, markers, cube_dim, voxel_depth=1.0):
    for pos in markers:
        yield CellStack(imp, pos[0], pos[1], pos[2], cube_dim, voxel_depth)


def relative_center(xc, yc, zc, roi_3D):
    # type: (int, int, int, dict) -> list
    """
Calculate the center of the cell relatively to its roi
    :param roi_3D: region of interest of the cell obtained with dump_3DRoi()
    :return: 3D coordinates
    """
    return [xc - roi_3D['x0'], yc - roi_3D['y0'], zc - roi_3D['z0']]


def dump_3DRoi(imp, xc, yc, zc, dim, voxel_depth):
    # type: (ImagePlus, int, int, int, int, float) -> dict
    """
Create a dict for rapid access to stack dimensions
    :param imp: i
    :param xc:
    :param yc:
    :param zc:
    :param dim:
    :param voxel_depth: depth of a voxel (1 if image is isotropic)
    :return: dict, key values are: x0, y0, z0, width, height depth
    """
    x0 = xc - int(dim / 2)
    y0 = yc - int(dim / 2)
    z0 = zc - int(dim*voxel_depth / 2)

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
    d = int(dim*voxel_depth) if z0 + int(dim*voxel_depth) - 1 < imp_depth else imp_depth - z0
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


class CellStack(ImagePlus):
    def __init__(self, imp, xc, yc, zc, dim, voxel_depth=1.):
        # type: (ImagePlus, int, int, int, int, float) -> CellStack
        self.seed = [xc, yc, zc]
        self.roi3D = dump_3DRoi(imp, xc, yc, zc, dim, voxel_depth)
        self.center = relative_center(xc, yc, zc, self.roi3D)

        title = 'Cell in ' + str(self.seed)
        stack = imp.getImageStack().crop(self.roi3D['x0'],
                                         self.roi3D['y0'],
                                         self.roi3D['z0'],
                                         self.roi3D['width'],
                                         self.roi3D['height'],
                                         self.roi3D['depth'])
        super(ImagePlus, self).__init__(title, stack)













