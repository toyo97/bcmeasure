from ij import IJ
from ij.gui import OvalRoi
from ij.plugin import LutLoader
from ij.process import LUT
from ij.process import StackStatistics
from java.awt import Color

from stacks import CellStack


def apply_lut(cs, cmap):
    # type: (CellStack, str) -> None
    """
Apply a different Look Up Table according to the given cmap name

    :param cmap: Can be 'fire'
    """
    stats = StackStatistics(cs)
    ll = LutLoader()
    if cmap == 'fire':
        cm = ll.open('luts/fire.lut')
        # print("Stats.max " + str(stats.max))
        lut = LUT(cm, stats.min, stats.max)
        cs.setLut(lut)
    else:
        IJ.error('Invalid color map: ' + cmap + '\nDefault LUT applied')


def circle_roi(cs, r, color):
    # type: (CellStack, int, Color) -> None
    """
Draw a circle roi with center and radius of the cell
    """
    d = r * 2
    x, y = cs.center[0] - r, cs.center[1] - r
    roi = OvalRoi(x, y, d, d)
    roi.setColor(color)
    cs.setRoi(roi)
