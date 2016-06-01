#!/bin/sh
set -e

PASS=$1
LOG_DIR="/var/log/syslog"
TSTAT_LOG="/tmp/tstat.log"
ROOT_PATH="/opt/monroe/monroe-mplane/"
SUP_IP="130.192.181.137"
TSTAT="start_tstat.sh"
SETUP_PROXY="setup_proxy.sh"

echo "mPlane Container starts !"

CURRENT_INTERFACE="NONE"
IP="130.192.181.137"
# Create the log directories if dont exist

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

if [ ! -d /outdir ]
then
    echo "mkdir outdir !"
    mkdir /outdir
fi

if [ ! -d /tstat_log ]
then
    echo "mkdir tstat_log !"
    mkdir /tstat_log
fi


for interface in  $(ip -o link show | awk -F': ' '{if ($2 != "lo" && $2 != "docker0" && $2 != "metadata") print $2}');
do 

    if [ ! -d "/outdir/$NODE_ID/$interface" ]
    then
        echo "/outdir/$NODE_ID/$interface" 
        mkdir -p "/outdir/$NODE_ID/$interface"
    fi

    if [ ! -d "/outdir/tstat_rrd/$interface" ]
    then
        echo "/outdir/tstat_rrd/$interface"
        mkdir -p "/outdir/tstat_rrd/$interface"
    fi

    if [ ! -d "/tstat_log/$interface" ]
    then
        echo "/tstat_log/$interface"
        mkdir -p "/tstat_log/$interface"
    fi


done


if [ -e protocol-ri.tar.gz ]
then
    echo "Extract local copy of protocol-ri !"
    tar -xvzf protocol-ri.tar.gz 2>>$LOG_DIR  1>>$TSTAT_LOG
    rm  protocol-ri.tar.gz
fi

# Main loop for mPlane container
while true;
do
    # If the tstat is not running, start it
    bash $ROOT_PATH$TSTAT  2>>$LOG_DIR  1>>$TSTAT_LOG
    # If the tstat-proxy is not running, start it
    if [ ! "$(netstat -anp | grep '130.192.181.137:8889' | grep -v grep | grep 'ESTABLISHED')" -o ! "$(netstat -anp | grep '130.192.181.142:9000' | grep -v grep | grep 'ESTABLISHED')" -o -z "$( ip link|  grep $CURRENT_INTERFACE | grep -v grep | grep 'UP')" ]; then  
        # Setup Tstat proxy to interact with Supervisor and Repository
        bash $ROOT_PATH$SETUP_PROXY $SUP_IP $PASS  2>>$LOG_DIR 1>>$TSTAT_LOG  
        # Start Tstat proxy to interact with Supervisor and Repository
        cd "/opt/monroe/monroe-mplane/protocol-ri/"
        export PYTHONPATH="/opt/monroe/monroe-mplane/protocol-ri/"
        #Start Tstat Proxy
        for PID in $(ps -ef | grep protocol-ri/mplane/components | grep -v grep | awk '{print $2}'); do
            kill -9 $PID
            sleep 60
        done
        /opt/monroe/monroe-mplane/protocol-ri/scripts/mpcom --config /opt/monroe/monroe-mplane/protocol-ri/mplane/components/tstat/conf/tstat.conf &
        sleep 30
        CURRENT_INTERFACE=$(ip route get $IP | grep -Po '(?<=(dev )).*(?= src)')
    fi    
    sleep 900


    for interface in  $(ip -o link show | awk -F': ' '{if ($2 != "lo" && $2 != "docker0" && $2 != "metadata") print $2}');
    do 
    DIR="/tstat_log/$interface/"
    LATEST=$(ls -rtl $DIR | tail -n 1 | grep out | awk '{print $NF}')
        for FILE in $(ls -rtl $DIR | grep out | awk '{print $NF}') ; do
            if [ $LATEST != $FILE ]; then
                cp -r $DIR$FILE "/outdir/$NODE_ID/$interface" 
                rm -rf $DIR$FILE
            fi
        done
    done



done
echo "mPlane Container exit ! "
