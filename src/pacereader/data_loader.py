'''
This class provides a set of utilities to perform various operations on NetCDF image files.
It is designed to facilitate easy manipulation and processing of NetCDF datasets.
'''

import os
import subprocess as sub
from netCDF4 import Dataset
from osgeo import gdal, osr

gdal.UseExceptions()

def array_to_geotiff(array, filename, dtype=gdal.GDT_Float32):

    '''
    Save a Data Array as TIFF image
    Args:
        array (np.array): Data Array to be converted
        filename (string): path + file_name.tiff
        dtype (gdal.GDT): Data type of the array
    Returns:
        None
    '''

    driver = gdal.GetDriverByName('GTiff')
    out_raster = driver.Create(filename, array.shape[1], array.shape[0], 1, dtype)
    out_raster.SetGeoTransform((0, 1, 0, 0, 0, -1))
    out_band = out_raster.GetRasterBand(1)
    out_band.WriteArray(array)
    out_raster_srs = osr.SpatialReference()
    out_raster_srs.ImportFromEPSG(4326)
    out_raster.SetProjection(out_raster_srs.ExportToWkt())
    out_band.FlushCache()

def get_geolocation_parameters(dest, dataset_file):

    '''
    Access the Geolocation parameters (latitude and longitude) from a netCDF file. The lat_array and lon_array are saved as TIFF images.
    Args:
        dest (float): destination folder
        dataset_file (DataArray): NetCDF file opened with Xarray
    Returns:
        lon_tif (string): path to the longitute.tiff file
        lat_tif (string): path to the latitude.tiff file
        lon_data (DataArray): dataset of the longitude information
        lat_data (DataArray): dataset of the latitude information
    '''

    lat_tif = os.path.join(dest, 'latitude.tif')
    lon_tif = os.path.join(dest, 'longitude.tif')

    # The np.array must be transposed to match the GeoTIFF format
    lat_data = dataset_file['geolocation_data']['latitude'][:][::1]
    lon_data = dataset_file['geolocation_data']['longitude'][:][::1]

    array_to_geotiff(lat_data, lat_tif)
    array_to_geotiff(lon_data, lon_tif)

    return lon_tif, lat_tif, lon_data, lat_data

def netcdf_to_vrt(obs_dataset, data, dest, band_name, band_number, lon_tif, lat_tif):

    '''
    Convert the netCDF file to a VRT file.
    Args:
        data (DataArray): Dataset loaded from the NetCDF file
        nc_file (string): folder_path + netcdf file name
        dest (string): destination folder
        band_name (string): band of interest (for PACE image: blue, red, SWIR)
        band_number (string): band number of interest (integer)
        lon_tif (string): path to the longitude.tiff file
        lat_tif (string): path to the latitude.tiff file
    Returns:
        vrt_file (string): path to the .vrt file
    '''

    # Create a reference netCDF from one single band:

    rrs = obs_dataset["rhot_" + band_name].sel({band_name + "_bands": band_number})
    netcdf_file = os.path.join(dest, 'band_ref.nc')
    rrs.to_netcdf(netcdf_file)

    vrt_file = os.path.join(dest, 'output_' + str(band_number) + '.vrt')

    # Write VRT file:
    with open(vrt_file, 'w') as vrt:
        vrt.write(f'''
        <VRTDataset rasterXSize="{data.shape[1]}" rasterYSize="{data.shape[0]}">
            <GeoTransform> 0,  1,  0,  0,  0, -1 </GeoTransform>
            <VRTRasterBand dataType="Float32" band="1">
            <NoDataValue>-32767</NoDataValue>
            <ComplexSource>
                <SourceFilename relativeToVRT="0">{netcdf_file}</SourceFilename>
                <SourceBand>1</SourceBand>
                <SourceProperties RasterXSize="{data.shape[1]}" RasterYSize="{data.shape[0]}" DataType="Float32" BlockXSize="1272" BlockYSize="1"/>
                <SrcRect xOff="0" yOff="0" xSize="{data.shape[1]}" ySize="{data.shape[0]}"/>
                <DstRect xOff="0" yOff="0" xSize="{data.shape[1]}" ySize="{data.shape[0]}"/>
            </ComplexSource>
            </VRTRasterBand>
            <metadata domain="GEOLOCATION">
            <mdi key="X_DATASET">{lon_tif}</mdi>
            <mdi key="X_BAND">1</mdi>
            <mdi key="Y_DATASET">{lat_tif}</mdi>
            <mdi key="Y_BAND">1</mdi>
            <mdi key="PIXEL_OFFSET">0</mdi>
            <mdi key="LINE_OFFSET">0</mdi>
            <mdi key="PIXEL_STEP">1</mdi>
            <mdi key="LINE_STEP">1</mdi>
            </metadata>
        </VRTDataset>
            ''')

    return vrt_file

def vrt_to_geotiff(out_tif, vrt_file, lon_data, lat_data):

    '''
    Convert the vrt file to a GeoTIFF file.
    Args:
        out_tif (string): destination filename
        vrt_file (string): folder_oath + vrt file name
        lon_data (DataArray): dataset of the latitude information
        lat_data (DataArray): dataset of the longitude information
    Returns:
        None
    '''

    cmd_warp = [
        'gdalwarp',
        '-geoloc',
        '-t_srs', 'EPSG:4326',
        '-srcnodata', '-32767',
        '-dstnodata', '100000000000000000000',
        '-te', f'{lon_data.min()}', f'{lat_data.min()}', f'{lon_data.max()}', f'{lat_data.max()}',
        '-tr', f'{(lon_data.max() - lon_data.min()) / lon_data.shape[1]}',
        f'{(lat_data.max() - lat_data.min()) / lat_data.shape[0]}',
        vrt_file,
        out_tif
    ]
    sub.call(cmd_warp)

def merge_band_files(path_main, band_name):

    '''
    Merge all .tiff files into one single file with multi bands.
    Args:
        path_main (string): main folder path
        band_name (string): band of interest (for PACE image: blue, red, SWIR)
    Returns:
        None
    '''

    band_files = [os.path.join(path_main, f) for f in os.listdir(path_main) if
                    f.endswith('.tif') and 'latitude' not in f and 'longitude' not in f]

    output_tif = os.path.join(path_main, 'rhot_' + band_name + '.tif')

    # Create a VRT (Virtual Raster) from the list of band files
    vrt_options = gdal.BuildVRTOptions(separate=True)
    vrt = gdal.BuildVRT(os.path.join(path_main, 'rhot_' + band_name + '.vrt'), band_files,
                        options=vrt_options)

    # Translate the VRT to a GeoTIFF
    gdal.Translate(output_tif, vrt)

    vrt = None

    os.remove(os.path.join(path_main, 'rhot_' + band_name + '.vrt'))
    for file_path in band_files: os.remove(file_path)