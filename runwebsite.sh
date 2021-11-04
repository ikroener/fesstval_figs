#!/bin/bash

## Driver Script
## I.Kroener 2021-05-21

#! /bin/bash

startdate=$(date --date="-1day" +"%Y%m%d00")
enddate=$(date  +"%Y%m%d00")
ltoday=1
lplot=1
lgit=1

# process arguments "$1", "$2", ... (i.e. "$@")
while getopts b:c:s:e:t:p:g: OPT; do
    case $OPT in
    b) basedir=${OPTARG} ;; 
    c) cachedir=${OPTARG} ;;
    s) startdate=${OPTARG} ;;
    e) enddate=${OPTARG} ;;
    t) ltoday=${OPTARG} ;;
    p) lplot=${OPTARG} ;;
    g) lgit=${OPTARG} ;;
    # \?) ;; # Handle error: unknown option or missing required argument.
    esac
done

echo "--- Run website ----------------"
echo "start date : "$startdate
echo "end date   : "$enddate
echo "base dir   : "$basedir
echo "cache dir  : "$cachedir
echo "--------------------------------"

## Run main script....
if [ -z ${cachedir} ];then
    echo python3.6 $basedir/runprocessing.py $basedir $startdate $enddate
    python3.6 $basedir/runprocessing.py $basedir $startdate $enddate
    cachedir=$basedir/data/$startdate
    echo "cache dir  : "$cachedir
fi

if [ $lplot ]; then
    echo python3.6 $basedir/website/scripts/main.py $startdate $enddate $basedir $cachedir
    python3.6 $basedir/website/scripts/main.py $startdate $enddate $basedir $cachedir
    echo python3.6 $basedir/website/scripts/filehandling.py $basedir $ltoday
    python3.6 $basedir/website/scripts/filehandling.py $basedir $ltoday

    if [ $lgit ]; then
	cd $basedir/website
	if [ $ltoday ]; then
	    git add today
	fi
	git add archive/${startdate:0:8}
	git commit -m "daily update"
	git push
    fi
fi
