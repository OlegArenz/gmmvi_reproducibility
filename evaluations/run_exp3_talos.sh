for file in configs/exp3\ \(hyperopt\)/*
do
  ./run_conf_with_different_timelimit.sh "$file" 1-00:00:00 TALOS 12
done
