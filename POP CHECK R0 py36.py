'''
Created on: see version log.
@author: rigonz
coding: utf-8

IMPORTANT: requires py3.6 (rasterio)

Script that:
1) reads a series of raster files,
2) runs some checks,
3) makes charts showing the results.

The input data corresponds to a region of the world (ESP) and represents
the population density.
Each file has from a data provider, or different calculation conditions.

The checks consist in verifying that the input files refer to the same region.

The charts show the correlation among the different input data, as tuples
associated to the same geographical location.

Version log.
R0 (20210512):
First trials, seems to work well.

'''

# %% Imports.
import rasterio  # IMPORTANT: requires py3.6
import numpy as np
from matplotlib import pyplot as plt

# %% Directories.
RootDirIn = 'D:/0 DOWN/zz EXTSave/GIS/POP/EUR/SHP/'

# Filenames:
FileNameI1 = RootDirIn + 'WP/ESP_clip_pd_2020_1km_UNadj.tif'
FileNameI2 = RootDirIn + 'WP/ESP_clip_ppp_2020_1km_Aggregated_UNadj_d.tif'
FileNameI3 = RootDirIn + 'GPW/ESP_clip gpw_v4_population_density_rev11_2020_30_sec.tif'
FileNameI4 = RootDirIn + 'GPW/ESP_clip gpw_v4_population_density_adjusted_to_2015_unwpp_country_totals_rev11_2020_30_sec.tif'

# %% Read data.
# Open files:
print('Opening and reading the files...')
ds1 = rasterio.open(FileNameI1)
ds2 = rasterio.open(FileNameI2)
ds3 = rasterio.open(FileNameI3)
ds4 = rasterio.open(FileNameI4)

# Read data:
band1 = ds1.read(1)
band2 = ds2.read(1)
band3 = ds3.read(1)
band4 = ds4.read(1)

# %% Check the datasets.
print('Checking the data...')
# Bounds:
if not(ds1.bounds == ds2.bounds and ds2.bounds == ds3.bounds and
       ds3.bounds == ds4.bounds):
    print('WARNING: bounds are not the same:')
    print(ds1.bounds)
    print(ds2.bounds)
    print(ds3.bounds)
    print(ds4.bounds)

# Width and height:
if not(ds1.width == ds2.width and ds2.width == ds3.width and
       ds3.width == ds4.width):
    print('WARNING: widths are not the same:')
    print(ds1.width)
    print(ds2.width)
    print(ds3.width)
    print(ds4.width)

if not(ds1.height == ds2.height and ds2.height == ds3.height and
       ds3.height == ds4.height):
    print('WARNING: heights are not the same:')
    print(ds1.height)
    print(ds2.height)
    print(ds3.height)
    print(ds4.height)

# Bands:
if not(ds1.indexes[0] == ds2.indexes[0] and ds2.indexes[0] == ds3.indexes[0]
       and ds3.indexes[0] == ds4.indexes[0]):
    print('WARNING: bands are not the same:')
    print(ds1.indexes[0])
    print(ds2.indexes[0])
    print(ds3.indexes[0])
    print(ds4.indexes[0])

# Dimensions:
if not(ds1.shape == ds2.shape and ds2.shape == ds3.shape and
       ds3.shape == ds4.shape):
    print('WARNING: shapes are not the same:')
    print(ds1.shape)
    print(ds2.shape)
    print(ds3.shape)
    print(ds4.shape)

# CRS:
try:
    if (ds1.crs.data['init'] != 'epsg:4326' or
        ds2.crs.data['init'] != 'epsg:4326' or
        ds3.crs.data['init'] != 'epsg:4326' or
        ds4.crs.data['init'] != 'epsg:4326'):
        print('WARNING: CRS is not EPSG:4326.')
except:
    print('WARNING: CRS is not available or is not EPSG:4326:')

# %% Create new bands.
print('Checking the new bands...')
# Remain within the boundaries of data:
left = max(ds1.bounds.left, ds2.bounds.left, ds3.bounds.left, ds4.bounds.left)
top = min(ds1.bounds.top, ds2.bounds.top, ds3.bounds.top, ds4.bounds.top)
right = min(ds1.bounds.right, ds2.bounds.right, ds3.bounds.right, ds4.bounds.right)
bottom = max(ds1.bounds.bottom, ds2.bounds.bottom, ds3.bounds.bottom, ds4.bounds.bottom)
res = 1 / 120.  # 30 arc-sec, approx 100 m; should be min() etc.

height = int(np.ceil((top - bottom) / res + 1))
width = int(np.ceil((right - left) / res + 1))

res_x = (right - left) / (width - 1)
res_y = (top - bottom) / (height - 1)

# Check (valid for east + north hemispheres only!):
if right > min(ds1.bounds.right, ds2.bounds.right, ds3.bounds.right, ds4.bounds.right):
    print('WARNING: right boundary exceeded.')
