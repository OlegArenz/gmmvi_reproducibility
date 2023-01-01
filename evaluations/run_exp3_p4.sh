for file in configs/exp3\ \(hyperopt\)/*
do
  ./run_conf_with_different_timelimit.sh "$file" 0-08:00:00 Planar4 4
done
