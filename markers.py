from __future__ import print_function
import csv
import os
from ij import IJ


def invert_y(y, height=150):
    return str(height - int(y))


def read_marker(marker_path, y_inv_height=None):
    # type: (str, int) -> list
    """
Read a marker file (any extension) and return the feature of interests (x, y, z) in a list of rows

    :param marker_path: Absolute path to the marker file

    :param y_inv_height: Height of the image to invert upside-down the y coord (only if y inversion needed)

    :return: Rows containing the coordinates (list of lists)
    """
    rows = []
    with open(marker_path, 'r') as marker:
        reader = csv.reader(marker)
        # skip header
        reader.next()
        for row in reader:

            # y coordinate inversion
            if y_inv_height is not None:
                row[1] = invert_y(row[1], y_inv_height)

            # takes only the x,y,z coordinates
            rows.append(row[:3])

        IJ.log('Read {} rows from {}'.format(len(rows), marker_path))
    return rows


def markers_to_csv(source_dir, target_dir=None, y_inv_height=None):
    # type: (str, str, int) -> None
    """
Convert *.marker files in *.csv extracting only the features of interest (i.e. x,y,z)

    :param source_dir: Source directory for the marker files

    :param target_dir: Target directory for the csv files (same as source if None)

    :param y_inv_height: Height of the image to invert upside-down the y coord (only if y inversion needed)
    """
    if target_dir is None:
        target_dir = source_dir

    # look for *.marker files
    for filename in os.listdir(source_dir):
        if filename.endswith('.marker'):

            marker_path = os.path.join(source_dir, filename)
            header = ['x', 'y', 'z']
            rows = read_marker(marker_path, y_inv_height=y_inv_height)

            csv_path = marker_path.replace('.marker', '.csv')

            with open(csv_path, 'w') as csv_file:

                IJ.log('Writing rows on {}...'.format(csv_path))

                writer = csv.writer(csv_file)
                writer.writerow(header)
                writer.writerows(rows)


if __name__=='__main__':
    source_dir = '/home/zemp/IdeaProjects/bcmeasure/input/'
    markers_to_csv(source_dir, y_inv_height=150)
