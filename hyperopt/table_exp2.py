import os
import pandas as pd

DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "results")

from table_exp1 import best_elbo_per_choice

if __name__ == "__main__":
    best_elbos_bc = best_elbo_per_choice(["exp2_gmm", "exp2_stm", "exp2_planar4"], "eapmuoxgn")
