#!/bin/sh
PASS=$1
LOG_DIR="/var/log/syslog"
TSTAT_LOG="/tmp/tstat.log"
ROOT_PATH="/opt/monroe/monroe-mplane/"
SUP_IP="130.192.181.137"
TSTAT="start_tstat.sh"
SETUP_PROXY="setup_proxy.sh"

echo "mPlane Container starts !"

TSTAT_PID=10000
PROXY_PID=99999

# Create the log directories if dont exist
if [ ! -d /outdir ]
then
	echo "mkdir outdir !"
	mkdir /outdir
fi
if [ ! -d /outdir/tstat_rrd ]
then
	echo "mkdir tstat_rrd !"
	mkdir /outdir/tstat_rrd
fi
if [ ! -d /outdir/tstat_log ]
then
	echo "mkdir tstat_log !"
	mkdir /outdir/tstat_log
fi

tar -xvzf protocol-ri.tar.gz 2>>$LOG_DIR  1>>$TSTAT_LOG
rm  protocol-ri.tar.gz

# Main loop for mPlane container
while true; 
do
# If the tstat is not running, start it

if ! ps -p $TSTAT_PID > /dev/null  
then 
	#Removing the laatest log
	rm -rf $TSTAT_LOG &> /dev/null
	bash $ROOT_PATH$TSTAT  2>>$LOG_DIR  1>>$TSTAT_LOG &
	TSTAT_PID=$!

	echo "TSTAT_PID "  $TSTAT_PID
fi

# If the tstat-proxy is not running, start it

if ! ps -p $PROXY_PID > /dev/null 
then 
	# Setup Tstat proxy to interact with Supervisor and Repository
	bash $ROOT_PATH$SETUP_PROXY $SUP_IP $PASS  2>>$LOG_DIR 1>>$TSTAT_LOG  


	# Start Tstat proxy to interact with Supervisor and Repository
	cd "/opt/monroe/monroe-mplane/protocol-ri/" 
	export PYTHONPATH="/opt/monroe/monroe-mplane/protocol-ri/"

	#CHECK AT HOME
	/opt/monroe/monroe-mplane/protocol-ri/scripts/mpcom --config /opt/monroe/monroe-mplane/protocol-ri/mplane/components/tstat/conf/tstat.conf 2>>$LOG_DIR 1>>$TSTAT_LOG &
	PROXY_PID=$!

	echo "PROXY_PID  " $PROXY_PID 

fi

echo "SLEEP 300 !"
sleep 300

done
echo "mPlane Container exit ! "