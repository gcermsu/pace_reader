"""
Package Name: PACE Read
Author: Rejane Paulino, Thainara Lima
Date: August 12, 2024
Version: 0.0.0

Description:
------------
This package provides a set of tools to convert the .nc image file from PACE to .tiff georeferenced image.

"""

import os
import numpy as np
import xarray as xr
from netCDF4 import Dataset

from . import data_loader

def read_pace(nc_file, band_name, band_number = None):

    '''
    This function read the PACE NetCDF file and convert it to a georreferenced TIFF file.
    Args:
        nc_file (string): path to the NetCDF file
        band_name (string): name of the band to be converted
        band_number (int): number of the band to be converted
    Returns:
        None
    '''

    path_main, file_name = os.path.split(nc_file)

    # Open the NetCDF files:
    dsx = Dataset(nc_file, engine='h5netcdf')
    data_var = dsx["observation_data"]['rhot_' + band_name]
    obs_dataset = xr.open_dataset(nc_file, group="observation_data")

    # Get geolocation parameters
    lon_tif, lat_tif, lon_data, lat_data = data_loader.get_geolocation_parameters(path_main, dsx)

    # Loop through PACE bands    
    if band_number == None:
        band_numbers = range(0, data_var.shape[0])
    else:
        band_numbers = [band_number]
    for i in band_numbers:

        out_tif = os.path.join(path_main, 'output_' + str(i) + '.tif') # Temporary file for each band

        # The np.array must be transposed to match the GeoTIFF format
        data = data_var[:][i][::1]
        data = np.squeeze(data)

        # Write the data as VRT file
        vrt_file = data_loader.netcdf_to_vrt(obs_dataset,data, path_main, band_name, i, lon_tif, lat_tif)

        # Convert the VRT file to GeoTIFF file
        data_loader.vrt_to_geotiff(out_tif, vrt_file, lon_data, lat_data)

        os.remove(vrt_file)

    # Merge all bands into one raster file
    data_loader.merge_band_files(path_main, band_name)

    # Cleanup
    os.remove(lat_tif)
    os.remove(lon_tif)

    print("The image was successfully converted to a georeferenced TIFF file.")