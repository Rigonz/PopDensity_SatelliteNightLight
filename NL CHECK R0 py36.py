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
night light (NL).
Each file corresponds to a data provider (satellite or measurement conditions).

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
RootDirIn = 'D:/0 DOWN/zz EXTSave/GIS/NIGHTLIGHT/SHP/'

# Filenames:
FileNameI1 = RootDirIn + 'VNL_v2_npp_2019_global_vcmslcfg_c202102150000.median_masked_ESP_clip.tif'
FileNameI2 = RootDirIn + 'F16_20100111-20110731_rad_v4.avg_vis_ESP_clip.tif'
FileNameI3 = RootDirIn + 'F182013.v4c_web.avg_vis_ESP_clip.tif'

# %% Read data.
# Open files:
print('Opening and reading the files...')
ds1 = rasterio.open(FileNameI1)
ds2 = rasterio.open(FileNameI2)
ds3 = rasterio.open(FileNameI3)

# Read data:
band1 = ds1.read(1)
band2 = ds2.read(1)
band3 = ds3.read(1)

# %% Check the datasets.
print('Checking the data...')
# Bounds:
if ds1.bounds != ds2.bounds or ds1.bounds != ds2.bounds:
    print('WARNING: bounds are not the same:')
    print(ds1.bounds)
    print(ds2.bounds)
    print(ds3.bounds)

# Width and height:
if ds1.width != ds2.width or ds1.width != ds3.width:
    print('WARNING: widths are not the same:')
    print(ds1.width)
    print(ds2.width)
    print(ds3.width)

if ds1.height != ds2.height or ds1.height != ds3.height:
    print('WARNING: heights are not the same:')
    print(ds1.height)
    print(ds2.height)
    print(ds3.height)

# Bands:
if ds1.indexes[0] != ds2.indexes[0] or ds1.indexes[0] != ds3.indexes[0]:
    print('WARNING: bands are not the same:')
    print(ds1.indexes[0])
    print(ds2.indexes[0])
    print(ds3.indexes[0])

# Dimensions:
if band1.shape != band2.shape or band1.shape != band3.shape:
    print('WARNING: shapes are not the same:')
    print(band1.shape)
    print(band2.shape)
    print(band3.shape)

# CRS:
try:
    if (ds1.crs.data['init'] != 'epsg:4326' or
        ds2.crs.data['init'] != 'epsg:4326' or
        ds3.crs.data['init'] != 'epsg:4326'):
        print('WARNING: CRS is not EPSG:4326.')
except:
    print('WARNING: CRS is not available or is not EPSG:4326:')

# %% Create new bands.
print('Checking the new bands...')
# Remain within the boundaries of data:
left = max(ds1.bounds.left, ds2.bounds.left, ds3.bounds.left)
top = min(ds1.bounds.top, ds2.bounds.top, ds3.bounds.top)
height = min(ds1.height, ds2.height, ds3.height)
width = min(ds1.width, ds2.width, ds3.width)
res = 1 / 120.  # 30 arc-sec, approx 100 m; should be min() etc.
right = left + (width - 1) * res
bottom = top - (height - 1) * res

# Check (valid for east + north hemispheres only!):
if right > min(ds1.bounds.right, ds2.bounds.right, ds3.bounds.right):
    print('WARNING: right boundary exceeded.')
if bottom > max(ds1.bounds.bottom, ds2.bounds.right, ds3.bounds.right):
    print('WARNING: bottom boundary exceeded.')

# Create new bands:
print('Creating the new bands...')
b1 = np.full((height, width), 0.)
b2 = np.full((height, width), 0.)
b3 = np.full((height, width), 0.)

# Populate the new bands:
count = 0
for i in range(0, height, 1):
    for j in range(0, width, 1):
        x, y = (left + j * res, top - i * res)
        row, col = ds1.index(x, y)
        b1[i, j] = band1[row, col]
        row, col = ds2.index(x, y)
        b2[i, j] = band2[row, col]
        row, col = ds3.index(x, y)
        b3[i, j] = band3[row, col]

    # Show the progress:
    if count % height % 50 == 0:
        print('Progress... {:4.1f}%'.format(count/height*100))
    count += 1

# Flatten:
b1f = b1.flatten()
b2f = b2.flatten()
b3f = b3.flatten()

# %% Compute correlations.
# Complete set of data:
print('Pearson coeff. for the whole datasets:')
print('DS1-2 = {:4.3f}.'.format(np.corrcoef(b1f, b2f)[0, 1]))
print('DS1-3 = {:4.3f}.'.format(np.corrcoef(b1f, b3f)[0, 1]))
print('DS2-3 = {:4.3f}.'.format(np.corrcoef(b2f, b3f)[0, 1]))

# Remove no-data and 0s:
b_mask = np.array(np.array([b1f, b2f, b3f]).min(axis=0) <= 0)
b1fm = np.delete(b1f, b_mask)
b2fm = np.delete(b2f, b_mask)
b3fm = np.delete(b3f, b_mask)
print('Pearson coeff. for the whole data after removing the 0s:')
print('DS1-2 = {:4.3f}.'.format(np.corrcoef(b1fm, b2fm)[0, 1]))
print('DS1-3 = {:4.3f}.'.format(np.corrcoef(b1fm, b3fm)[0, 1]))
print('DS2-3 = {:4.3f}.'.format(np.corrcoef(b2fm, b3fm)[0, 1]))

# %% Draw histograms.
# Auxiliaries:
color = ['k', 'r', 'b', 'g']
label = ['DS1', 'DS2', 'DS3']

