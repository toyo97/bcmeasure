"""
Author: Vittorio Zampinetti

***Main script***
    Still in testing phase

TODOs:
-Remember to check these functions
    IJ.message()
    imp.getCalibration()/setCalibration()

"""

from __future__ import with_statement, print_function
import os
from ij import IJ, ImagePlus, ImageJ

import markers as mrk
from stacks import get_cells_vstacks, gen_cell_stacks
from filters import gaussianIJ

# inputs
source_dir = '/home/zemp/bcfind_GT'
n_preview = 3
cube_roi_dim = 70  # dim of cube as region of interest (ROI) around every cell center
voxel_depth = 0.4  # approx proportion with xy axis

# gauss filter params
# TODO try using voxel_depth parameter to set zsigma based on xysigma
xysigma = 2
zsigma = 1

# start ImageJ program
ImageJ()


def process_marked_imgs(root, filename):
    tif_file = filename.replace('.marker', '')
    img_path = os.path.join(root, tif_file)
    IJ.log('Processing {} ...'.format(img_path))

    # open image
    imp = IJ.openImage(img_path)
    imp.show()
    stack = imp.getImageStack()

    # read relative csv file rows (coordinates of centers)
    img_name, img_extension = os.path.splitext(img_path)
    marker_path = img_name + '.csv'

    if not os.path.exists(marker_path):
        IJ.log('Creating corrected CSV files in {}...'.format(root))
        mrk.markers_to_csv(root, y_inv_height=imp.height)

    markers = mrk.read_marker(marker_path, to_int=True)

    # cells_vstacks = get_cells_vstacks(stack, markers, cube_roi_dim, voxel_depth)
    #
    # # show the virtual stacks of the first image
    # IJ.log('Showing first {} cells'.format(n_preview))
    # for cs in cells_vstacks[:n_preview]:
    #     ImagePlus('Cell at {}'.format(cs.get_center()), cs).show()
    #     gauss_stack = gaussianIJ(cs, xysigma, zsigma)

    IJ.log('Showing first {} cells'.format(n_preview))
    for cs in gen_cell_stacks(imp, markers, cube_roi_dim, voxel_depth):
        cs.show()
        gauss_stack = gaussianIJ(cs.getImageStack(), xysigma, zsigma)


for root, directories, filenames in os.walk(source_dir):
    for filename in filenames:
        if filename.endswith('.marker'):
            process_marked_imgs(root, filename)
            raw_input('Press enter to continue...')
            IJ.run("Close All")
