for file in configs/exp3\ \(hyperopt\)/s*
do
  ./run_conf_with_different_timelimit.sh "$file" 2-00:00:00 STM300 12
done
