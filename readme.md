
# mPlane 
**Background:**
The [mPlane](http://www.ict-mplane.eu/) protocol provides control and data interchange for passive and active network measurement tasks. 
It is built around a simple workflow in which can be plugged in different frameworks to interact with them to provide the result of the measurement. It possibly can do more sophisticated analysis by mean of intelligent reasoner.
This package includes a mPlane proxy and generic configuration files for [Tstat](http://www.tstat.polito.it/).

A new branch in mPlane page added for Monroe project, see [here](https://github.com/fp7mplane/protocol-ri/tree/monroe).

The mPlane experiment directory contains the Tstat v.3 debian package and script to make docker image and run the tstat in run.sh. 

Tstat RRD logs and compressed log stored on host node in /experiments/monroe/mplane respectively. These are exported to the monroe remote repository via management interface. The latest three generated Tstat's logs are shared with monroe experimenters on the "/monroe/tstat", it helps the Monroe users to use passive traces collected by Tstat during their experiment. 
The Tstat logs are imported into MONROE database, you can find the schema of the tables [here](https://github.com/MONROE-PROJECT/Database/blob/master/db_schema.cql).

The mplane docker image pushed into [monroe/mplane](https://hub.docker.com/r/monroe/mplane/). 


## Requirements
The script must be able to have access to /nodeid and run get_nodeid. 

## Example usage
Create the docker image:
* make image
 
Run the container:
* docker run -i -t --net=host -d -v /mplane:/monroe/results -v /tstat:/monroe/tstat -v /etc/nodeid:/nodeid:ro monroe/mplane
 

## Docker misc usage

docker ps  # list running images

docker exec -it [container id] bash   # attach to running container
