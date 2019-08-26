# Brain Cell Measure
_ImageJ script to measure radius of brain cells in 3D images_

- [Description](#description)
- [Algorithm](#algorithm)
- [Sources](#sources)

## Description
The script is written in Python and interpreted using [Jython](https://www.jython.org)
which translates it in Java code along with the ImageJ library.

### Algorithm

The algorithm to compute the radius is the following
- Every cell in every image is opened in ImageJ in a stack of fixed dimensions (e.g. a cube of 70 pix contains easily every cell in the dataset)
- The stack is eventually **filtered** using gaussian blur 3D or other filters (median, mean)
- A new, more accurate, center of the cell is set at the **local maximum** around the starting seed
- A **threshold** value is computed weighting the sum of the mean of the voxel values around the center and the mean of the voxel outside the cell (given internal radius, external radius and weight of the spot mean as parameters - it is empirically found that 15, 50, 0.6 values respectively work well)
- The **3D radial distribution** is computed in a given radius around the center (e.g. 40)
- Finally the **radius** is extracted cutting the radial distribution gaussian at the threshold value found before

## Sources
- [ImageJ API](https://imagej.nih.gov/ij/developer/api/)
- [Jython Scripting](https://imagej.net/Jython_Scripting)
- [bcfind](https://github.com/paolo-f/bcfind)
