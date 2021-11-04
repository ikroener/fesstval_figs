import sys
import xarray as xr
import numpy as np
import datetime
import os
import plotting
import itertools
import requests
import shutil
import matplotlib.pyplot as plt
import plot_skewt

## GLOBAL DEFINITIONS...
##~~~~~~~~~~~~~~~~~~~~~~~~

def main(tmpstart,tmpende,basedir,cachedir):

    basedir = sys.argv[3]

    tmpstart = sys.argv[1]
    tmpende = sys.argv[2]
    start = datetime.datetime(int(tmpstart[0:4]),int(tmpstart[4:6]),int(tmpstart[6:8]),int(tmpstart[8:10]))
    ende = datetime.datetime(int(tmpende[0:4]),int(tmpende[4:6]),int(tmpende[6:8]),int(tmpende[8:10]))

    cachedir=sys.argv[4]

    ## PREPARING DATA AND MAKE DICTS WITH GROUPS
    ## ~~~~~~~~~~~~~~~~~~~~~~~~                                                                                  
    # Read cachedir

    nc_files = [os.path.join(cachedir, f) for f in os.listdir(cachedir) if f.endswith('.nc')]
    nc_files = list(itertools.compress(nc_files,list(map(lambda x : str(tmpstart) in x,nc_files))))
    nc_names = list(map(lambda x: os.path.basename(x).split("_")[0],nc_files))

    o_files = ["aero","rrps","sfc","tprifh","tprifl","turb"]
    m_files = 'meteogram'
    s_files = ['scm','crm','lem']

    o_file_work = list(itertools.compress(nc_files,list(map(lambda x : x in o_files,nc_names))))
    m_file_work = list(itertools.compress(nc_files,list(map(lambda x : m_files in x,nc_names))))
    s_file_work = list(itertools.compress(nc_files,list(map(lambda x : x in s_files,nc_names))))


    print(o_file_work)
    print(m_file_work)
    print(s_file_work)

    o_files = sorted(o_file_work)
    o_names = list(map(lambda x: os.path.basename(x).split("_")[0],o_files))
    o_file_work = {}
    for (i,o_name) in enumerate(o_names):
        o_file_work[o_name] = o_files[i]

    #s_file_work = sorted(s_file_work)
    ## Read Data
    o = {}
    for i in o_file_work:
        o[i] = xr.open_dataset(o_file_work[i])


    oentry=list(o.keys())[1]
    obs_slice = slice(o[oentry].time[0],o[oentry].time[-1])

    m_files = sorted(m_file_work)
    m_names = list(map(lambda x: os.path.basename(x).split(".")[1],m_files))
    model_names = {'ilam':'ICON_D2','iglo':'ICON_GLOBAL'}
    m_file_work = {}
    for (i,m_name) in enumerate(m_names):
        m_file_work[m_name] = m_files[i]

    m = {}
    for i in m_file_work:
        m[i] = xr.open_dataset(m_file_work[i]).sel(time = obs_slice)

        
    s_files = sorted(s_file_work)
    s_names = list(map(lambda x: os.path.basename(x).split("_")[0],s_files))

    scm_names = {'scm':'SCM_D2','crm':'CRM_D2','lem':'LEM_D2'}
    s_file_work = {}
    for (i,s_name) in enumerate(s_names):
        s_file_work[s_name] = s_files[i]

    s = {}
    for i in s_file_work:
        s[i] = xr.open_dataset(s_file_work[i]).sel(time = obs_slice)


    legs = {'obs':'Obs','iglo':'ICON-Global','ilam':'ICON-D2','scm':'ICON-SCM','crm':'ICON-CRM','lem':'ICON-LEM'}
    legends = []
    legends.append(legs['obs'])
    for i in m:
        legends.append(legs[i])

    for i in s:
        legends.append(legs[i])

        
    ## PLOTTING
    ## ~~~~~~~~~~~~~~~~~~~~~~~~      
    if 'tprifh' in o_names:
        # interpolate to range(10,100)
        tmpo = o['tprifh'].interp(height=range(9,100))
        tmp = [tmpo.temp]
        [tmp.append(m[i].temp.interp(height=range(9,100))) for i in m]
        [tmp.append(s[i].temp.interp(height=range(9,100))) for i in s]
        Tlimits = plotting.createLimits(tmp)
        tmp = [tmpo.wspeed]
        [tmp.append(m[i].wspeed.interp(height=range(9,100))) for i in m]
        [tmp.append(s[i].wspeed.interp(height=range(9,100))) for i in s]
        Wlimits = plotting.createLimits(tmp)
        tmp = [tmpo.rel_hum]
        [tmp.append(m[i].rel_hum.interp(height=range(9,100))) for i in m]
        [tmp.append(s[i].rel_hum.interp(height=range(9,100))) for i in s]
        Rlimits = plotting.createLimits(tmp)
        Rlimits = (Rlimits[0]-Rlimits[0]%10,Rlimits[1]+10-Rlimits[1]%10)
        #
        plotting.contourf(tmpo.temp,basedir,{'lims':Tlimits,'station':'Falkenberg'})
        plotting.contourf(tmpo.wspeed,basedir,{'lims':Wlimits,'station':'Falkenberg','colors':plt.cm.plasma_r})
        plotting.contourf(tmpo.rel_hum,basedir,{'lims':Rlimits,'station':'Falkenberg','colors':plt.cm.terrain_r})

        
        for i in m:
            tmpm = m[i].interp(height=range(9,100))
            plotting.contourf(tmpm.temp,
                        basedir,{'model' : model_names[i],'lims' : Tlimits})
            plotting.contourf(tmpm.wspeed,
                        basedir,{'model' : model_names[i],'lims' : Wlimits,'colors':plt.cm.plasma_r})
            plotting.contourf(tmpm.rel_hum,
                        basedir,{'model' : model_names[i],'lims' : Rlimits,'colors':plt.cm.terrain_r})
        #
        for i in s:
            tmps = s[i].interp(height=range(9,100))
            plotting.contourf(tmps.temp,
                        basedir,{'model': scm_names[i],'station':'Falkenberg','lims':Tlimits})
            plotting.contourf(tmps.wspeed,
                        basedir,{'model': scm_names[i],'station':'Falkenberg','lims':Wlimits,'colors':plt.cm.plasma_r})
            plotting.contourf(tmps.rel_hum,
                        basedir,{'model': scm_names[i],'station':'Falkenberg','lims':Rlimits,'colors':plt.cm.terrain_r})
            

            
        ## Wind dir
        tmp = [o['tprifh'].wdir.sel(height=[40.,98.])]
        [tmp.append(m[i].wdir.interp(height=[40.,98.])) for i in m]
        [tmp.append(s[i].wdir.interp(height=[40.,98.])) for i in s]
        plotting.multilines(tmp[0],tmp[1:],basedir,{'lims' : [0,360],'legend':legends})

        
    #2m temp
    if 'tprifl' in o_names:
        tmpo=o['tprifl'].temp.sel(height=2)
        tmpm = [m[i].t2m for i in m]
        tmps = [s[i].t2m for i in s]
        tmp = [tmpo]
        [tmp.append(i) for i in tmpm]
        [tmp.append(i) for i in tmps]
        limits=plotting.createLimits(tmp)
        plotting.lines(tmp[0],tmp[1:],basedir,{'lims' : limits,'legend':legends})
        
    # TKE
    if ( 2 == 2 ):
        tmp = []
        tmpleg=[]
        if 'turb' in o_names:
            tmp.append(o['turb'].tke)
            tmpleg.append(legs['obs'])
        [tmp.append(m[i].tke.interp(height=80.)) for i in m]
        [tmp.append(s[i].tke.interp(height=80.)) for i in s]
        [tmpleg.append(legs[i]) for i in m]
        [tmpleg.append(legs[i]) for i in s]
        limits=plotting.createLimits(tmp)
        plotting.lines(tmp[0],tmp[1:],basedir,{'lims' : limits,'legend':tmpleg})


    ## Heat Fluxes

    if ( 2 == 2):
        tmp = []
        tmpleg=[]
        if ('sfc' in o_names):
            tmp.append(o['sfc'].lhfl * -1)
            tmpleg.append(legs['obs'])
        [tmp.append(m[i].lhfl) for i in m] 
        [tmpleg.append(legs[i]) for i in m]
        [tmp.append(s[i].lhfl) for i in s]
        [tmpleg.append(legs[i]) for i in s]
        limits=plotting.createLimits(tmp)
        plotting.lines(tmp[0],tmp[1:],basedir,{'lims' : limits,'legend':tmpleg})
        tmp=[]
        tmpleg=[]
        if ('sfc' in o_names):
            tmp.append(o['sfc'].shfl * -1)
            tmpleg.append(legs['obs'])    
        [tmp.append(m[i].shfl) for i in m]
        [tmpleg.append(legs[i]) for i in m]
        [tmp.append(s[i].shfl) for i in s]
        [tmpleg.append(legs[i]) for i in s]
        limits=plotting.createLimits(tmp)
        plotting.lines(tmp[0],tmp[1:],basedir,{'lims' : limits,'legend':tmpleg})

        
    if ('rrps' in o_names) and ('tprifl' in o_names) and (2 == 2):
    # Plot MSL Pressure:
        constants = {'g' : 9.81 , 'Rd' : 287 , 'hf' : 73.0, 'iglo' : 53.6,'ilam':65.60,'hfs' : 55.134,'hfs2':96.0}
        tmp = [o['rrps'].p_sfc *np.exp(constants['g']/(constants['Rd']*(o['tprifl'].temp[:,0]+273.15))*constants['hf'])]
        [ tmp.append(m[i].p_sfc *np.exp(constants['g']/(constants['Rd']*(m[i].t2m + 273.15))*constants[i])/100) for i in m]
        legs2=[]
        legs2.append(legs['obs'])
        for i in m:
            legs2.append(legs[i])
        
        if ( 'crm' in s_names ):
            tmp.append(s['crm'].p_sfc *np.exp(constants['g']/(constants['Rd']*(s['crm'].t2m + 273.15))*constants['hfs'])/100)
            legs2.append(legs['crm'])

        tmp[1].attrs
            
        limits=plotting.createLimits(tmp)
        limits = (limits[0]-limits[0]%10,limits[1])
        plotting.lines(tmp[0],tmp[1:],basedir,{'lims':limits,'legend':legs2,'station':'Falkenberg','title':'Falkenberg','variable':'MSL_pressure' })


    ## Vertical profiles temp...
    if 'aero' in o_names:
        tmpo = o['aero'].groupby('id')
        timestamps = list(tmpo.groups.keys())
        for j in ['temp','rel_hum','wspeed','wdir']:
            for i in range(len(timestamps)):
                tmpo=o['aero'].sel(id=timestamps[i]).drop(('time','height'))
                tmpo = tmpo.rename({'id':'height'})
                tmpo = tmpo.assign_coords({'height':tmpo.r_hoehe.data})

                ts = str(timestamps[i])
                tts = datetime.datetime(int(ts[0:4]),int(ts[4:6]),int(ts[6:8]),int(ts[8:10]))
                key = int(ts[8:10])
                print(tts)
                tmp = [tmpo[j]]
                [tmp.append(m[k][j].sel(time=tts,height=slice(11000,0))) for k in m]
                [tmp.append(s[k][j].sel(time=tts,height=slice(11000,0))) for k in s]
                limits=plotting.createLimits(tmp)
                plotting.profiles(tmp[0],tmp[1:],basedir,
                            {'lims':limits,'legend':legends,'key':'profile{:02d}'.format(key),'title': '{:02d} UTC'.format(key)})


        for i in range(len(timestamps)):
            tmpo=o['aero'].sel(id=timestamps[i]).drop(('time','height'))
            tmpo = tmpo.rename({'id':'height'})
            tmpo = tmpo.assign_coords({'height':tmpo.r_hoehe.data})
            ts = str(timestamps[i])
            tts = datetime.datetime(int(ts[0:4]),int(ts[4:6]),int(ts[6:8]),int(ts[8:10]))
            key = int(ts[8:10])

            plot_skewt.plot_skewt(tmpo,basedir,{"station":"falkenberg","variable":"skewt","key":"{:02d}".format(key),"model":"obs",'title': '{:02d} UTC'.format(key),'time':ts[0:8]})
            
            for i in m:
                tmpm = m[i].sel(time=tts,height=slice(11000,0))
                plot_skewt.plot_skewt(tmpm,basedir,{'station':'falkenberg','model' : model_names[i],"variable":"skewt","key":"{:02d}".format(key),'title': '{:02d} UTC'.format(key)})

            for i in s:
                tmps = s[i].sel(time=tts,height=slice(11000,0))
                plot_skewt.plot_skewt(tmps,basedir,{'station':'falkenberg','model' : scm_names[i],"variable":"skewt","key":"{:02d}".format(key),'title': '{:02d} UTC'.format(key)})


                
    if (2 == 2):
        tmp = [m['ilam'].clct]
        [tmp.append(m[i].clct) for i in m]
        [tmp.append(s[i].clct) for i in s]
        limits=plotting.createLimits(tmp)
        plotting.lines(tmp[0],tmp[1:],basedir,{'lims' : (-0.1,1.1),'legend':legends})


        if (2 == 2):
            tmpyear=start.strftime('%Y')
            tmpmonth=start.strftime('%Y%m')
            tmpday=start.strftime('%Y%m%d')
            r = requests.get("http://lglks006.dwd.de:8000/media/www/mol1/cloudradar/cloudnet/classification/{0}/{1}/{2}_lindenberg_classification.png".format(tmpyear,tmpmonth,tmpday),stream=True)
            if r.status_code == 200:
                with open(os.path.join(basedir,"tmp/figs","falkenberg-clc-obs-{0}.png".format(tmpday)), 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)     
        
        for i in m:
            plotting.contourf(m[i].clc.sel(height=slice(12000,0)),basedir,{'model' : model_names[i],'lims' : (0,1.1),'station':'Falkenberg','colors':plt.cm.Blues})

        for i in s:
            plotting.contourf(s[i].clc.sel(height=slice(12000,0)),basedir,{'model' : scm_names[i],'lims' : (0,1.1),'station':'Falkenberg','colors':plt.cm.Blues})

            
    ## FILEHANDLING
    # import filehandling
    # importlib.reload(filehandling)
    # filehandling.main(basedir)
    ## RSYNC WITH SERVER
    ## Clean cache
    ## Clean tmp figs


if __name__ == "__main__":
    main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
