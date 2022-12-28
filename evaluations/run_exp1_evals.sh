# each evaluation can be started by running the corresponding command independently. Drop the "-s" when not using slurm. 
python clusterwork.py "configs/exp1 (update stability)/sep.yml" -e WINE -s
python clusterwork.py "configs/exp1 (update stability)/septrux.yml" -e WINE -s

