#!/bin/bash
# the tstat Version 3.0 should been installed on the mPlane container
# The script sets the directories and starts the Tstat
# The Tstat configuration files are in 'tstat-conf' directory
# TODO specify  internal and external network

# HOW TO RUN 
# sudo bash start_tstat.sh


###  SETUP
LOG_DIR="/var/log/syslog"
date &>> $LOG_DIR

### Sitting the tstat-conf/subnets.txt file to distinguish between the internal and external networks
ifconfig | awk  'sub(/inet addr:/,""){ if($1!~'/^127/') print $1"/32"}'  > /opt/monroe/monroe-mplane/tstat-conf/subnets.txt 2>> $LOG_DIR


### start tstat, it is reading the tstat.conf file on the current directory
cd /opt/monroe/monroe-mplane/
tstat  
