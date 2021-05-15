'''
Created on: see version log.
@author: rigonz
coding: utf-8

IMPORTANT: requires py3.6 (rasterio)

Script that:
1) reads a series of raster files,
2) runs some analytics on the data,
3) makes charts showing the results.

The input data corresponds to a country of the world (ESP); this can be easily
changed to any area.

There are two types of data:
- the first represents population densities (PD),
- the second represents night-light measures from satellites (NL).

For each type of data there are several files. Each file corresponds to a data
provider (source, satellite or measurement conditions).

Separate scripts run checks that verify that the input files refer to the same
region and other intercomparison indicators. These scripts are:
- NL CHECK R_ py36 for the night-light,
- POP CHECK R_ py36 for the population density.
Those scripts also provide additional information on the data.

This script simply finds the correlations among the sets of data.
It also provides some charts for few pairs of data.

It is based on the previous scripts, and improves some details.

Version log.
R0 (20210515):
First trials, seems to work well.

'''

# %% Imports.
import rasterio  # IMPORTANT: requires py3.6
import numpy as np
from matplotlib import pyplot as plt


# %% Functions.
def f_PearsonLE0(b1faux, b2faux):
    '''
    Function that:
    - receives two flattened arrays of the same shape,
    - applies a mask to remove the negative values in any of the arrays,
    - calculates the Pearson correlation coefficient to the masked pair,
    - returns the coefficient.
    '''
    b_mask = np.array(np.array([b1faux, b2faux]).min(axis=0) < 0)
    return(np.corrcoef(np.delete(b1faux, b_mask),
                       np.delete(b2faux, b_mask))[0, 1])


def f_PearsonLT0(b1faux, b2faux):
    '''
    Function that:
    - receives two flattened arrays of the same shape,
    - applies a mask to remove 0 and the negative values in any of the arrays,
    - calculates the LOG-LOG Pearson correlation coefficient to the masked pair,
    - returns the coefficient.
    '''
    b_mask = np.array(np.array([b1faux, b2faux]).min(axis=0) <= 0)
    return(np.corrcoef(np.log10(np.delete(b1faux, b_mask)),
                       np.log10(np.delete(b2faux, b_mask)))[0, 1])

# %% Directories.
# Filenames for NL:
RootDirIn = 'D:/0 DOWN/zz EXTSave/GIS/NIGHTLIGHT/SHP/'
FileNameINL1 = RootDirIn + 'VNL_v2_npp_2019_global_vcmslcfg_c202102150000.median_masked_ESP_clip.tif'
FileNameINL2 = RootDirIn + 'F16_20100111-20110731_rad_v4.avg_vis_ESP_clip.tif'
FileNameINL3 = RootDirIn + 'F182013.v4c_web.avg_vis_ESP_clip.tif'

# Filenames for POP:
RootDirIn = 'D:/0 DOWN/zz EXTSave/GIS/POP/EUR/SHP/'
FileNameIPD1 = RootDirIn + 'WP/ESP_clip_pd_2020_1km_UNadj.tif'
FileNameIPD2 = RootDirIn + 'WP/ESP_clip_ppp_2020_1km_Aggregated_UNadj_d.tif'
FileNameIPD3 = RootDirIn + 'GPW/ESP_clip gpw_v4_population_density_rev11_2020_30_sec.tif'
FileNameIPD4 = RootDirIn + 'GPW/ESP_clip gpw_v4_population_density_adjusted_to_2015_unwpp_country_totals_rev11_2020_30_sec.tif'


# %% Read data.
# Open NL files:
print('Opening and reading the NL files...')
dsNL1 = rasterio.open(FileNameINL1)
dsNL2 = rasterio.open(FileNameINL2)
dsNL3 = rasterio.open(FileNameINL3)

# Read NL data:
bandNL1 = dsNL1.read(1)
bandNL2 = dsNL2.read(1)
bandNL3 = dsNL3.read(1)

# Open PD files:
print('Opening and reading the PD files...')
dsPD1 = rasterio.open(FileNameIPD1)
dsPD2 = rasterio.open(FileNameIPD2)
dsPD3 = rasterio.open(FileNameIPD3)
dsPD4 = rasterio.open(FileNameIPD4)

# Read PD data:
bandPD1 = dsPD1.read(1)
bandPD2 = dsPD2.read(1)
bandPD3 = dsPD3.read(1)
bandPD4 = dsPD4.read(1)

