# PACE Reader
pacereader package is designed to read PACE hyperspectral data (https://pace.gsfc.nasa.gov/) in its original format (.netCDF) and convert it to GeoTiff reprojected format.

## Dependencies management and package installation
The following command can be used to recreate the conda enviroment with all the dependencies needed to run the code in this repository. The package is also installed in development mode. This command should be run from the root of the repository.
```
conda env create -f environment.yml
```
If you prefer to use another conda enviroment, you need to activate it and install the package in development mode. To do so, from the repository root, run the command below. It will install the package in development mode, so you can make changes to the code and test it without the need to reinstall the package.
```
pip install -e .
```
You can also install the package directly from GitHub using the following command:
```
pip install git+https://github.com/gcermsu/pacereader
```
## Additional information
[GCER](https://www.gcerlab.com/)
![](./docs/gcer_logo.png)