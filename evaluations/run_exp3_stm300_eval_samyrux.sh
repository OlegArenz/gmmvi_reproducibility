for file in configs/exp3\ \(eval\)/samyrux*
do
  ./run_conf_with_different_timelimit.sh "$file" 1-00:00:00 STM300 24
done
