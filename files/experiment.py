#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Ali Safari Khatouni
# Date: April 2017
# License: GNU General Public License v3
# Developed for use by the EU H2020 MONROE project

import json
import zmq
import netifaces
import pickle
import rrdtool
import sys
import gzip
import socket
from time import sleep, time, mktime
from subprocess import check_output, CalledProcessError
from multiprocessing import Process, Manager
from os import mkdir,rename,listdir,remove,system,makedirs
from os.path import isfile,join,isdir,getsize
from shutil import rmtree


Default_conf = {
        "zmqport": "tcp://172.17.0.1:5556",
        "modem_metadata_topic": "MONROE.META.DEVICE.MODEM",
        "dataversion": 3,
        "nodeid": "fake.nodeid",
        "rsync_dir" : "/monroe/results/",
        "shared_dir" : "/monroe/tstat/",
        "tstat_dir" : "/opt/monroe/monroe-mplane/tstat-conf/",
        "log_dir" : "/tmp/", 
        "verbosity": 2,  
        "modeminterfacename": "InternalInterface",
        "disabled_interfaces": ["lo",
                                "metadata",
                                "wlan0"
                                ],  # Interfaces to NOT run the experiment on
        "interfaces_without_metadata": ["eth0",
                                        "wlan0"]  # Manual metadata on these IF
        }
"""
# interval is 300 seconds for Tstat by default 
def fetch_Tstat_RRD( path, output_path,default_interval=300):
    #fetch all RRD files and dump them in compress file for each time
    #the file create in the rsync  direcctory

    open(EXPCONFIG["log_dir"],"a").write ("RRD UTC start time : {} \n".format( time()))
    while True:
        interval = default_interval
        if (not isdir (path)):
            open(EXPCONFIG["log_dir"],"a").write ("RRD directory does not exist ! creating the directory.\n")
            mkdir(path)
            continue

        Interface_list = [ d for d in listdir(path) if isdir(join(path,d)) and not d.startswith("op") ]
        for interface in Interface_list:
            last_fetched_time = int (read_latest_fetched_data( path,interface))

            # fetch RRD files till the process killed by the function -> change_conf_indirect_export
            result_list = []
            if(last_fetched_time == 0):
                startTime = int(time()) - interval
            else:
                startTime = last_fetched_time

            endTime = int(time())

            if endTime < startTime:
                open(EXPCONFIG["log_dir"],"a").write("Start time is after End time!!!!!!!!!!!!!! \n" )
                startTime = endTime - interval

            rrd_files = [ f for f in listdir(join(path,interface)) if isfile(join(path,interface,f)) and (".rrd" in f) ]
            for f in rrd_files :
                rrdMetric = rrdtool.fetch( join(path,interface,f),  "AVERAGE" ,'--resolution', str(interval), '-s', str (startTime), '-e', str(endTime))
                rrd_time = rrdMetric[0][0]
                last_fetched_time = rrdMetric[0][0] 
                interval = rrdMetric[0][2]
                for tuple in rrdMetric[2]:
                    rrd_time += interval
                    if tuple[0] is not None:
                        timestamp = float(rrd_time)
                        value = float(tuple[0])
                        metric = f
                        result_list.append((metric,timestamp,value))
                        last_fetched_time = max (last_fetched_time , rrd_time)

            if len(result_list) > 0:
                write_into_file(output_path, interface,result_list)
            write_latest_fetched_date( path,interface,last_fetched_time)
            sleep(5)
        sleep(30)


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
            open(EXPCONFIG["log_dir"],"a").write ("Error in compressing file {0} \n".format(e))

def read_latest_fetched_data(path,interface):
    if ( isdir (join(path,interface) ) and isfile(join(path,interface,"latest_fetched_data.txt")) ) :
        fp = open (join(path,interface,"latest_fetched_data.txt"), "r")
        latest_time = fp.readline()
        if (latest_time.isdigit()):
            return  latest_time
    return 0


def create_rrd_process(EXPCONFIG):
    process = Process(target=fetch_Tstat_RRD,
                      args=(join(EXPCONFIG["shared_dir"],"tstat_rrd/"), EXPCONFIG["rsync_dir"],300, ))
    process.daemon = True
    return (process)
"""
def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

