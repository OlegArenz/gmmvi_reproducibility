for file in configs/exp3\ \(hyperopt\)/samtron*
do
  ./run_conf_with_different_timelimit.sh "$file" 1-00:00:00 WINE 12
done
