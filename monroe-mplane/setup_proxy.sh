#!/bin/bash 
# The monroe-mplane folder should be in /opt/monroe/monroe-mplane/
# This script clone the code from monroe branch in the current direcoty and configure the component
# monroe-supervisor.polito.it 130.192.181.137
# HOW TO RUN
# sudo bash setup_proxy 130.192.181.137 passphrase

IP=$1
PASS=$2
protocol_ri_path="/opt/monroe/monroe-mplane/"
relative_path_to_conf="/protocol-ri/mplane/components/tstat/conf/"
conf_file="tstat.conf"
Supervisor_DNS="	monroe-supervisor.polito.it"
LOG_DIR="/var/log/syslog"
NODEID_PATH="/nodeid" 

echo "If there is an error,  check the log file $LOG_DIR"
cd $protocol_ri_path

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


# Clone or Pull the protocol-ri from mPlane's monroe brance on github
if [ -d $protocol_ri_path"/protocol-ri" ]

then
	cd protocol-ri/
	echo "git pull protocol-ri!"
	git pull 2>>$LOG_DIR
	cd ..
else
	# Clone the mplane protocol-ri !
	echo "git clone protocol-ri!"
	git clone -b monroe https://github.com/fp7mplane/protocol-ri.git 2>>$LOG_DIR
fi

# check the certificate for NodeID if does not exist, generate it 
name="Monroe_Node_"$NODE_ID
MPLANE_PKI_DIR=$protocol_ri_path"protocol-ri/PKI/ca"
MINIMUM_SIZE=1024
if [ -s "$MPLANE_PKI_DIR/certs/$name.crt" -a \
	 -s "$MPLANE_PKI_DIR/certs/$name-plaintext.key" -a \
	 -s "$MPLANE_PKI_DIR/certs/$name.key" ] 
then
  	echo "Certificate exist for this NodeID!"
else
	cd "protocol-ri/PKI"
	bash create-component-cert.sh $PASS
	cd ../..
fi

# Configure the tstat.conf
sed -i "/cert =*/c\cert = PKI\/ca\/certs\/Monroe_Node_$NODE_ID.crt" $protocol_ri_path$relative_path_to_conf$conf_file
sed -i "/key =*/c\key = PKI\/ca\/certs\/Monroe_Node_$NODE_ID-plaintext.key" $protocol_ri_path$relative_path_to_conf$conf_file
sed -i "/cert =*/c\cert = PKI\/ca\/certs\/Monroe_Node_$NODE_ID.crt" $protocol_ri_path$relative_path_to_conf"export_"$conf_file
sed -i "/key =*/c\key = PKI\/ca\/certs\/Monroe_Node_$NODE_ID-plaintext.key" $protocol_ri_path$relative_path_to_conf"export_"$conf_file
sed -i '/runtimeconf =/c\runtimeconf = \/opt\/monroe\/monroe-mplane\/tstat-conf\/runtime.conf' $protocol_ri_path$relative_path_to_conf$conf_file
sed -i '/tstat_rrd_path =/c\tstat_rrd_path = \/opt\/monroe-mplane\/rrd_tstat\/' $protocol_ri_path$relative_path_to_conf$conf_file
sed -i '/client_host = 127.0.0.1/c\client_host = 130.192.181.137' $protocol_ri_path$relative_path_to_conf$conf_file
sed -i '/listen-cap-link*/c\listen-cap-link = https:\/\/130.192.181.137:8888\/' $protocol_ri_path$relative_path_to_conf$conf_file
sed -i "s/System_ID.*/System_ID = $NODE_ID/g" $protocol_ri_path$relative_path_to_conf$conf_file
sed -i "s/tStat-Proxy.*)/tStat-Proxy-$NODE_ID\")/g" $protocol_ri_path"/protocol-ri/mplane/components/tstat/tstat.py"