def run_tstat(meta_info, EXPCONFIG):
    """
        Seperate process that runs the Tstat
        The ICCID and interface name excatrcted form meta info
        Tstat store data on a subdirecoty based on ICCID 
    """
    ifname = meta_info[EXPCONFIG["modeminterfacename"]]
    iccid  = meta_info["ICCID"] 

    # interface is up or not is a double check
    if not (ifname in netifaces.interfaces() and netifaces.AF_INET in netifaces.ifaddresses(ifname)):
        return False 

    ip = netifaces.ifaddresses(ifname)[2][0]['addr']
    # specify internal subnet for each interface 
    subnet_file = open(join(EXPCONFIG["tstat_dir"],iccid+"_subnets.txt"),"w")
    subnet_file.write(ip+"/32\n")
    subnet_file.close()
    open(EXPCONFIG["log_dir"],"a").write("Tstat consider %s ip as internal for interface %s with iccid %s \n" %(ip+"/32",ifname,iccid))

 
    if validate_ip(ip):
        cmd = ["tstat",
                "-l",
                "-i","{}".format(ifname),
                "-f","{}".format(join(EXPCONFIG["tstat_dir"],"filter.txt")), 
                "-N","{}".format(join(EXPCONFIG["tstat_dir"],iccid+"_subnets.txt")),
                "-R","{}".format(join(EXPCONFIG["tstat_dir"],"rrd.conf")),
                "-H","{}".format(join(EXPCONFIG["tstat_dir"],"histo.conf")),
                "-T","{}".format(join(EXPCONFIG["tstat_dir"],"runtime.conf")),
                "-r","{}".format(join(EXPCONFIG["shared_dir"],"tstat_rrd/",iccid)),
                "-s","{}".format(join(EXPCONFIG["shared_dir"],iccid))
                ]
    else:
        #  it is not valid IP EXPCONFIG["tstat_dir"] all connection considered internal ! 
        cmd = ["tstat",
                "-l",
                "-i","{}".format(ifname),
                "-f","{}".format(join(EXPCONFIG["tstat_dir"],"filter.txt")), 
                "-R","{}".format(join(EXPCONFIG["tstat_dir"],"rrd.conf")),
                "-H","{}".format(join(EXPCONFIG["tstat_dir"],"histo.conf")),
                "-T","{}".format(join(EXPCONFIG["tstat_dir"],"runtime.conf")),
                "-r","{}".format(join(EXPCONFIG["shared_dir"],"tstat_rrd/",iccid)),
                "-s","{}".format(join(EXPCONFIG["shared_dir"],iccid))
                ]

    output = None
    err_code = 0
    try:
        try:
            # Write the interface meta data to use tstat proxy
            # Proxy knows iccid mapping to interface name
            if not isdir(join(EXPCONFIG["rsync_dir"],iccid)):
                makedirs(join(EXPCONFIG["rsync_dir"],iccid))
            open(join(EXPCONFIG["rsync_dir"],iccid,"interface_info.json"),"w").write(str(meta_info))

            output = check_output(cmd)

        except CalledProcessError as e:
                err_code = e.returncode # AEL get the error code here
                output = e.output
    except Exception as e:
        if EXPCONFIG['verbosity'] > 0:
            print ("Execution or parsing failed for "
                   "command : {}, "
                   "output : {}, "
                   "error: {}").format(cmd, output, e)


def metadata(meta_ifinfo, EXPCONFIG):
    """
        Seperate process that attach to the ZeroMQ socket as a subscriber.
        Will listen forever to messages with topic defined in topic and update
        the meta_ifinfo dictionary (a Manager dict).
    """
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(EXPCONFIG['zmqport'])
    socket.setsockopt(zmq.SUBSCRIBE, EXPCONFIG['modem_metadata_topic'])
    while True:
        metadata={}
        data = socket.recv()
        try:
            ifinfo = json.loads(data.split(" ", 1)[1])
            if (EXPCONFIG["modeminterfacename"] in ifinfo and
                    ifinfo[EXPCONFIG["modeminterfacename"]] not in EXPCONFIG["disabled_interfaces"]):
                # In place manipulation of the reference variable
                for key, value in ifinfo.iteritems():
                    metadata[key] = value
        except Exception as e:
            open(EXPCONFIG["log_dir"],"a").write("Cannot get modem metadata in container {0} \n".format(e))
            sleep(1)
            pass
        if "ICCID" in str(metadata): 
            meta_ifinfo[metadata["ICCID"]] = metadata
        sleep(1)


# Helper functions
def check_if(ifname):
    """Check if interface is up and have got an IP address."""
    return (ifname in netifaces.interfaces() and
            netifaces.AF_INET in netifaces.ifaddresses(ifname))


