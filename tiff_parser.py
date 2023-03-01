# builds an OpenSCAD file that generates a 3D model of an elevation map
# natively uses GeoTIFF data for elevation source, which can be obtained here: https://apps.nationalmap.gov/downloader/

import rasterio
import numpy as np
import math
import sys
from matplotlib import pyplot

# global dict to store terrain data
# avoids having to re-open via rasterio each time
datasets = {}

# Helper Functions

# sample_geotiff
# function to sample elevation from 13 arc-second GeoTIFF
def sample_geotiff(lat, lon):
    # determine relevant database
    # example GeoTIFF is: USGS_13_n22w158_20130911.tiff
    dataset_type = 'USGS_13'
    dataset_date = '20220919'

    # dataset is referenced to "northwest corner"
    if lat >= 0: # northern hemisphere
        dataset_lat = 'n{0}'.format(math.ceil(abs(lat)))
    else: # southern hemisphere
        dataset_lat = 's{0}'.format(math.floor(abs(lat)))

    if lon >= 0: # eastern hemisphere
        dataset_lon = 'e{0}'.format(math.floor(abs(lon)))
    else: # western hemisphere
        dataset_lon = 'w{0}'.format(math.ceil(abs(lon)))
    
    dataset_key = '{0}{1}'.format(dataset_lat,dataset_lon)

    # if dataset cannot be found in Dict, load new dataset
    if datasets.get(dataset_key) is None:
        dataset_name = '{0}_{1}_{2}.tiff'.format(dataset_type,dataset_key,dataset_date)

        try: 
            dataset = rasterio.open('./Data/{0}'.format(dataset_name))
            datasets[dataset_key] = dataset

        except rasterio.errors.RasterioIOError:
            print('Could not find database for {0}\n'.format(dataset_name))
            print('Ensure that the correct database is loaded in the Data/ directory')
            sys.exit(1)

    # otherwise, use known dataset
    else:
        dataset = datasets.get('{0}{1}'.format(dataset_lat,dataset_lon))

    # sample dataset
    samples = dataset.sample([(lon,lat)])
    for elev in samples:
        elevation = elev
    
    # if no elevation data present at this lat/lon
    if elevation < -999990: 
        elevation = 0 # set to 0 for nice 3D print model

    return elevation
# sample_geotiff

# approx_scale
# approximates the scale of 1 side of the terrain map square to 1 OpenSCAD unit to get accurate relative elevation
def approx_scale(lon1, lon2, num_samples):
    # approximate scale 
    diff_lon = abs(lon1-lon2)
    length_map = diff_lon*111111 # 1 degree of longitude is about 111111 meters, outside of the northern/southern hemispheres
    scale = length_map/num_samples # determine ratio for number of meters to 1 sample unit

    return scale
# approx_scale


# define northwest, southeast corners of terrain map
# assume square print - choose a square for lat/lon corners
# for now to avoid complicated earth geometry problems - assume a flat earth
lat1 = 46.960788
lon1 = -121.916461
lat2 = 46.735284
lon2 = -121.578849

# choose number of samples in lat and lon
openscad_length = 100 # mm
num_samples = 200 
scale = approx_scale(lon1,lon2,openscad_length) # meters/sample
sample_size = openscad_length/num_samples

# get grid of latitudes, longitudes, and altitudes
lats = np.linspace(lat1,lat2,num_samples)
lons = np.linspace(lon1,lon2,num_samples)
alts = np.zeros((num_samples,num_samples))

# indexed by [lon,lat]
for lon_idx in range(num_samples):
    for lat_idx in range(num_samples):
        alts[lon_idx,lat_idx] = sample_geotiff(lats[lat_idx],lons[lon_idx])


# overwrite terrain_vector.scad file
with open('terrain_vector.scad','w') as file:
    file.write('terrain_vector = [\n')
    for lon_idx in range(0,num_samples,1):
        line = '['
        for lat_idx in range(num_samples-1,-1,-1):
            if lat_idx != 0:
                line = line + '{0:.3f},'.format(alts[lon_idx,lat_idx])
            else:
                line = line + '{0:.3f}'.format(alts[lon_idx,lat_idx])

        if lon_idx != num_samples-1:
            line = line + '],\n'
        else:
            line = line + ']\n'
        file.write(line)
    file.write('];\n')
    file.write('scale = {0:.3f};\n'.format(scale))
    file.write('num_samples = {0};\n'.format(num_samples))
    file.write('sample_size = {0};'.format(sample_size))

print('max altitude = {0}'.format(np.amax(alts)))
