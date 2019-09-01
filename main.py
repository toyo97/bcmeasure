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

from java.awt import Color
from ij import IJ, ImageJ
from ij.gui import PointRoi
import markers as mrk
import stacks
import utils
from filters import filter_cellstack

# inputs
from mean_shift import ms_center
from utils import apply_lut, circle_roi

source_dir = '/home/zemp/bcfind_GT'
cube_roi_dim = 70  # dim of cube as region of interest (ROI) around every cell center
scaleZ = 0.4  # approx proportion with xy axis

# recenter seed using local_mean
recenter = True

# local mean params
r0 = 13
r1 = 18
r2 = 40
meanw = 0.4

# filter params
method = 'none'
sigma = 10

# 3d radial distribution
max_rad = 40
plot_rad3d = True

# maxima param
noise_tol = 0

# lut (alternatives: fire, default)
cmap = 'fire'

# display
circle = True


def process_cell(cs):
    IJ.log('Cell at {}'.format(cs.center))
    cs.set_calibration()

    # filter the image
    if method != 'none':
        IJ.log('Applying ' + method + ' 3D filtering')
        filter_cellstack(cs, method=method, sigma=sigma)

    # cell stats
    loc_max = utils.local_max(cs, cs.center)
    IJ.log('Local max in {}, value: {}'.format(loc_max, cs.get_voxel(loc_max)))

    if recenter:
        cs.center = loc_max

    loc_mean = utils.local_mean(cs, r0=r0, r1=r1, r2=r2,  weight=meanw)
    IJ.log('Local mean: ' + str(loc_mean))

    tab = utils.radial_distribution_3D(cs, max_rad=max_rad)

    radius = utils.radius_thresh(tab, loc_mean)
    IJ.log('Radius: ' + str(radius))

    # find local maxima
    peaks = utils.find_maxima(cs, radius, loc_mean)
    IJ.log('Peaks: ' + str(peaks))

    # run mean shift with those maxima
    IJ.log('Applying mean shift...')
    centroid = ms_center(cs, radius, peaks, sigma, loc_mean)
    IJ.log('New center: ' + str(centroid))

    # update the centroid
    cs.center = centroid

    # apply local_mean thresh to radial distribution
    new_loc_mean = utils.local_mean(cs, r0=radius-2, r1=radius+2, r2=r2,  weight=meanw)
    IJ.log('New local mean: ' + str(new_loc_mean))

    new_tab = utils.radial_distribution_3D(cs, max_rad=max_rad)

    new_radius = utils.radius_thresh(new_tab, new_loc_mean)
    IJ.log('New radius: ' + str(new_radius))

    # apply a different look up table for display
    if cmap != 'default':
        apply_lut(cs, cmap)

    # show the cell stack positioned in the cell center
    cs.setSlice(cs.center[2] + 1)

    if circle:
        # circle_roi(cs, radius, Color.YELLOW)
        circle_roi(cs, new_radius, Color.RED)

    # draw point for new centroid
    # point = PointRoi(cs.center[0], cs.center[1])
    # point.setSize(2)
    # point.setColor(Color.RED)
    # cs.setRoi(point)

    cs.show()
    w = cs.getWindow()
    w.setLocationAndSize(1550, 400, 300, 300)

    # TODO use Image/Scale... to make cubes

    # if plot_rad3d:
    #     plot = utils.plot_rad3d(tab)
    #     plot.show()
    #     raw_input("Enter to close plot")
    #     plot.close()


def process_img(img_path):
    IJ.log('Processing {} ...'.format(img_path))

    # open image
    imp = IJ.openImage(img_path)
    imp.show()
    w_big = imp.getWindow()
    w_big.setLocationAndSize(1050, 400, 500, 500)

    # read relative csv file rows (coordinates of centers)
    img_name, img_extension = os.path.splitext(img_path)
    marker_path = img_name + '.csv'

    if not os.path.exists(marker_path):
        root = os.path.dirname(marker_path)
        IJ.log('Creating corrected CSV files in {}...'.format(root))
        mrk.markers_to_csv(root, y_inv_height=imp.height)

    markers = mrk.read_marker(marker_path, to_int=True)

    for cs in stacks.gen_cell_stacks(imp, markers, cube_roi_dim, scaleZ):

        # identify cell in original image
        imp.setSlice(cs.seed[2] + 1)
        point = PointRoi(cs.seed[0], cs.seed[1])
        point.setSize(3)
        point.setColor(Color.RED)
        imp.setRoi(point)

        if not cs.onBorder:
            process_cell(cs)
        else:
            IJ.log('Skipped on border cell in seed ' + str(cs.seed))

        c = raw_input("Press enter to show the next cell or 'n' to go to the next image\n")

        cs.close()
        if c == 'n':
            IJ.log("Skipped remaining cells")
            break


def full_process():
    for root, directories, filenames in os.walk(source_dir):
        for filename in filenames:
            if filename.endswith('.marker'):
                tif_file = filename.replace('.marker', '')
                img_path = os.path.join(root, tif_file)

                process_img(img_path)

                raw_input('Press enter to continue...')
                IJ.run("Close All")

    IJ.log('Finish')

    """
Particular images

/home/zemp/bcfind_GT/SST_11_17.tif
/home/zemp/bcfind_GT/SST_11_14.tif
/home/zemp/bcfind_GT/SST_11_16.tif
/home/zemp/bcfind_GT/SST_11_7.tif
/home/zemp/bcfind_GT/SST_11_17.tif
/home/zemp/bcfind_GT/GT_SST/03400_15600_1500.tif
/home/zemp/bcfind_GT/GT_SST/02400_14600_1000.tif
/home/zemp/bcfind_GT/GT_SST/04400_08500_1200.tif
/home/zemp/bcfind_GT/GT_SST/14600_06450_0950.tif
    """


if __name__ == '__main__':
    # launch Fiji
    ImageJ()

    # full_process()

    process_img('/home/zemp/bcfind_GT/SST_11_14.tif')

