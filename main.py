from __future__ import with_statement, print_function
import os
from ij import IJ, ImagePlus, ImageJ

import markers as mrk

from stacks import CellStack

# inputs
source_dir = '/home/zemp/IdeaProjects/bcmeasure/input/'
n_preview = 5
cube_roi_dim = 40  # dim of cube as region of interest (ROI) around every cell center

# start ImageJ program
ImageJ()

IJ.log('Start')
for filename in os.listdir(source_dir):
    if filename.endswith('.tif'):

        # open image
        file_path = os.path.join(source_dir, filename)
        imp = IJ.openImage(file_path)
        imp.show()
        stack = imp.getImageStack()

        # read relative csv file rows (coordinates of centers)
        marker_path = file_path.replace('.tif', '.csv')
        markers = mrk.read_marker(marker_path, to_int=True)

        cells_vstacks = []
        # for each marker append the virtual stack crop of the cell to cells_vstacks
        for xc, yc, zc in markers:
            cells_vstacks.append(CellStack(stack, xc, yc, zc, cube_roi_dim))

        # show the virtual stacks of the first image
        IJ.log('Showing first {} cells'.format(n_preview))
        for cs in cells_vstacks[:n_preview]:
            ImagePlus('Cell at {}'.format(cs.get_center()), cs).show()
        break