# %% Check the NL datasets.
print('Checking the NL data...')
# Bounds:
if dsNL1.bounds != dsNL2.bounds or dsNL1.bounds != dsNL2.bounds:
    print('WARNING: boundsNL are not the same:')
    print(dsNL1.bounds)
    print(dsNL2.bounds)
    print(dsNL3.bounds)

# Width and height:
if dsNL1.width != dsNL2.width or dsNL1.width != dsNL3.width:
    print('WARNING: widths are not the same:')
    print(dsNL1.width)
    print(dsNL2.width)
    print(dsNL3.width)

if dsNL1.height != dsNL2.height or dsNL1.height != dsNL3.height:
    print('WARNING: heights are not the same:')
    print(dsNL1.height)
    print(dsNL2.height)
    print(dsNL3.height)

# Bands:
if dsNL1.indexes[0] != dsNL2.indexes[0] or dsNL1.indexes[0] != dsNL3.indexes[0]:
    print('WARNING: bands are not the same:')
    print(dsNL1.indexes[0])
    print(dsNL2.indexes[0])
    print(dsNL3.indexes[0])

# Dimensions:
if bandNL1.shape != bandNL2.shape or bandNL1.shape != bandNL3.shape:
    print('WARNING: shapes are not the same:')
    print(bandNL1.shape)
    print(bandNL2.shape)
    print(bandNL3.shape)

# CRS:
try:
    if (dsNL1.crs.data['init'] != 'epsg:4326' or
        dsNL2.crs.data['init'] != 'epsg:4326' or
        dsNL3.crs.data['init'] != 'epsg:4326'):
        print('WARNING: CRS is not EPSG:4326.')
except:
    print('WARNING: CRS is not available or is not EPSG:4326:')


# %% Check the PS datasets.
print('Checking the PS data...')
# BoundsPD:
if not(dsPD1.bounds == dsPD2.bounds and dsPD2.bounds == dsPD3.bounds and
       dsPD3.bounds == dsPD4.bounds):
    print('WARNING: boundsPD are not the same:')
    print(dsPD1.bounds)
    print(dsPD2.bounds)
    print(dsPD3.bounds)
    print(dsPD4.bounds)

# Width and height:
if not(dsPD1.width == dsPD2.width and dsPD2.width == dsPD3.width and
       dsPD3.width == dsPD4.width):
    print('WARNING: widths are not the same:')
    print(dsPD1.width)
    print(dsPD2.width)
    print(dsPD3.width)
    print(dsPD4.width)

if not(dsPD1.height == dsPD2.height and dsPD2.height == dsPD3.height and
       dsPD3.height == dsPD4.height):
    print('WARNING: heights are not the same:')
    print(dsPD1.height)
    print(dsPD2.height)
    print(dsPD3.height)
    print(dsPD4.height)

# bands:
if not(dsPD1.indexes[0] == dsPD2.indexes[0] and dsPD2.indexes[0] == dsPD3.indexes[0]
       and dsPD3.indexes[0] == dsPD4.indexes[0]):
    print('WARNING: bands are not the same:')
    print(dsPD1.indexes[0])
    print(dsPD2.indexes[0])
    print(dsPD3.indexes[0])
    print(dsPD4.indexes[0])

# Dimensions:
if not(dsPD1.shape == dsPD2.shape and dsPD2.shape == dsPD3.shape and
       dsPD3.shape == dsPD4.shape):
    print('WARNING: shapes are not the same:')
    print(dsPD1.shape)
    print(dsPD2.shape)
    print(dsPD3.shape)
    print(dsPD4.shape)

# CRS:
try:
    if (dsPD1.crs.data['init'] != 'epsg:4326' or
        dsPD2.crs.data['init'] != 'epsg:4326' or
        dsPD3.crs.data['init'] != 'epsg:4326' or
        dsPD4.crs.data['init'] != 'epsg:4326'):
        print('WARNING: CRS is not EPSG:4326.')
except:
    print('WARNING: CRS is not available or is not EPSG:4326:')