# Plot:
plt.hist([b1fm, b2fm, b3fm], bins=20, color=color[0:3], label=label)

# Etc:
plt.title('DS=>0', loc='right')
plt.xlabel('NL readings')
plt.ylabel('count')
plt.grid(True)
plt.legend()
plt.show()

# Zoom at the right tail:
# Plot:
plt.hist([b1fm, b2fm, b3fm], bins=20, color=color[0:3], density=True, label=label)

# Etc:
plt.title('DS>=0', loc='right')
plt.xlabel('NL readings')
plt.ylabel('rel. freq.')
plt.grid(True)
plt.legend()
plt.xlim(100, 2000)
plt.ylim(0, 0.0005)
plt.show()

# %% Draw chart - NOT Normalized, all.
# Auxiliaries:
color = ['k', 'r', 'b', 'g']

# Plot:
plt.figure(1, figsize=(4, 4), dpi=300)
plt.scatter(b1f, b2f, color=color[0], s=1.0, label='1-2', alpha=0.1)
plt.scatter(b1f, b3f, color=color[1], s=1.0, label='1-3', alpha=0.1)
plt.scatter(b2f, b3f, color=color[2], s=1.0, label='2-3', alpha=0.1)

# Titles:
plt.title('NL >=0', loc='right')
plt.xlabel('nightlight, not normalized')
plt.ylabel('nightlight, not normalized')

# Etc:
plt.grid(True)
plt.legend()
plt.tight_layout()

# Take a look:
plt.show()

# %% Draw chart - NOT Normalized, >0.
# Auxiliaries:
color = ['k', 'r', 'b', 'g']

# Plot:
plt.figure(1, figsize=(4, 4), dpi=300)
plt.scatter(b1fm, b2fm, color=color[0], s=1.0, label='1-2', alpha=0.1)
plt.scatter(b1fm, b3fm, color=color[1], s=1.0, label='1-3', alpha=0.1)
plt.scatter(b2fm, b3fm, color=color[2], s=1.0, label='2-3', alpha=0.1)

# Titles:
plt.title('NL >0', loc='right')
plt.xlabel('nightlight, not normalized')
plt.ylabel('nightlight, not normalized')

# Etc:
plt.grid(True)
plt.legend()
plt.tight_layout()

# Take a look:
plt.show()

# %% Normalized: cut-off with percentile.
p0 = 0
p1 = 100

# Band #1:
eq0 = np.percentile(b1, p0)
eq1 = np.percentile(b1, p1)
b1n = (b1 - eq0) / (eq1 - eq0)

# Band #2:
eq0 = np.percentile(b2, p0)
eq1 = np.percentile(b2, p1)
b2n = (b2 - eq0) / (eq1 - eq0)

# Band #3:
eq0 = np.percentile(b3, p0)
eq1 = np.percentile(b3, p1)
b3n = (b3 - eq0) / (eq1 - eq0)

# Flatten:
b1nf = b1n.flatten()
b2nf = b2n.flatten()
b3nf = b3n.flatten()

# %% Draw chart - Normalized percentile.
# Auxiliaries:
color = ['k', 'r', 'b', 'g']

# Plot:
plt.figure(1, figsize=(4, 4), dpi=300)
plt.scatter(b1nf, b2nf, color=color[0], s=1.0, label='1-2', alpha=0.1)
plt.scatter(b1nf, b3nf, color=color[1], s=1.0, label='1-3', alpha=0.1)
plt.scatter(b2nf, b3nf, color=color[2], s=1.0, label='2-3', alpha=0.1)

# Titles:
plt.title('NL '+str(p0)+'-'+str(p1)+'%', loc='right')
plt.xlabel('nightlight, normalized')
plt.ylabel('nightlight, normalized')

# Etc:
plt.grid(True)
plt.legend(loc='lower right')
plt.tight_layout()
plt.xlim(0, 1)
plt.ylim(0, 1)

# Take a look:
plt.show()

# %% Normalized: cut-off with absolute values.
# Band #1:
eq0 = 0.25
eq1 = 25.
b1n = (b1 - eq0) / (eq1 - eq0)

# Band #2:
eq0 = 0.25
eq1 = 100.
b2n = (b2 - eq0) / (eq1 - eq0)

# Band #3:
p0 = 0
p1 = 100
eq0 = np.percentile(b3, p0)
eq1 = np.percentile(b3, p1)
b3n = (b3 - eq0) / (eq1 - eq0)

# Flatten:
b1nf = b1n.flatten()
b2nf = b2n.flatten()
b3nf = b3n.flatten()

# %% Draw chart - Normalized, cut-off absolute value.
# Auxiliaries:
color = ['k', 'r', 'b', 'g']

# Plot:
plt.figure(1, figsize=(4, 4), dpi=300)
plt.scatter(b1nf, b2nf, color=color[0], s=1.0, label='1-2', alpha=0.1)
plt.scatter(b1nf, b3nf, color=color[1], s=1.0, label='1-3', alpha=0.1)
plt.scatter(b2nf, b3nf, color=color[2], s=1.0, label='2-3', alpha=0.1)

# Titles:
plt.title('NL ABS', loc='right')
plt.xlabel('nightlight, normalized')
plt.ylabel('nightlight, normalized')

# Etc:
plt.grid(True)
plt.legend(loc='lower right')
plt.tight_layout()
plt.xlim(0, 1)
plt.ylim(0, 1)

# Take a look:
plt.show()

# %% Script done.
print('\nScript completed. Thanks!')
