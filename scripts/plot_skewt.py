import sys
import matplotlib.pyplot as plt
import metpy
from metpy.calc import dewpoint_from_relative_humidity
from metpy.units import units
from metpy.plots import SkewT

import xarray as xr
import numpy as np


def plot_skewt(tmp,basedir,OUT):

    outdir=basedir+"/tmp/figs/"

    if 'time' not in OUT:
        OUT['time'] = str(tmp.time.data)[:10]
        OUT['time'] = OUT['time'].replace('-','')

    
    tmp['temp'].attrs['units'] = 'temperature'
    ps = tmp.p.data * units.Pa
    temp = tmp.temp.data * units.degC
    rh = tmp.rel_hum.data * units.percent
    td = dewpoint_from_relative_humidity(temp,rh)
    ws = tmp.wspeed.data * units('m/s')
    wd = tmp.wdir.data * units('degrees')
    u, v = metpy.calc.wind_components(ws, wd)

    my_interval = np.arange(100, 1000, 50) * units('mbar')
    ix = metpy.calc.resample_nn_1d(ps, my_interval)

    S = SkewT()
    S.plot(ps,temp,'r')
    S.plot(ps,td,'g')
    S.plot_barbs(ps[ix], u[ix], v[ix])

    S.plot_dry_adiabats()
    S.plot_moist_adiabats()
    S.plot_mixing_lines()
    S.ax.set_ylim(1040, 200)

    fig = plt.gcf()

    figtitle = OUT['station'].capitalize() + ", " + OUT['variable'].capitalize() + ", " + OUT['time'] + '\n' + OUT['title']
    fig.suptitle(figtitle)   
    figname = OUT['station'].lower() + "-" + OUT['variable'].lower() + "_" + OUT['key'] + "-" + OUT['model'] + "-" + OUT['time'] + ".png"
    fig.savefig(outdir + figname)


    plt.close('all')
