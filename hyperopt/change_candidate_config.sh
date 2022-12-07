# changes a candidate config (eg. saptrux.yml to samtrux.yml), by renaming the algorithm_id inside the config and the name of the yml file. If the new candidate uses different hyperparameters, they need to be modified adapted manually
for file in *.yml; do OLDNAME=`echo $file | cut -c1-7`; NEWNAME=`echo $OLDNAME | sed 's/p/m/'`; sed -i "s/$OLDNAME/$NEWNAME/" $file ; mv $file ${NEWNAME}.yml ; done