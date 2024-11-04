import xarray as xr
import matplotlib.pyplot as plt
import cmocean
import numpy as np
import pandas as pd

import spilhaus

def prepare_woa_data(spilhaus_res):
    # loading remote dataset
    path = "/media/sf_VM_Folder/data/0_woa23_decav_t00_04.nc4"

    ds = xr.open_dataset(path, decode_times=False)
    # extracting temperature data array at the sea surface (SST)
    sst = ds["t_mn"].sel(depth=0, time=4.614e+03)

    # creating data frame with desired resolution
    spilhaus_df = spilhaus.make_spilhaus_xy_gridpoints(spilhaus_res=spilhaus_res)
    lon, lat = spilhaus.from_spilhaus_xy_to_lonlat(spilhaus_df['x'], spilhaus_df['y'])

    assert not np.all(np.isnan(lon))

    # extracting SST data from dataset
    spilhaus_df['z'] = sst.sel(lon=xr.DataArray(lon, dims="points"),
                               lat=xr.DataArray(lat, dims="points"),
                               method="nearest").data

    # prettifying
    pretty_spilhaus_df = spilhaus.prettify_spilhaus_df(spilhaus_df)
    pretty_spilhaus_df.to_pickle("./sst.pkl")
    print("saved data as ./sst.pkl")
    return pretty_spilhaus_df


def prepare_landmask(spilhaus_res):
    path = "/media/sf_VM_Folder/data/landsea_04.msk"
    df = pd.read_csv(path, usecols=[0, 1, 2], sep=",", skiprows=1)
    # rectify inconstistent naming between both land mask resolutions
    if "Bottom_Standard_level" in df.columns:
        df.rename(columns={"Bottom_Standard_level": "Bottom_Standard_Level"}, inplace=True)

    # Create a copy of the original dataframe
    landmask = df.copy()
    # Set values above 1 in Bottom_Standard_Level to 0 in the new dataframe
    landmask.loc[landmask['Bottom_Standard_Level'] > 1, 'Bottom_Standard_Level'] = 0
    # save memory by switching from int64 to bool
    landmask["Bottom_Standard_Level"] = landmask["Bottom_Standard_Level"].astype("bool")
    # Set 'Latitude' and 'Longitude' as indexes to a xarray data set
    landmask_ds = landmask.set_index(['Latitude', 'Longitude']).to_xarray()

    spilhaus_landmask_df = spilhaus.make_spilhaus_xy_gridpoints(spilhaus_res=spilhaus_res)
    lon, lat = spilhaus.from_spilhaus_xy_to_lonlat(spilhaus_landmask_df['x'], spilhaus_landmask_df['y'])

    # extracting landmask from dataset
    spilhaus_landmask_df['z'] = landmask_ds["Bottom_Standard_Level"].sel(Longitude=xr.DataArray(lon, dims="points"),
                                                                         Latitude=xr.DataArray(lat, dims="points"),
                                                                         method="nearest")

    pretty_landmask_df = spilhaus.prettify_spilhaus_df(spilhaus_landmask_df)  # .copy(deep=True))
    pretty_landmask_df.to_pickle("./landmask.pkl")
    return pretty_landmask_df


def main():
    RELOAD_DATA = False
    SPILHAUS_RES = 2000
    DATA_GAP_COLOR = "lightgrey"
    BACKGROUND_COLOR = "white"  # "xkcd:charcoal"
    FOREGROUND_COLOR = "k"  # "white"

    try:
        assert not RELOAD_DATA
        print("try loading sst data")
        sst_df = pd.read_pickle('./sst.pkl')
    except (FileNotFoundError, AssertionError):
        print("./sst.pkl not found")
        sst_df = prepare_woa_data(spilhaus_res=SPILHAUS_RES)
    try:
        assert not RELOAD_DATA
        print("try loading landmask")
        landmask = pd.read_pickle('./landmask.pkl')
    except (FileNotFoundError, AssertionError):
        print("generating landmask")
        landmask = prepare_landmask(spilhaus_res=SPILHAUS_RES)

    print("start plotting")
    fig, ax = plt.subplots(1, 1, figsize=(8, 8), layout="constrained")

    # keep only the data points which mark the ocean, which reduces memory size
    oceanmask = landmask[landmask['z'] == 0]
    # lay down broad base layer, which will be seen through the data gaps
    ax.scatter(
        x=oceanmask["x"],
        y=oceanmask["y"],
        c=DATA_GAP_COLOR,
        marker='o',
        s=3,
        linewidth=0,
        zorder=-5,
        rasterized=True  # only useful if output figure is a vector graphic
    )

    # plot sst data
    mpp = ax.scatter(
        x=sst_df["x"],
        y=sst_df["y"],
        c=sst_df["z"],
        marker='.',
        s=1.5,
        cmap=cmocean.cm.thermal,
        zorder=0,
        linewidth=0,
        rasterized=True  # only useful if output figure is a vector graphic
    )

    # keep only the data points which mark land, which reduces memory size
    sparse_landmask = landmask[landmask['z'] != 0]
    ax.scatter(
        x=sparse_landmask["x"],
        y=sparse_landmask["y"],
        c=BACKGROUND_COLOR,
        marker='.',
        s=1.5,
        linewidth=0,
        zorder=5,
        rasterized=True  # only useful if output figure is a vector graphic
    )

    cbar_ax = fig.add_axes([0.85, 0.7, 0.025, 0.15])
    cbar = plt.colorbar(mpp, cax=cbar_ax, ticks=np.linspace(0, 30, 7))
    cbar.set_label('SST [°C]', labelpad=-20, y=1.15, rotation=0, color=FOREGROUND_COLOR)
    cbar.ax.yaxis.set_tick_params(color=FOREGROUND_COLOR)
    cbar.outline.set_edgecolor(FOREGROUND_COLOR)
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=FOREGROUND_COLOR)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.get_xaxis().set_ticks([])
    ax.get_yaxis().set_ticks([])

    if BACKGROUND_COLOR is not None:
        ax.patch.set_facecolor(BACKGROUND_COLOR)

    # save as combination of vector an raster graphic
    plt.savefig('./sst_spilhaus_white.pdf', dpi=450)
    print('Done')
    plt.show()


if __name__ == "__main__":
    main()