if bottom > max(ds1.bounds.bottom, ds2.bounds.bottom, ds3.bounds.bottom, ds4.bounds.bottom):
    print('WARNING: bottom boundary exceeded.')

# Create new bands:
print('Creating the new bands...')
b1 = np.full((height, width), 0.)
b2 = np.full((height, width), 0.)
b3 = np.full((height, width), 0.)
b4 = np.full((height, width), 0.)

# Populate the new bands:
count = 0
for i in range(0, height-1, 1):
    for j in range(0, width-1, 1):
        x, y = (left + j * res_x, top - i * res_y)
        row, col = ds1.index(x, y)
        b1[i, j] = band1[row, col]
        row, col = ds2.index(x, y)
        b2[i, j] = band2[row, col]
        row, col = ds3.index(x, y)
        b3[i, j] = band3[row, col]
        row, col = ds4.index(x, y)
        b4[i, j] = band4[row, col]

    # Show the progress:
    if count % height % 50 == 0:
        print('Progress... {:4.1f}%'.format(count/height*100))
    count += 1

# %% Flatten and clear nodata.
print('Preparing the new bands...')
b1f = b1.flatten()
b2f = b2.flatten()
b3f = b3.flatten()
b4f = b4.flatten()

# Remove only nodata, retain 0s:
b_mask = np.array(np.array([b1f, b2f, b3f, b4f]).min(axis=0) < 0)
b1fm = np.delete(b1f, b_mask)
b2fm = np.delete(b2f, b_mask)
b3fm = np.delete(b3f, b_mask)
b4fm = np.delete(b4f, b_mask)

# %% Compute correlations.
print('Pearson coeff. after removing the no-data:')
print('DS1-2 = {:4.3f}.'.format(np.corrcoef(b1fm, b2fm)[0, 1]))
print('DS1-3 = {:4.3f}.'.format(np.corrcoef(b1fm, b3fm)[0, 1]))
print('DS1-4 = {:4.3f}.'.format(np.corrcoef(b1fm, b4fm)[0, 1]))
print('DS2-3 = {:4.3f}.'.format(np.corrcoef(b2fm, b3fm)[0, 1]))
print('DS2-4 = {:4.3f}.'.format(np.corrcoef(b2fm, b4fm)[0, 1]))
print('DS3-4 = {:4.3f}.'.format(np.corrcoef(b3fm, b4fm)[0, 1]))

# %% Draw histograms.
# Auxiliaries:
color = ['k', 'r', 'b', 'g']
label = ['DS1', 'DS2', 'DS3', 'DS4']

# Plot:
plt.hist([b1fm, b2fm, b3fm, b4fm], bins=20, color=color[0:4], label=label)

# Etc:
plt.title('DS=>0', loc='right')
plt.xlabel('pop. density, hab/km2')
plt.ylabel('count')
plt.grid(True)
plt.legend()
plt.show()

# Zoom at the right tail:
# Plot:
plt.hist([b1fm, b2fm, b3fm, b4fm], bins=20, color=color[0:4], label=label)

# Etc:
plt.title('DS>=0', loc='right')
plt.xlabel('pop. density, hab/km2')
plt.ylabel('count')
plt.grid(True)
plt.legend()
#•plt.xlim(1500, 40000)
plt.ylim(0, 7500)
plt.show()


# %% Draw chart.
# Auxiliaries:
color = ['k', 'r', 'b', 'g']

# Plot:
plt.figure(1, figsize=(4, 4), dpi=300)
# plt.scatter(b1fm, b3fm, color=color[0], s=1.0, label='1-3', alpha=0.1)
# plt.scatter(b1fm, b4fm, color=color[1], s=1.0, label='1-4', alpha=0.1)
plt.scatter(b2fm, b3fm, color=color[2], s=1.0, label='2-3', alpha=0.1)


# Titles:
plt.title('PD>=0', loc='right')
plt.xlabel('pop. density, hab/km2')
plt.ylabel('pop. density, hab/km2')

# Etc:
plt.grid(True)
plt.legend()
plt.tight_layout()

# Take a look:
plt.show()

# %% Draw heatmap.
# Remove 0s:
b_mask = np.array(np.array([b1f, b2f, b3f, b4f]).min(axis=0) <= 0)
b1fm = np.delete(b1f, b_mask)
b2fm = np.delete(b2f, b_mask)
b3fm = np.delete(b3f, b_mask)
b4fm = np.delete(b4f, b_mask)

# Plot:
plt.hist2d(np.log10(b2fm), np.log10(b3fm), bins=100, cmap='binary')

# Colorbar:
cb = plt.colorbar()
cb.set_label('Number of entries')

# Etc:
plt.title('PD>0', loc='right')
plt.xlabel('log10_DS2 pop. density, hab/km2')
plt.ylabel('log10_DS3 pop. density, hab/km2')
plt.tight_layout()
plt.show()

# %% Script done.
print('\nScript completed. Thanks!')
