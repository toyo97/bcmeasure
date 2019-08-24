import os

from ij import IJ, ImagePlus, ImageStack
from ij.plugin import filter, GaussianBlur3D, Zoom, Filters3D
import markers as mrk
from stacks import get_cells_vstacks

xysigma = 2
zsigma = 1


def gaussianIJ(stack, xysigma, zsigma):
    # type: (ImageStack, float, float) -> ImagePlus
    """
Perform ImageJ gaussian blur 3D with same sigma along x and y axes on a copy of the given ImageStack
    """
    imp = ImagePlus('stack copy', stack.duplicate())
    GaussianBlur3D.blur(imp, xysigma, xysigma, zsigma)
    return imp.getImageStack()


def medianIJ(stack, xysigma, zsigma):
    # type: (ImageStack, float, float) -> ImageStack
    """
Perform ImageJ median filter 3D with same sigma along x and y axes on a copy of the given ImageStack
    """
    new_stack = Filters3D.filter(stack, Filters3D.MEDIAN, xysigma, xysigma, zsigma)
    return new_stack


def meanIJ(stack, xysigma, zsigma):
    # type: (ImageStack, float, float) -> ImageStack
    """
Perform ImageJ mean filter 3D with same sigma along x and y axes on a copy of the given ImageStack
    """
    new_stack = Filters3D.filter(stack, Filters3D.MEAN, xysigma, xysigma, zsigma)
    return new_stack


# filter testing
if __name__ == '__main__':
    img_path = '/home/zemp/bcfind_GT/SST_11_12.tif'
    img_name, img_ext = os.path.splitext(img_path)
    marker_path = img_name + '.csv'

    imp = IJ.openImage(img_path)
    imp.show()

    markers = mrk.read_marker(marker_path, to_int=True)

    cells_vstacks = get_cells_vstacks(imp.getImageStack(), markers, 70, 0.4)
    for vstack in cells_vstacks:
        cell_imp = ImagePlus('Cell at {}'.format(vstack.get_center()), vstack)
        cell_imp.setSlice(int(vstack.getSize() / 2))
        cell_imp.show()
        IJ.run("Set... ", "zoom=600")

        # stack = ImageStack(vstack.width, vstack.height, vstack.getSize())
        # for i in range(1, vstack.getSize() + 1):
        #     stack.addSlice(vstack.getProcessor(i))

        new_stack = gaussianIJ(vstack, xysigma, zsigma)
        new_imp = ImagePlus('[blur3d] Cell at {}'.format(vstack.get_center()), new_stack)
        new_imp.setSlice(int(vstack.getSize() / 2))
        new_imp.show()
        IJ.run("Set... ", "zoom=600")

        raw_input('Press enter to continue...')
        cell_imp.close()
        new_imp.close()
