
include common.mk

CONTAINER:=mplane
RUNOPTIONS:=--net=host -v /outdir:/outdir -v /etc/config/nodeid:/nodeid:ro