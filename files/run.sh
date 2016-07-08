#!/bin/sh
# -*- coding: utf-8 -*-

# Author: Ali Safari Khatouni
# Date: June 2016
# License: GNU General Public License v3
# Developed for use by the EU H2020 MONROE project

set -e
LOG_DIR="/var/log/syslog"
ROOT_PATH="/opt/monroe/monroe-mplane/"

echo "mPlane Container starts !"
NODEID_PATH="/nodeid"
TIMER=0

date &>$LOG_DIR

# Read the node id
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

# Create the sub directories for results
RSYNC_DIR="/monroe/results/"$NODE_ID
SHARED_DIR="/monroe/tstat/"$NODE_ID
TSTAT_DIR="/opt/monroe/monroe-mplane/tstat-conf/"


if [ ! -d $RSYNC_DIR ]
then
    mkdir -p $RSYNC_DIR 2>>$LOG_DIR 1>>$LOG_DIR
fi

if [ ! -d $SHARED_DIR ]
then
    mkdir -p $SHARED_DIR 2>>$LOG_DIR 1>>$LOG_DIR
fi

if [ ! -d $SHARED_DIR/tstat_rrd ]
then
    mkdir -p $SHARED_DIR/tstat_rrd 2>>$LOG_DIR 1>>$LOG_DIR
fi


# Main loop for mPlane container
while true;
do
    TIMER=$((TIMER+1))


    # Run Tstat for each interface 
    for INTERFACE in  $(ip -o link show | awk -F': ' '{print $2}' | awk -F "@" '{print $1}' | sed 's/[ \t].*//;/^\(lo\|\)$/d;/^\(docker0\|\)$/d;/^\(metadata\|\)$/d');
    do 
        if [ -z "$(ps -afx | grep -v grep | grep "tstat -l -i $INTERFACE")" ]; then
            tstat -l -i $INTERFACE -f $TSTAT_DIR"filter.txt" -N $TSTAT_DIR"subnets.txt" -R $TSTAT_DIR"rrd.conf" -H $TSTAT_DIR"histo.conf" -T $TSTAT_DIR"runtime.conf" -r $SHARED_DIR"/tstat_rrd/"$INTERFACE -s $SHARED_DIR/$INTERFACE  2>>$LOG_DIR 1>>$LOG_DIR  &    
        fi
    done

    # Python script for fetching the latest updated RRD files
    if [ -z "$(ps -ef | grep "fetch_rrd.py" | grep -v grep | awk '{print $2}')" ]; then  
        # fetch rrd files
        python3 fetch_rrd.py $SHARED_DIR"/tstat_rrd/"  $RSYNC_DIR  2>/dev/null 1>>$LOG_DIR &
    fi      

    TEMP_DIR=$SHARED_DIR"/*/"
    # Keep that last two hours of log before moving to the rsync directory
    # It will be rsynced and remove after few mintues in rsync directory
    for DIR in $TEMP_DIR;
    do
        INTERFACE=$(echo $DIR | awk -F "/" '{print $(NF-1)}')
        LATEST=$(ls -rtl $DIR | tail -n 3 | grep "\.out" | awk '{print $NF}' |  tr -d ' ' | tr "\n" " ")
        EDITING_FOLDER=$(ls -rtl $DIR | tail -n 1 | grep "\.out" | awk '{print $NF}' |  tr -d ' ')


        if [ $TIMER -ge 6 -a $INTERFACE != "tstat_rrd" ]; then
            curl --interface $INTERFACE 192.168.0.1 2>/dev/null 1>>$LOG_DIR 
        fi


        for FILE in $(ls -rtl $DIR | grep "\.out" | awk '{print $NF}' |  tr -d ' ') ; do
            Found="false"
            for line in $LATEST ; do
                if [ ! -d $RSYNC_DIR/$INTERFACE/ ] ; then
                    mkdir $RSYNC_DIR/$INTERFACE/
                fi 
                if [ "$line" = "$FILE" ] ; then
                    Found="true"
                fi
            done

            for f in $(find $DIR$FILE -type f -not -name '*.gz'); do
                gzip -k -c $f > $f".gz" 
            done

            if [ "$EDITING_FOLDER" != "$FILE" ] ; then
                for f in $(find $DIR$FILE -type f -not -name '*.gz' ); do
                    rm $f
                done

            elif [ "$EDITING_FOLDER" = "$FILE" ] ; then
                rsync -r --include='*gz' --include="$FILE/" --include='*/' --exclude='*' $DIR$FILE $RSYNC_DIR/$INTERFACE/  2>/dev/null 1>>$LOG_DIR
            fi

            if [ "$Found" = "false" ] ; then
                rm -rf $DIR$FILE  2>/dev/null 1>>$LOG_DIR
            fi
        done
    done    
    sleep 10

    # Generate fake traffic to  modem to regulate the tstat folder creation in low traffic load
    if [ $TIMER -ge 6 ]; then
        TIMER=0       
    fi

done
echo "mPlane Container exit ! "
