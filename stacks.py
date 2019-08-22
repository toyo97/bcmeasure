from ij import VirtualStack, ImageStack
from ij.gui import Roi


def square_roi(xc, yc, dim):
    x = xc - int(dim/2)
    y = yc - int(dim/2)
    # Roi corrects itself when out of borders
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


class CellStack(VirtualStack):
    def __init__(self, stack, xc, yc, zc, dim, voxel_depth=1):
        # type: (ImageStack, int, int, int, int, float) -> CellStack
        """
Constructor of the VirtualStack pointing to the cell at the given coordinates
        :param stack: ij.ImageStack, Stack of the original image
        :param xc: X coord of the cell center
        :param yc: Y coord of the cell center
        :param zc: Z coord of the cell center
        :param dim: Dimension of the cube roi around the cell
        """
        self.z_start, size = calculate_slices(stack, zc, dim*voxel_depth)
        self.cell_roi = square_roi(xc, yc, dim)
        width = int(self.cell_roi.getFloatWidth())
        height = int(self.cell_roi.getFloatHeight())
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
        return ip.crop()

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
