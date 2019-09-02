from ij import IJ
from ij.plugin import GaussianBlur3D, Filters3D
from stacks import CellStack


def gaussianIJ(cs, xysigma):
    # type: (CellStack, float) -> None
    """
Perform ImageJ gaussian blur 3D with same sigma along x and y axes on a CellStack
    """
    zsigma = cs.scaleZ * xysigma
    GaussianBlur3D.blur(cs, xysigma, xysigma, zsigma)


def medianIJ(cs, xysigma):
    # type: (CellStack, float) -> None
    """
Perform ImageJ median filter 3D with same sigma along x and y axes on a CellStack (locally)
    """
    stack = cs.getImageStack()
    new_stack = Filters3D.filter(stack, Filters3D.MEDIAN, xysigma, xysigma, xysigma * cs.scaleZ)
    cs.setStack(new_stack)


def meanIJ(cs, xysigma):
    # type: (CellStack, float) -> None
    """
Perform ImageJ mean filter 3D with same sigma along x and y axes on a CellStack (locally)
    """
    stack = cs.getImageStack()
    new_stack = Filters3D.filter(stack, Filters3D.MEAN, xysigma, xysigma, xysigma * cs.scaleZ)
    cs.setStack(new_stack)


def filter_cellstack(cs, method, sigma):
    # type: (CellStack, str, float) -> None
    """
Perform the requested filter

    :param cs: CellStack

    :param method: name of filter, can be 'gauss', 'mean' or 'median'

    :param sigma: sigma value along xy axis (on the z axis it is self-computed using CellStack z scale value)
    """
    if method == 'gauss':
        gaussianIJ(cs, sigma)
    elif method == 'mean':
        meanIJ(cs, sigma)
    elif method == 'median':
        medianIJ(cs, sigma)
    else:
        IJ.error('Filter not valid: ' + method + '\nImage not filtered')
