for file in *.yml; do OLDNAME=`echo $file | cut -c1-7`; NEWNAME=s`echo $file | cut -c2-7`; sed -i "s/$OLDNAME/$NEWNAME/" $file; mv $file ${NEWNAME}.yml; done