def check_meta(info, EXPCONFIG):
    """Check if we have recieved required information."""
    if (EXPCONFIG["modeminterfacename"] in info and
            "Operator" in info and
            "Timestamp" in info and
            "ICCID" in info ): 
        if (info ["ICCID"] != "None" and 
            info[EXPCONFIG["modeminterfacename"]] != "None"):
            return True

    return False


def add_manual_metadata_information(info, ifname, EXPCONFIG):
    """
        Only used for local interfaces that do not have any metadata information.
        Normally eth0 and wlan0.
    """
    info[ifname]={EXPCONFIG["modeminterfacename"]: ifname, 
                "Operator":"local", 
                "ICCID":ifname, 
                "Timestamp":time(),
                "InternalIPAddress" : netifaces.ifaddresses(ifname)[2][0]['addr']}


def create_meta_process(EXPCONFIG):
    meta_info = Manager().dict()
    process = Process(target=metadata,
                      args=(meta_info, EXPCONFIG, ))
    process.daemon = True
    return (meta_info, process)


def create_tstat_process(meta_info, EXPCONFIG):
    process = Process(target=run_tstat, args=(meta_info, EXPCONFIG, ))
    process.daemon = True
    return process


def compress_and_rsync(EXPCONFIG):
    """ compress modified logs and move them to rsync directory"""
    try : 
        # copy Tstat logs into result directory
        for interface_dir in [ d for d in listdir(EXPCONFIG["shared_dir"]) if isdir(join(EXPCONFIG["shared_dir"],d)) ]:
            # remove old version data from shared folder
            if interface_dir.startswith("op") or interface_dir.startswith("usb") or interface_dir.startswith("wlan"):
                rmtree(join (EXPCONFIG["shared_dir"],interface_dir) ,ignore_errors=True)
                if isdir (join (EXPCONFIG["rsync_dir"],interface_dir)): 
                    rmtree(join (EXPCONFIG["rsync_dir"],interface_dir) ,ignore_errors=True)
                continue

            logs_dir_list=[ d for d in listdir(join(EXPCONFIG["shared_dir"],interface_dir)) if isdir(join(EXPCONFIG["shared_dir"],interface_dir,d)) and d.endswith(".out") ]
            logs_dir_list.sort(reverse=True)
            cmd=""
            for log_dir in logs_dir_list:
                # create the rsync dir for the interface 
                if not isdir (join(EXPCONFIG["rsync_dir"], interface_dir)):
                    mkdir(join(EXPCONFIG["rsync_dir"], interface_dir))
                for log in [ d for d in listdir(join(EXPCONFIG["shared_dir"],interface_dir,log_dir)) if isfile(join(EXPCONFIG["shared_dir"],interface_dir,log_dir,d)) and not d.endswith(".gz") ]:
                    cmd += "gzip -c -k {0} > {1} ;".format(join(EXPCONFIG["shared_dir"],interface_dir,log_dir,log),join(EXPCONFIG["shared_dir"],interface_dir,log_dir,log)+".gz")
                # move data to rsync folder
                if log_dir == logs_dir_list[0]:
                    cmd +="rsync -r --include='*gz' --include='*/' --exclude='*' {0} {1}  ;".format(join(EXPCONFIG["shared_dir"],interface_dir,log_dir), join(EXPCONFIG["rsync_dir"],interface_dir))   
                if len (logs_dir_list) > 3 and log_dir in logs_dir_list[3:]:
                    cmd += "rm -rf %s"%join(EXPCONFIG["shared_dir"],interface_dir,log_dir)
                system(cmd)
            sleep(10)

    except Exception as e:
        open(EXPCONFIG["log_dir"],"a").write ("Compress or rsync failed for exception : {} \n".format(e))
        return

