#!/bin/bash
# This script creates a temporary copy of every yml file with a modified slurm time-limit and run it with clusterwork
# First argument is the new timelimit in slurm format, Second argument is the experiment that should be run
for file in configs/exp3\ \(hyperopt\)/*
  do mkdir -p "tmp/"
  CONFFILE=bc_`basename "$file"`
  cp "$file" tmp/$CONFFILE
  sed -i "tmp/$CONFFILE" -e s/2-00:00:00/$1/
  python clusterwork.py $CONFFILE -e $2 -s
done
