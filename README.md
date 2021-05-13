# PopDensity_SatelliteNightLight
Compares Population Density Estimates and Satellite Night Light Mesurements

## Presentation
This repository compares estimates of population density and satellite measurements of night light. 
It is applied with data for Spain (for simplicity, exclusing Canary Islands), but it can easily be used for different datasets.

## Data
The sources for the population density datasets are:
* 1 [WorldPop](https://www.worldpop.org/project/categories?id=18), UN Adjusted, 2020, 1 km resolution.
* 2 [WorldPop](https://www.worldpop.org/project/categories?id=3), UN adjusted, unconstrained, 2020, 1 km resolution, which provides population counts and is procesed with the script [CALC DENS POP](https://github.com/Rigonz/CountryPopDensityDistrib/blob/main/CALC%20DENS%20POP%20R1%20py36.py) to obtain the required population density raster.
* 3 [GPW v4](https://sedac.ciesin.columbia.edu/data/collection/gpw-v4/sets/browse), rev. 4.11, 2020, 30 arc-sec resolution, unadjusted.
* 4 [GPW v4](https://sedac.ciesin.columbia.edu/data/collection/gpw-v4/sets/browse), rev. 4.11, 2020, 30 arc-sec resolution, adjusted to WPP-UN 2015 country totals.

The sources for the nightlight datasets are:
* 1 [VIIRS-VNL2](https://eogdata.mines.edu/nighttime_light/annual/v20/), median masked measurements for 2019.
* 2 [DMSP-OLS](https://eogdata.mines.edu/products/dmsp/#v4), for 2013, average visible band.
* 3 [DMSP-OLS](https://eogdata.mines.edu/products/dmsp/#radcal), for 2010, averaged with radiance calibration.

All raster files have been clipped to (-9.65, 43.9; 4.5, 36.0) deg (lon, lat).

The rasters are, at plain sight, correct as shown in the following snapshots from QGIS with a transparency of 80%:
![POPDENS_2](https://github.com/Rigonz/PopDensity_SatelliteNightLight/blob/main/Images/POPDENS_2.png)
![POPDENS_4](https://github.com/Rigonz/PopDensity_SatelliteNightLight/blob/main/Images/POPDENS_4.png)
![NL_1](https://github.com/Rigonz/PopDensity_SatelliteNightLight/blob/main/Images/NL_1.png)
![NL_3](https://github.com/Rigonz/PopDensity_SatelliteNightLight/blob/main/Images/NL_3.png)

## Internal correlations
The datasets have been compared within each type of data, with the following main results.

### Population Density
The datasets are highly correlated by pairs 1-2 and 3-4, as should be expected, and only moderately correlated across these groups as indicated by the Pearson coefficients (after removing the no-data, maintaining the 0s):
* DS1-2 = 0.995.
* DS1-3 = 0.693.
* DS1-4 = 0.693.
* DS2-3 = 0.681.
* DS2-4 = 0.681.
* DS3-4 = 1.000.

The histograms are controlled by the low densities:

![NL_HIST1](https://github.com/Rigonz/PopDensity_SatelliteNightLight/blob/main/Images/NL_HIST1.png)
![NL_HIST2](https://github.com/Rigonz/PopDensity_SatelliteNightLight/blob/main/Images/NL_HIST2.png)

The bivariate graphs confirm the moderate correlation:

![NL_BIVAR](https://github.com/Rigonz/PopDensity_SatelliteNightLight/blob/main/Images/NL_BIVAR.png)
![NL_HEAT](https://github.com/Rigonz/PopDensity_SatelliteNightLight/blob/main/Images/NL_HEAT.png)


### Nightlight Measurements
The correlation among the datasets is also just moderate, as indicated by the Pearson coefficients (after removing the 0s and no-data):
* DS1-2 = 0.632.
* DS1-3 = 0.507.
* DS2-3 = 0.646.

Normalizing the data yields a loose relationship:

![NL 0-100%](https://github.com/Rigonz/PopDensity_SatelliteNightLight/blob/main/Images/NL_0-100.png)

## External correlations
The rather low internal correlations among the datasets raises the question of which can actually be the strength of the relationship between population density and night-light measurements. It should be quite straightforward to assess the correlation between a dataset of population densities and the nightlight readings from another dataset, but the observed variations across the datasets of the same type seem to make this exercise a walk alongside the data bazaar, which I prefer to avoid.

## Scripts
Two scripts are provided:
* [POP CHECK](https://github.com/Rigonz/PopDensity_SatelliteNightLight/blob/main/POP%20CHECK%20R0%20py36.py), performs the calculations with the population density rasters.
* [NL CHECK](https://github.com/Rigonz/PopDensity_SatelliteNightLight/blob/main/NL%20CHECK%20R0%20py36.py), which does a similar task with the nightlight measurements.

The scripts are written in Python. They use the library [rasterio](https://rasterio.readthedocs.io/en/latest/index.html#), which I have not been able to run under python 3.8, but it works well under python 3.6.

They have been uploaded as they are on my computer: modifying the location of the files and other preferences should be quite straightforward.
