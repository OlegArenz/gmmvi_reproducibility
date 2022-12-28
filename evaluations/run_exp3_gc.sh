for file in configs/exp3\ \(hyperopt\)/*
do
  ./run_conf_with_different_timelimit.sh "$file" 0-02:00:00 GC
done
