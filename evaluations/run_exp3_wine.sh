for file in configs/exp3\ \(hyperopt\)/sam*
do
  ./run_conf_with_different_timelimit.sh "$file" 1-00:00:00 WINE 4
done
