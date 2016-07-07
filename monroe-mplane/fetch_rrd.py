#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Ali Safari Khatouni
# Date: June 2016
# License: GNU General Public License v3
# Developed for use by the EU H2020 MONROE project

import pickle
from os import listdir,remove
from os.path import isfile, join, isdir
from time import sleep, time, mktime
import rrdtool
import sys
import gzip

# default start time is the decision date on gio 16 giu 2016
# interval is 300 seconds for Tstat by default 

def fetch_Tstat_RRD( path, output_path, start,interval=300):
    """
    fetch all RRD files and dump them in compress file for each time
    the file create in the rsync  direcctory

    """
    print ("UTC start time :" + str(start))
    while True:
        if (not isdir (path)):
            print ("RRD directory does not exist !\n ")
            continue

        Interface_list = [ d for d in listdir(path) if isdir(join(path,d)) ]
        for interface in Interface_list:
            last_fetched_time = int (read_latest_fetched_data( path,interface))

            # fetch RRD files till the process killed by the function -> change_conf_indirect_export
            result_list = []
            if(last_fetched_time == 0):
                startTime = str (start - interval)
            else:
                startTime = str(last_fetched_time)

            endTime = str (int(time()))
            rrd_files = [ f for f in listdir(join(path,interface)) if isfile(join(path,interface,f)) and (".rrd" in f) ]
            for f in rrd_files :
                rrdMetric = rrdtool.fetch( join(path,interface,f),  "AVERAGE" ,'--resolution', str(interval), '-s', startTime, '-e', endTime)
                rrd_time = rrdMetric[0][0]

                for tuple in rrdMetric[2]:
                    if tuple[0] is not None:
                        rrd_time = rrd_time + interval
                        timestamp = float(rrd_time)
                        value = float(tuple[0])
                        metric = f
                        if (rrd_time > last_fetched_time):
                            last_fetched_time = int(rrd_time)

                        result_list.append((metric,timestamp,value))
                                
            if len(result_list) > 0:
                print ("result list size :    " + str(len (result_list)))
                write_into_file(output_path, interface,result_list)
            write_latest_fetched_date( path,interface,last_fetched_time)
        sleep(interval)


def write_latest_fetched_date( path,interface,last_fetched_time):
    if ( isdir (join(path,interface)) ) :
        fp = open (join(path,interface,"latest_fetched_data.txt"), "w")
        fp.write(str(last_fetched_time))

def write_into_file(path, interface, result_list):
    pickle_file=str(int(time()))+".pickle"
    if ( isdir (join(path,interface)) ) :
        with open(join(path,interface,pickle_file), 'wb') as fp:
            pickle.dump(result_list, fp)
        try:
            with open(join(path,interface,pickle_file), 'rb') as f_in:
                with gzip.open('{0}'.format(join(path,interface, pickle_file+".gz")), 'wb') as f_out:
                    f_out.writelines(f_in)
            remove(join(path,interface,pickle_file))
        except Exception as e:
            print ("Error in compressing file {0}".format(e))

def read_latest_fetched_data(path,interface):
    if ( isdir (join(path,interface) ) and isfile(join(path,interface,"latest_fetched_data.txt")) ) :
        fp = open (join(path,interface,"latest_fetched_data.txt"), "r")
        latest_time = fp.readline()
        if (latest_time.isdigit()):
            return  latest_time
    return 0

if __name__ == '__main__':
    fetch_Tstat_RRD( str(sys.argv[1]), str(sys.argv[2]), 1466513658 , 300)