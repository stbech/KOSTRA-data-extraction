# KOSTRA-data-extraction

Uses data from <https://opendata.dwd.de/climate_environment/CDC/grids_germany/return_periods/precipitation/KOSTRA/> published by the German meteorological service (DWD). KOSTRA is a data set, that provides reference values for heavy precipitation, extrapolated from records lasting 60 years.

This repository uses the current data set KOSTRA-DWD-2010R from 2017.

The code uses a location as input to determinate coordinates by using <plus.codes>-website. Then it searches for the right grid field, in which the coordinates are located in, and extracts and saves the precipitation heights using the tables in the DWD_heights-folder.