# %% Create new bands.
print('Checking the new bands...')
# Remain within the boundaries of data:
lNL1 = dsNL1.bounds.left
lNL2 = dsNL2.bounds.left
lNL3 = dsNL3.bounds.left
tNL1 = dsNL1.bounds.top
tNL2 = dsNL2.bounds.top
tNL3 = dsNL3.bounds.top
rNL1 = dsNL1.bounds.right
rNL2 = dsNL2.bounds.right
rNL3 = dsNL3.bounds.right
bNL1 = dsNL1.bounds.bottom
bNL2 = dsNL2.bounds.bottom
bNL3 = dsNL3.bounds.bottom

lPD1 = dsPD1.bounds.left
lPD2 = dsPD2.bounds.left
lPD3 = dsPD3.bounds.left
lPD4 = dsPD4.bounds.left
tPD1 = dsPD1.bounds.top
tPD2 = dsPD2.bounds.top
tPD3 = dsPD3.bounds.top
tPD4 = dsPD4.bounds.top
rPD1 = dsPD1.bounds.right
rPD2 = dsPD2.bounds.right
rPD3 = dsPD3.bounds.right
rPD4 = dsPD4.bounds.right
bPD1 = dsPD1.bounds.bottom
bPD2 = dsPD2.bounds.bottom
bPD3 = dsPD3.bounds.bottom
bPD4 = dsPD4.bounds.bottom

l = max(lNL1, lNL2, lNL3, lPD1, lPD2, lPD3, lPD4)
t = min(tNL1, tNL2, tNL3, tPD1, tPD2, tPD3, tPD4)
r = min(rNL1, rNL2, rNL3, rPD1, rPD2, rPD3, rPD4)
b = max(bNL1, bNL2, bNL3, bPD1, bPD2, bPD3, bPD4)

res = 1 / 120.  # 30 arc-sec, approx 100 m; should be min() etc.

h = int(np.ceil((t - b) / res + 1))
w = int(np.ceil((r - l) / res + 1))

r_x = (r - l) / (w - 1)
r_y = (t - b) / (h - 1)

# Results:
print('Results:')
print('Boundaries: L= {:6.3f} T= {:6.3f} R= {:6.3f} B= {:6.3f}'.format(l, t, r, b))
print('Resolution: x= {:8.6f} y= {:8.6f}'.format(r_x, r_y))
print('Shape: w= {:4d} h= {:4d}'.format(w, h))

# %% New bands.
# Create new bands:
print('Creating the new bands...')
bNL1 = np.full((h, w), 0.)
bNL2 = np.full((h, w), 0.)
bNL3 = np.full((h, w), 0.)

bPD1 = np.full((h, w), 0.)
bPD2 = np.full((h, w), 0.)
bPD3 = np.full((h, w), 0.)
bPD4 = np.full((h, w), 0.)

# Populate the new bands:
for i in range(0, h-1, 1):
    for j in range(0, w-1, 1):
        x, y = (l + j * r_x, t - i * r_y)
        bNL1[i, j] = bandNL1[dsNL1.index(x, y)]
        bNL2[i, j] = bandNL2[dsNL2.index(x, y)]
        bNL3[i, j] = bandNL3[dsNL3.index(x, y)]

        bPD1[i, j] = bandPD1[dsPD1.index(x, y)]
        bPD2[i, j] = bandPD2[dsPD2.index(x, y)]
        bPD3[i, j] = bandPD3[dsPD3.index(x, y)]
        bPD4[i, j] = bandPD4[dsPD4.index(x, y)]

    # Show the progress:
    if (i % h) % 50 == 0:
        print('Progress... {:4.1f}%'.format(i/h*100))

# Flatten:
bNL1f = bNL1.flatten()
bNL2f = bNL2.flatten()
bNL3f = bNL3.flatten()

bPD1f = bPD1.flatten()
bPD2f = bPD2.flatten()
bPD3f = bPD3.flatten()
bPD4f = bPD4.flatten()

