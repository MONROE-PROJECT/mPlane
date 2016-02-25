
# Tstat experiment
**Background:**
The [mPlane](http://www.ict-mplane.eu/) protocol provides control and data interchange for passive and active network measurement tasks. 
It is built around a simple workflow in which can be plugged in different frameworks to interact with them to provide the result of the measurement. It possibly can do more sophisticated analysis by mean of intelligent reasoner.
This package includes a mPlane proxy and generic configuration files for [Tstat](http://www.tstat.polito.it/).

A new branch in mPlane page added for Monroe project, see [here](https://github.com/fp7mplane/protocol-ri/tree/monroe).

The Tstat experiment directory is based on ping experiment and contains the mPlane source code, Tstat v.3 debian package and script to make docker image and run the tstat and proxy in run.sh. 

Tstat RRD logs and compressed log stored on host node in /output/tstat_rrd and /output/tstat_log respectively.
The RRD log exported by the mplane rrd exporter. 

The mplane docker image pushed into monroe1.cs.kau.se:5000/monroe/tstat. For user and password contact KaU.

TODO: 
* using Monroe metadata exporter to export /output/tstat_log
* Test --net=none


## Requirements
The script must be able to have access to /nodeid and run get_nodeid. 
These directories must exist and be writable by the user/process:    
/output/    
/tmp/    

## Example usage
Create the docker image:
* make image
 
Run the container:
* docker run --net=host -d -v /outdir:/outdir -v /etc/nodeid:/nodeid:ro monroe1.cs.kau.se:5000/monroe/tstat PASSPHRASE
(send an email to ali.safari@polito.it to know PASSPHRASE)

## Docker misc usage

docker ps  # list running images

docker exec -it [container id] bash   # attach to running container
