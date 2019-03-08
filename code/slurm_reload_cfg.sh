#!/bin/bash

#RUN AS ROOT!

spath=/etc/slurm-llnl/

logger "Starting slurm reload with new config at $1"

systemctl stop slurmd
systemctl stop slurmctld

cp $spath/slurm.conf $spath/slurm.conf.old

cp $1 $spath/slurm.conf

sleep 5

systemctl start slurmctld

sleep 5

systemctl stop slurmd

logger "slurm conf updated and daemons restarted"

exit
