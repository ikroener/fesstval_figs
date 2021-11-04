## File handling 

import sys
import os
import shutil
from ftplib import FTP

def find_figs(basedir):
    fig_files = [os.path.join(basedir+'tmp/figs/', f) for f in os.listdir(basedir + '/tmp/figs/') if f.endswith('.png')]
    return fig_files

def rename_fig(infig):
    infig = os.path.basename(infig)
    infig = infig.split("-")
    outfig = infig[1] + '-' + infig[2] + '-today.png' 
    return outfig

def find_namelists(basedir):
    namelist_files = [os.path.join(basedir+'tmp/figs/', f) for f in os.listdir(basedir + '/tmp/figs/') if f.startswith('NAMELIST')]
    return namelist_files

def rename_namelists(infig):
    infig = os.path.basename(infig)
    infig = infig.split("_")
    outfig = infig[0] + '_' + infig[1] + '_' + infig[2] +'_today'
    return outfig

def move2archive(infig):

    #ftp = FTP('ftp-projects.cen.uni-hamburg.de')  
    #ftp.login('fesstval','7Tq9c4Yg')
    #ftp.cwd('work/tbfrankfurt/modeling/today')
    #outfile = rename_fig(infig)
    #outfig = outdir+"/today/"+outfile
    #shutil.copyfile(infig,outfig)
    #serverfig = os.path.basename(outfig)
    #send2FTP(ftp,outfig,serverfig)
    print(infig)
    tmpfig = os.path.basename(infig).split("-")[3]
    tmpfig = tmpfig.replace(".png","")
    try:
        os.mkdir(basedir+"/website/archive/"+tmpfig)
    except FileExistsError:
        pass
    outfig = basedir+"/website/archive/"+tmpfig+ "/" +os.path.basename(infig)
    shutil.move(infig,outfig)
    #serverfig = os.path.basename(outfig)
    #send2FTP(ftp,outfig,serverfig)

def copy2today(infig):
    outfile = rename_fig(infig)
    outfig = basedir+"/website/today/"+outfile
    shutil.copyfile(infig,outfig)          

def list2today(infig):
    outfile = rename_namelists(infig)
    outfig = basedir+"/website/today/"+outfile
    shutil.copyfile(infig,outfig)

def list2archive(infig):
    tmpfig = os.path.basename(infig).split("_")[3][0:8]
    try:
        os.mkdir(outdir+"/website/archive/"+tmpfig)
    except FileExistsError:
        pass
    outfig = basedir+"/website/archive/"+tmpfig+ "/" +os.path.basename(infig)
    shutil.move(infig,outfig)
    
def main(basedir):
    fig_files = find_figs(basedir)
    [copy_n_move(f) for f in fig_files]

def send2FTP(ftp,outfig,serverfig):
    f = open(outfig, 'rb') 
    ftp.storbinary('STOR ' + serverfig, f,1024) 

def clean(basedir):
    ## Remove all working and input files
    return True


## Body to call as script


if __name__ == "__main__":

    basedir=sys.argv[1]
    fig_files = find_figs(basedir)
    list_files = find_namelists(basedir)
    if (sys.argv[2] == "1") :
        print("copy figs to today")
        [copy2today(f) for f in fig_files]
        [list2today(f) for f in list_files]

    print("copy figs to archive")
    [move2archive(f) for f in fig_files]
    [list2archive(f) for f in list_files]
