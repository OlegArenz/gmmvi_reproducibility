for file in configs/exp3\ \(hyperopt\)/*
do
  ./run_conf_with_different_timelimit.sh "$file" 0-00:30:00 GMM20 4
done
