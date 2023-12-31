#!/bin/bash
# This script creates a temporary copy of every yml file with a modified slurm time-limit and run it with clusterwork
# First argument is the new timelimit in slurm format, Second argument is the experiment that should be run
FILE=$1

mkdir -p "tmp/"
CONFFILE=$3_`basename "$FILE"`
cp "$FILE" tmp/$CONFFILE
sed -i "tmp/$CONFFILE" -e s/2-00:00:00/$2/ -e "s/cpus-per-task: 3/cpus-per-task: $4/"
python clusterwork.py "tmp/$CONFFILE" -e $3 -s -o
echo $CONFFILE started
