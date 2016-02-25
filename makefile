
include common.mk

CONTAINER:=tstat
RUNOPTIONS:=--net=host -v /outdir:/outdir -v /etc/config/nodeid:/nodeid:ro 

run-fixme:
	docker run --net=host -d -v /outdir:/outdir -v /etc/config/nodeid:/nodeid:ro monroe/tstat  