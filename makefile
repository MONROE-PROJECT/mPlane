
include common.mk

CONTAINER:=tstat
RUNOPTIONS:=--net=host -v /outdir:/outdir -v /etc/config/nodeid:/nodeid:ro