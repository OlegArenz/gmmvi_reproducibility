for file in configs/matlab_comparison/*
do
  ./run_conf_with_different_timelimit.sh "$file" 1-00:00:00 STM20 4
done
