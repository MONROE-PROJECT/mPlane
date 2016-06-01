#!/bin/bash
# the tstat Version 3.0 should been installed on the mPlane container
# The script sets the directories and starts the Tstat
# The Tstat configuration files are in 'tstat-conf' directory
# TODO specify  internal and external network

# HOW TO RUN 
# sudo bash start_tstat.sh


###  SETUP

cd /opt/monroe/monroe-mplane/

### Sitting the tstat-conf/subnets.txt file to distinguish between the internal and external networks

# Assume 10.0.0.0/8 and 192.168.0.0/24 are internal networks
# These net 127.0.0.0/8 and net 172.17.0.0/16 dont captured


### start tstat, it is reading the tstat.conf file on the current directory
for interface in  $(ip -o link show | awk -F': ' '{if ($2 != "lo" && $2 != "docker0" && $2 != "metadata") print $2}');
do 
    if [ -z "$(ps -afx | grep -v grep | grep "tstat -l -i $interface -Z -f tstat-conf/filter.txt -N tstat-conf/subnets.txt -R tstat-conf/rrd.conf -H tstat-conf/histo.conf -T tstat-conf/runtime.conf -r /outdir/tstat_rrd/$interface -s /tstat_log/$interface")" ]; then 
        tstat -l -i $interface -Z -f tstat-conf/filter.txt -N tstat-conf/subnets.txt -R tstat-conf/rrd.conf -H tstat-conf/histo.conf -T tstat-conf/runtime.conf -r /outdir/tstat_rrd/$interface -s /tstat_log/$interface   &
    
    fi
done