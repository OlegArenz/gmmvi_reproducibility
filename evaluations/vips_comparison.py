import os

from evaluations.eval_exp1 import get_mean_and_standarderror

my_path = os.path.dirname(os.path.realpath(__file__))
get_mean_and_standarderror(my_path, ["VIPS_results/BreastCancer", "results/BC_EVAL/zamtrux_bc"])
get_mean_and_standarderror(my_path, ["VIPS_results/germanCredit", "results/GC_EVAL/zamtrux_gc"])
get_mean_and_standarderror(my_path, ["VIPS_results/gmm20", "results/GMM20_EVAL/zamtrux_gmm20"])
get_mean_and_standarderror(my_path, ["VIPS_results/planar4", "results/Planar4_EVAL/zamtrux_planar_4"])
