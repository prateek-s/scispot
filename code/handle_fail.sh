#!/bin/bash
jobid=$1
logger "Job failed $jobid$"

curl "http://156.56.159.51:7878/?preempted=$jobid"

