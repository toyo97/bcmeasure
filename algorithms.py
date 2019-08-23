import os

import markers as mrk
from ij import IJ
from net.imglib2 import KDTree, RealPoint, RealRandomAccess, RealRandomAccessible
from net.imglib2.img.display.imagej import ImageJFunctions as IL


if __name__=='__main__':
    img_path = '/home/zemp/bcfind_GT/SST_11_12.tif'
    img_name, img_ext = os.path.splitext(img_path)
    marker_path = img_name+'.csv'
    markers = mrk.read_marker(marker_path, to_int=True)

    imp = IJ.openImage(img_path)

    img = IL.wrapReal(imp)

    r = img.randomAccess()
    r.setPosition(markers[0])
    print(markers[0])
    print(r.get())
