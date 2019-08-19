from __future__ import with_statement, print_function
import csv
import os
from ij import IJ, ImagePlus
from ij.gui import PointRoi

source_path = '/home/zemp/IdeaProjects/bcmeasure/input/'

for filename in os.listdir(source_path):
    if filename.endswith(".tif"):
        file_path = os.path.join(source_path, filename)
        imp = IJ.openImage(file_path)
        stack = imp.getImageStack()
        break


roi = PointRoi(0, 0)
with open('{0}.marker'.format(file_path.replace('.tif', '-GT.tif')), 'r') as csvfile:

    reader = csv.reader(csvfile, delimiter=',', quotechar="\"")
    header = reader.next()
    for i in range(10):
        reader.next()
    next_line = reader.next()
    x, y, z = next_line[:3]
    print(x, y, z)
    imp2 = ImagePlus('First point', stack.getProcessor(int(z)))
    roi.addPoint(imp2, float(x), float(y))

imp2.show()
imp2.setRoi(roi)