def set_config(EXPCONFIG):
    """ setting the nodeid and create subdirectory to store logs 
     reading the node id from file mounted on /nodeid 
    """
    try: 
        EXPCONFIG["nodeid"]=open("/nodeid","r").readline().strip()
    except Exception as e:
        print "Error in reading node id from /nodeid {}".format(e)
        raise e
    # FIXME clean all empty folder from previous run 
    system ("find {}  -type d -empty -delete ; find {}  -type d -empty -delete ; rm  -rf {}/*/tstat_rrd/op*;".format(EXPCONFIG["rsync_dir"],EXPCONFIG["rsync_dir"],EXPCONFIG["shared_dir"],EXPCONFIG["shared_dir"]))   
    # Just to clean the old logs till here FIXME

    # making sub directory to store logs and RRD
    if not isdir(join(EXPCONFIG["rsync_dir"],EXPCONFIG["nodeid"])):
        makedirs(join(EXPCONFIG["rsync_dir"],EXPCONFIG["nodeid"]))

    # remove the rrds to avoid looping to the replaces SIMs
    rmtree(join(EXPCONFIG["shared_dir"],EXPCONFIG["nodeid"],"tstat_rrd"),ignore_errors=True)
    makedirs(join(EXPCONFIG["shared_dir"],EXPCONFIG["nodeid"],"tstat_rrd"))


    EXPCONFIG["rsync_dir"] =join(EXPCONFIG["rsync_dir"],EXPCONFIG["nodeid"])
    EXPCONFIG["shared_dir"]=join(EXPCONFIG["shared_dir"],EXPCONFIG["nodeid"])
    EXPCONFIG["log_dir"]   =join(EXPCONFIG["rsync_dir"],"log.txt") 

if __name__ == '__main__':
    """The main thread control the processes (tstat/metadata/rrdfetch))."""
    EXPCONFIG = Manager().dict()
    EXPCONFIG = Default_conf
    set_config(EXPCONFIG)
    # dictionary to store process id for each process 
    process_dic={}

    open(EXPCONFIG["log_dir"],"w").write ("TStat cotainer starts at : {} \n".format( time()))
    while  True:
        try:
            # Create a process for getting the metadata
            if "meta_data" not in process_dic or not process_dic["meta_data"].is_alive(): 
                meta_info_dic, meta_process = create_meta_process(EXPCONFIG)
                meta_process.start()
                process_dic["meta_data"] = meta_process

            # hack metadata for inerfaces without metadata    
            for ifname in netifaces.interfaces():
                # Skip disbaled interfaces
                if ifname in EXPCONFIG["disabled_interfaces"]:
                    if EXPCONFIG['verbosity'] > 3:
                        open(EXPCONFIG["log_dir"],"a").write( "Interface is disabled skipping, {} \n".format(ifname))
                    continue
                # Interface is not up we just skip that one
                if not check_if(ifname):
                    if EXPCONFIG['verbosity'] > 3:
                        open(EXPCONFIG["log_dir"],"a").write ("Interface is not up {} \n".format(ifname))
                    continue
                # we hack metadata for interfaces without metadata
                if (check_if(ifname) and ifname in EXPCONFIG["interfaces_without_metadata"]):
                    add_manual_metadata_information(meta_info_dic, ifname, EXPCONFIG)

            # loop to run tstat for all available interfaces 
            for iccid, meta_info  in  meta_info_dic.items():
                # we give up on that interface
                if not check_meta(meta_info, EXPCONFIG):
                    if EXPCONFIG['verbosity'] > 1:
                        open(EXPCONFIG["log_dir"],"a").write( "No Metadata continuing -> \t")
                        open(EXPCONFIG["log_dir"],"a").write( "{} \n".format(meta_info))
                    continue
                if meta_info["ICCID"] not in process_dic or not process_dic[meta_info["ICCID"]].is_alive(): 
                    if EXPCONFIG['verbosity'] > 1:
                        open(EXPCONFIG["log_dir"],"a").write ( "Starting Tstat on operator %s with iccid %s \n"%(meta_info[EXPCONFIG["modeminterfacename"]], meta_info["ICCID"]))  
                    # Create a experiment process and start it
                    exp_process = create_tstat_process(meta_info, EXPCONFIG)
                    exp_process.start()
                    process_dic[meta_info["ICCID"]] = exp_process
            """
            # Create a process for fetching the rrd
            if "rrd" not in process_dic or not process_dic["rrd"].is_alive():
                open(EXPCONFIG["log_dir"],"a").write ( "Starting rrd fetch \n") 
                rrd_process = create_rrd_process(EXPCONFIG)
                rrd_process.start()
                process_dic["rrd"] = rrd_process
            """       
            compress_and_rsync(EXPCONFIG)

            #if log is greater than 1MB rename it to be exported
            if  isfile(EXPCONFIG["log_dir"]) and getsize(EXPCONFIG["log_dir"])>1000000:
                rename(EXPCONFIG["log_dir"],join(EXPCONFIG["rsync_dir"],"log_{}.gz".format(time())))
            sleep (30)

        except Exception as e:
            open(EXPCONFIG["log_dir"],"a").write ("The Tstat container should live forever ! Error happened {0} \n".format(e))
            sleep (10)