# %% Compute correlations by pairs of datasets, removing no-data.
print('Pearson coeff. for the whole data after removing no-data:')
print('NL1-PD1 = {:4.3f}.'.format(f_PearsonLE0(bNL1f, bPD1f)))
print('NL1-PD2 = {:4.3f}.'.format(f_PearsonLE0(bNL1f, bPD2f)))
print('NL1-PD3 = {:4.3f}.'.format(f_PearsonLE0(bNL1f, bPD3f)))
print('NL1-PD4 = {:4.3f}.'.format(f_PearsonLE0(bNL1f, bPD4f)))
print('NL2-PD1 = {:4.3f}.'.format(f_PearsonLE0(bNL2f, bPD1f)))
print('NL2-PD2 = {:4.3f}.'.format(f_PearsonLE0(bNL2f, bPD2f)))
print('NL2-PD3 = {:4.3f}.'.format(f_PearsonLE0(bNL2f, bPD3f)))
print('NL2-PD4 = {:4.3f}.'.format(f_PearsonLE0(bNL2f, bPD4f)))
print('NL3-PD1 = {:4.3f}.'.format(f_PearsonLE0(bNL3f, bPD1f)))
print('NL3-PD2 = {:4.3f}.'.format(f_PearsonLE0(bNL3f, bPD2f)))
print('NL3-PD3 = {:4.3f}.'.format(f_PearsonLE0(bNL3f, bPD3f)))
print('NL3-PD4 = {:4.3f}.'.format(f_PearsonLE0(bNL3f, bPD4f)))

# %% Compute correlations by pairs of datasets, removing no-data, log-log.
print('Pearson coeff. for the whole data after removing 0s and no-data, LOG-LOG:')
print('NL1-PD1 = {:4.3f}.'.format(f_PearsonLT0(bNL1f, bPD1f)))
print('NL1-PD2 = {:4.3f}.'.format(f_PearsonLT0(bNL1f, bPD2f)))
print('NL1-PD3 = {:4.3f}.'.format(f_PearsonLT0(bNL1f, bPD3f)))
print('NL1-PD4 = {:4.3f}.'.format(f_PearsonLT0(bNL1f, bPD4f)))
print('NL2-PD1 = {:4.3f}.'.format(f_PearsonLT0(bNL2f, bPD1f)))
print('NL2-PD2 = {:4.3f}.'.format(f_PearsonLT0(bNL2f, bPD2f)))
print('NL2-PD3 = {:4.3f}.'.format(f_PearsonLT0(bNL2f, bPD3f)))
print('NL2-PD4 = {:4.3f}.'.format(f_PearsonLT0(bNL2f, bPD4f)))
print('NL3-PD1 = {:4.3f}.'.format(f_PearsonLT0(bNL3f, bPD1f)))
print('NL3-PD2 = {:4.3f}.'.format(f_PearsonLT0(bNL3f, bPD2f)))
print('NL3-PD3 = {:4.3f}.'.format(f_PearsonLT0(bNL3f, bPD3f)))
print('NL3-PD4 = {:4.3f}.'.format(f_PearsonLT0(bNL3f, bPD4f)))

# %% Draw chart - NOT Normalized, all.
# Auxiliaries:
color = ['k', 'r', 'b', 'g']

# Plot:
plt.figure(1, figsize=(4, 4), dpi=300)
plt.scatter(bNL1f, bPD1f, color=color[0], s=1.0, label='NL1-PD1', alpha=0.1)
plt.scatter(bNL3f, bPD2f, color=color[1], s=1.0, label='NL3-PD2', alpha=0.1)

# Etc:
plt.title('data>=0', loc='right')
plt.xlabel('NL, not normalized')
plt.ylabel('PD, hab/km2')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.ylim(0, 30000)
plt.show()

# %% Draw heatmap for best log-log correlation (NL1-PD1).
# Plot:
b_mask = np.array(np.array([bNL1f, bPD1f]).min(axis=0) <= 0)
plt.hist2d(np.log10(np.delete(bNL1f, b_mask)), np.log10(np.delete(bPD1f, b_mask)), bins=100, cmap='binary')

# Colorbar:
cb = plt.colorbar()
cb.set_label('Number of entries')

# Etc:
plt.title('BEST', loc='right')
plt.xlabel('NL1, normalized, log10')
plt.ylabel('PD1, normalized, log10')
plt.tight_layout()
plt.show()

# %% Draw heatmap for worst log-log correlation (NL1-PD3).
# Plot:
b_mask = np.array(np.array([bNL1f, bPD3f]).min(axis=0) <= 0)
plt.hist2d(np.log10(np.delete(bNL1f, b_mask)), np.log10(np.delete(bPD3f, b_mask)), bins=100, cmap='binary')

# Colorbar:
cb = plt.colorbar()
cb.set_label('Number of entries')

# Etc:
plt.title('WORST', loc='right')
plt.xlabel('NL1, normalized, log10')
plt.ylabel('PD3, normalized, log10')
plt.tight_layout()
plt.show()

# %% Script done.
print('\nScript completed. Thanks!')
