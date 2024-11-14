# Spilhaus map projection in Python

> [!IMPORTANT]  
> Because [rtlemos/spilhaus](https://github.com/rtlemos/spilhaus), the repository this project is based on, is licensed under GPL3.0, this repository has to have necessarily the same license.
> If you do not want to also use this license, distribute just the ouput, not the code itself.
> For more information on how to work with the GPL3.0 license, see [this GitHub discussion](https://gist.github.com/kn9ts/cbe95340d29fc1aaeaa5dd5c059d2e60) or the [GPL FAQs](https://www.gnu.org/licenses/gpl-faq.html).

The spilhaus map projection allows to show the world ocean as one continous water surface. Here I use sea surface temperature from the 2023 World Ocean Atlas. 

<img src="./sst_spilhaus_dark.png" align="center" height="800"/>

## Data
- [WORLD OCEAN ATLAS 2023 Product Documentation](https://www.ncei.noaa.gov/data/oceans/woa/WOA23/DOCUMENTATION/WOA23_Product_Documentation.pdf)
- https://www.ncei.noaa.gov/products/world-ocean-atlas or https://www.ncei.noaa.gov/thredds-ocean/catalog/woa23/DATA/catalog.html

## Changes from [rtlemos/spilhaus](https://github.com/rtlemos/spilhaus)
- land mask added to differentiate between ocean data, no ocean data and land. In the original, land is colored the same as the coldest surface temperatures, which hides larger gaps in the World Ocean Atlas Data. This derivation includes a landmask to differentiate between data, no data and no applicable data. For a different implemention of a land mask, see the parallel fork [allochthonous/spilhaus](https://github.com/allochthonous/spilhaus).
- SST data source is updated to the 2023 version of the World Ocean Atlas
- Change to to combination of rasterized data with vectorial figure elements.
- more documentation, at least where I understood the code. The exact transformation from lat,lon to x,y still remains a mystery to me. 
