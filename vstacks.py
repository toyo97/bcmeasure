from ij import VirtualStack, ImageStack, IJ
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


def get_cells_vstacks(stack, markers, cube_dim, scaleZ=1.0):
    # type: (ImageStack, list, int, float) -> list
    """
Generate a list of CellVirtualStack containing all the cells in the stack pointed by the markers
    :param stack: Stack of the original image

    :param markers: list of lists, 3D points of the centers

    :param cube_dim: Dimension of the cube roi around the cell

    :param scaleZ: Depth of a voxel (1 if image is isotropic, less otherwise)

    :return list of CellVirtualStack
    """
    cells_vstacks = []
    # for each marker append the virtual stack crop of the cell to cells_vstacks
    for xc, yc, zc in markers:
        IJ.log('Processing cell at {},{},{} ...'.format(xc, yc, zc))
        cells_vstacks.append(CellVirtualStack(stack, xc, yc, zc, cube_dim, scaleZ))
    return cells_vstacks


class CellVirtualStack(VirtualStack):
    def __init__(self, stack, xc, yc, zc, dim, scaleZ=1):
        # type: (ImageStack, int, int, int, int, float) -> CellVirtualStack
        """
Constructor of the VirtualStack pointing to the cell at the given coordinates

        :param stack: ij.ImageStack, Stack of the original image

        :param xc: X coord of the cell center

        :param yc: Y coord of the cell center

        :param zc: Z coord of the cell center

        :param dim: Dimension of the cube roi around the cell

        :param scaleZ: Depth of a voxel (1 if image is isotropic, less otherwise)
        """
        self.z_start, size = calculate_slices(stack, zc, int(dim * scaleZ))
        self.cell_roi = square_roi(xc, yc, dim)

        # set width and height according to actual roi crop (which may differ from cell_roi dimensions)
        ip = stack.getProcessor(1)
        ip.setRoi(self.cell_roi)
        crop = ip.crop()
        width = crop.getWidth()
        height = crop.getHeight()

        # attribute to identify cells on image borders
        if width != dim or height != dim or size != int(dim * scaleZ):
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
        :return: List of 3D coords
        """
        return [self.xc, self.yc, self.zc]