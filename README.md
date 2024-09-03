# PACE Reader
The pacereader package is designed to facilitate the use of PACE (Plankton, Aerosol, Cloud, ocean Ecosystem) hyperspectral data available at [NASA's PACE mission](https://pace.gsfc.nasa.gov/). It reads the original data in .netCDF format and converts it into a georeferenced GeoTIFF format. Working with PACE data can be challenging because the reflectance values in the NetCDF files are not directly associated with geographic coordinates. This package simplifies the process by merging the geographic layers (latitude and longitude) with the variable layers, resulting in a georeferenced raster.

## Dependencies management and package installation
To set up the environment and install the package, you can recreate the conda environment with all the necessary dependencies. This command should be run from the root of the repository:
```
conda env create -f environment.yml
```
If you prefer to use an existing conda environment, you can activate it and then install the pacereader package in development mode. This allows you to make changes to the code and test them without needing to reinstall the package. Run the following command from the root of the repository:
```
pip install -e .
```
Alternatively, you can install the package directly from GitHub using the command:
```
pip install git+https://github.com/gcermsu/pacereader
```
## Usage
To see examples of how to use the pacereader package, refer to the Jupyter notebook provided in the notebooks folder. The notebook contains detailed examples and usage scenarios.

## Additional information
For more information about our research and projects, please visit the [GCER website](https://www.gcerlab.com/)
![](./docs/gcer_logo.png)