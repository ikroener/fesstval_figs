""""
@title plotting.py
@author I.Kroener

@description plot routines for FESSTVaL website
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def contourfdif(o,m,basedir,OUT):
    ## Input: Two xarrays (1. observational product, 2. modelled product),basedir,dictonary output
    ## Output: Three plots

    outdir = basedir +"/tmp/figs/"

    ## Prepare input
    o_slice = slice(o.time[0],o.time[-1])
    m = m.sel(time = o_slice)

    maxv = int(np.nanmax([np.nanmax(o.data),np.nanmax(m.data)]))+2
    minv = int(np.nanmin([np.nanmin(o.data),np.nanmin(m.data)]))


    ## TITLE
    OUT['station'] = m.attrs['title'].capitalize() if 'station' not in OUT else OUT['station']
    OUT['variable'] = m.name.capitalize()  if 'variable' not in OUT else OUT['variable']
    if 'time' not in OUT:
        OUT['time'] = str(m.time[0].data)[:10]
        OUT['time'] = OUT['time'].replace('-','')
    OUT['model'] = 'Model' if 'model' not in OUT else OUT['model']
    if 'lims' not in OUT:
        maxv = int(np.nanmax([np.nanmax(o.data),np.nanmax(m.data)]))+2
        minv = int(np.nanmin([np.nanmin(o.data),np.nanmin(m.data)]))
        OUT['lims'] = (minv,maxv)
    OUT['driver'] = 'ICON_D2' if 'driver' not in OUT else OUT['driver']

    print("{0}".format(OUT))
        
    ## Diffplot
    difference = m - o

    maxv = np.ceil(np.nanmax([np.abs(np.nanmax(difference.data)),np.abs(np.nanmin(difference.data))]))

    fig, ax = plt.subplots()
    col_lev=np.arange(maxv*-1,maxv+0.05,0.1)
    cs = ax.contourf(difference.time,difference.height,
            difference.transpose(),
            col_lev,cmap=plt.cm.seismic)
    ax.set_xlabel('Time [UTC]')
    ax.set_ylabel('Height [m]')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_yscale('symlog',linthreshy=1000)
    ax.set_yticks([0,200,400,600,800,1000,2000,5000,7500,10000])
    ax.set_yticklabels([0,200,400,600,800,1000,2000,5000,7500,10000])
    ax.format_xdata = mdates.DateFormatter('%H:%M')
    fig.colorbar(cs, ax=ax,label="["+o.attrs['units']+"]")
    figtitle = OUT['station'] + ", " + OUT['variable'] + ", " + OUT['time'] + "\n {0} - {1}".format(OUT['model'],OUT['driver'])
    plt.title(figtitle)
    figname = OUT['station'].lower() + "-" + OUT['variable'].lower() + "-" + "diff_"+OUT['model'] + "-" + OUT['time'] + ".png"
    fig.savefig(outdir + figname)

    plt.close('all')


def contourf(m,basedir,OUT):

    ## TITLE                                                                                                                                                                                          
    OUT['station'] = m.attrs['title'].capitalize() if 'station' not in OUT else OUT['station']
    OUT['variable'] = m.name.capitalize()  if 'variable' not in OUT else OUT['variable']
    if 'time' not in OUT:
        OUT['time'] = str(m.time[0].data)[:10]
        OUT['time'] = OUT['time'].replace('-','')
    OUT['model'] = 'obs' if 'model' not in OUT else OUT['model']
    if 'lims' not in OUT:
        maxv = int(np.nanmax([np.nanmax(m.data)]))+2
        minv = int(np.nanmin([np.nanmin(m.data)]))
        OUT['lims'] = (minv,maxv)
    OUT['colors'] = plt.cm.jet if 'colors' not in OUT else OUT['colors']
        
    print("{0}".format(OUT)) 
    outdir = basedir +"/tmp/figs/"

    colsteps = 0.1 if (OUT['lims'][1] == 1.1) else 1
    fig, ax = plt.subplots()
    col_lev=np.arange(OUT['lims'][0],OUT['lims'][1],colsteps)
    cs = ax.contourf(m.time,m.height,m.transpose(),col_lev,cmap=OUT['colors'])
    ax.set_xlabel('Time [UTC]')
    ax.set_ylabel('Height [m]')
    if (m.height.data[-1] >= 1000.):
        ax.set_yscale('symlog',linthreshy=1000)
        ax.set_yticks([0,200,400,600,800,1000,2000,5000,7500,10000])
        ax.set_yticklabels([0,200,400,600,800,1000,2000,5000,7500,10000])

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.format_xdata = mdates.DateFormatter('%H:%M')
    fig.colorbar(cs, ax=ax,label="["+m.attrs['units']+"]")
    figtitle = OUT['station'] + ", " + OUT['variable'] + ", " + OUT['time'] + '\n'+OUT['model']
    plt.title(figtitle)
    figname = OUT['station'].lower() + "-" + OUT['variable'].lower() + "-" + OUT['model'] + "-" + OUT['time'] + ".png"
    fig.savefig(outdir + figname)

    plt.close('all')


def lines(o,M,basedir,OUT):
    outdir = basedir+"/tmp/figs/"
    m = M[0]

    ## TITLE
    OUT['station'] = m.attrs['title'].capitalize() if 'station' not in OUT else OUT['station']
    OUT['variable'] = m.name.capitalize()  if 'variable' not in OUT else OUT['variable']
    if 'time' not in OUT:
        OUT['time'] = str(m.time[0].data)[:10]
        OUT['time'] = OUT['time'].replace('-','')
    OUT['model'] = 'Model' if 'model' not in OUT else OUT['model']
    if 'lims' not in OUT:
        minv,maxv = createLimits([o,M])
        OUT['lims'] = (minv,maxv)
    OUT['legend'] = range(10) if 'lims' not in OUT else OUT['legend']
    OUT['colors'] = get_colors(range(10),plt.cm.tab10)
    print("{0}".format(OUT))
    fig, ax = plt.subplots()

    ax.plot(o.time,o.data,color=OUT['colors'][0],label=OUT["legend"][0])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.format_xdata = mdates.DateFormatter('%H:%M')
    for (j,n) in enumerate(M):
        ax.plot(n.time,n.data,color=OUT["colors"][j+1],label=OUT["legend"][j+1])

    if ( OUT['variable'] == 'Tke'):
        ax.set_yscale('symlog',linthreshy=0.01)
        ax.set_yticks([0.01,0.1,1,10])
        ax.set_yticklabels([0.01,0.1,1,10])
    else:
        ax.set_ylim([OUT['lims'][0], OUT['lims'][1]])

    ax.set_xlabel('Time [UTC]')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.format_xdata = mdates.DateFormatter('%H:%M')

    #plt.legend(loc='upper center', bbox_to_anchor=(1, 1.15),
    #      ncol=1, fancybox=True, shadow=True)
    plt.legend()
    figtitle = OUT['station'] + ", " + OUT['variable'] + ", " + OUT['time']
    fig.suptitle(figtitle)   
    figname = OUT['station'].lower() + "-" + OUT['variable'].lower() + "-" + "combined" + "-" + OUT['time'] + ".png"
    fig.savefig(outdir + figname)

    plt.close('all')

def multilines(o,M,basedir,OUT):

    outdir = basedir+"/tmp/figs/"
    m = M[0]

    ## TITLE
    OUT['station'] = m.attrs['title'].capitalize() if 'station' not in OUT else None
    OUT['variable'] = m.name.capitalize()  if 'variable' not in OUT else None
    if 'time' not in OUT:
        OUT['time'] = str(m.time[0].data)[:10]
        OUT['time'] = OUT['time'].replace('-','')
    OUT['model'] = 'Model' if 'model' not in OUT else OUT['model']
    if 'lims' not in OUT:
        minv,maxv = createLimits([o,M])
        OUT['lims'] = (minv,maxv)
    OUT['legend'] = range(10) if 'lims' not in OUT else OUT['legend']
    OUT['colors'] = get_colors(range(10),plt.cm.tab10)

    print("{0}".format(OUT))
    nplots = len(o.height)

    fig, ax = plt.subplots(1,nplots,figsize=(nplots*8,6))

    for i in range(nplots):
        oo = o.isel(height=i)
        MM = [x.isel(height=i) for x in M]

        ax[i].plot(oo.time,oo.data,color=OUT['colors'][0],label=OUT["legend"][0])
        ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax[i].format_xdata = mdates.DateFormatter('%H:%M')
        ax[i].set_ylim([OUT['lims'][0], OUT['lims'][1]])
        for (j,n) in enumerate(MM):
            ax[i].plot(n.time,n.data,color=OUT["colors"][j+1],label=OUT["legend"][j+1])

        ax[i].set_xlabel('Time [UTC]')
        ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax[i].format_xdata = mdates.DateFormatter('%H:%M')
        figtitle = 'height: ' + str(oo.height.data) + 'm'
        ax[i].title.set_text(figtitle)

    #    plt.legend(loc='upper center', bbox_to_anchor=(1, 1.15),
    #          ncol=1, fancybox=True, shadow=True)
    plt.legend()
    figtitle = OUT['station'] + ", " + OUT['variable'] + ", " + OUT['time']
    fig.suptitle(figtitle)   
    figname = OUT['station'].lower() + "-" + OUT['variable'].lower() + "-" + "combined" + "-" + OUT['time'] + ".png"
    fig.savefig(outdir + figname)

    plt.close('all')
    
def profiles(o,M,basedir,OUT):

    outdir = basedir+"/tmp/figs/"
    m = M[0]

    ## TITLE
    OUT['station'] = m.attrs['title'].capitalize() if 'station' not in OUT else None
    OUT['variable'] = m.name.capitalize()  if 'variable' not in OUT else None
    if 'time' not in OUT:
        OUT['time'] = str(m.time.data)[:10]
        OUT['time'] = OUT['time'].replace('-','')
    OUT['model'] = 'Model' if 'model' not in OUT else OUT['model']
    if 'lims' not in OUT:
        minv,maxv = createLimits([o,M])
        OUT['lims'] = (minv,maxv)
    OUT['legend'] = range(10) if 'lims' not in OUT else OUT['legend']
    OUT['colors'] = get_colors(range(10),plt.cm.tab10)
    OUT['key'] = "profile" if 'key' not in OUT else OUT['key']
    OUT['title'] = "" if "title" not in OUT else OUT['title']
    print("{0}".format(OUT))
    fig, ax = plt.subplots()

    ax.plot(o.data,o.height,color=OUT['colors'][0],label=OUT["legend"][0])
    ax.set_xlim([OUT['lims'][0], OUT['lims'][1]])
    for (j,n) in enumerate(M):
        ax.plot(n.data,n.height,color=OUT["colors"][j+1],label=OUT["legend"][j+1])
    ax.set_ylabel('Height [m]')
    ax.set_yscale('symlog',linthreshy=1000)
    ax.set_yticks([0,200,400,600,800,1000,2000,5000,7500,10000])
    ax.set_yticklabels([0,200,400,600,800,1000,2000,5000,7500,10000])
    if (OUT['variable'] == "Temperature"):
        ax.set_xscale('symlog',linthreshx=20) if OUT['variable'] == "Temperature" else None
        ax.set_xticks(range(-100,100,10))
        ax.set_xticklabels(range(-100,100,10))
        
    ax.set_xlim([OUT['lims'][0], OUT['lims'][1]])
    ax.set_xlabel('['+o.units+']')
    plt.grid()
    plt.legend()
    figtitle = OUT['station'] + ", " + OUT['variable'] + ", " + OUT['time'] + '\n' + OUT['title']
    fig.suptitle(figtitle)   
    figname = OUT['station'].lower() + "-" + OUT['variable'].lower() + "-" + OUT['key'] + "-" + OUT['time'] + ".png"
    fig.savefig(outdir + figname)

    plt.close('all')
    
def createLimits(X):

    maxv = -100000000
    minv = 100000000
    for x in X:
        maxv = np.ceil(np.nanmax([maxv,np.nanmax(x.data)]))
        minv = np.floor(np.nanmin([minv,np.nanmin(x.data)]))
    maxv=maxv+1

    return (minv,maxv)


def get_colors(inp, colormap, vmin=None, vmax=None):
    norm = plt.Normalize(vmin, vmax)
    return colormap(norm(inp))
