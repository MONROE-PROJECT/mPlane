#!/bin/bash 
# This script start tstat proxy

# HOW TO RUN
# sudo bash start_proxy.sh 

cd "/opt/monroe/monroe-mplane/protocol-ri/" 

echo $PWD
export PYTHONPATH="/opt/monroe/monroe-mplane/protocol-ri/"


/opt/monroe/monroe-mplane/protocol-ri/scripts/mpcom --config /opt/monroe/monroe-mplane/protocol-ri/mplane/components/tstat/conf/tstat.conf
