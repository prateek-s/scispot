#!/bin/bash
jobid=$1
logger "Job finished $jobid$"

curl "http://156.56.159.51:7878/?finished=$jobid"


