#!/bin/bash
# the tstat Version 3.0 should been installed on the mPlane container
# The script sets the directories and starts the Tstat
# The Tstat configuration files are in 'tstat-conf' directory
# TODO specify  internal and external network

# HOW TO RUN 
# sudo bash start_tstat.sh


###  SETUP
LOG_DIR="/var/log/syslog"
NODEID_PATH="/nodeid" 

date &>> $LOG_DIR

if [ -s $NODEID_PATH ]
then
	read -r NODE_ID < $NODEID_PATH 2>>$LOG_DIR
else
	bash get_node_id.sh 2>>$LOG_DIR
	read -r NODE_ID < $NODEID_PATH 2>>$LOG_DIR
fi

if [ -z $NODE_ID ]
then
	echo "There is NO NodeID in /nodeid !" 
	exit $?
fi
if [ ! -d "/outdir/"$NODE_ID ]
then
	echo "mkdir /outdir/"$NODE_ID" !"
	mkdir "/outdir/"$NODE_ID
fi

cd /opt/monroe/monroe-mplane/
sed -i "/-s/c\-s \/outdir\/"$NODE_ID"        # output dir for log files" tstat.conf 2>> $LOG_DIR
### Sitting the tstat-conf/subnets.txt file to distinguish between the internal and external networks
ip -4  addr  | grep inet | awk '{print $2}' > tstat-conf/subnets.txt 2>> $LOG_DIR

### start tstat, it is reading the tstat.conf file on the current directory
tstat  
