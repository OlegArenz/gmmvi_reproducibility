for file in configs/exp3\ \(eval\)/sam*
do
  ./run_conf_with_different_timelimit.sh "$file" 0-08:00:00 Planar4 5
done
