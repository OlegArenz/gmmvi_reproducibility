import pandas as pd
import numpy as np
import os
import h5py

def mat2csv(input_folder, output_folder):
    for file in os.listdir(input_folder):
        if not file.endswith("mat"):
            continue
        f = h5py.File(os.path.join(input_folder, file))
        indices = np.where(np.array(f["track_elbos"]) != 0)
        dat = np.stack((np.array(f["track_n_fevals"])[indices], -np.array(f["track_elbos"])[indices]))
        outfile = os.path.join(output_folder, file[:-3]+"csv")
        pd.DataFrame(dat.T, columns=["num_samples", "-elbo"]).to_csv(outfile)

if __name__ == "__main__":
    mat2csv("/home/oleg/src/i_bayes_rule_matlab/MoG/log/STM300",
            "/home/oleg/src/gmmvi_experiments/evaluations/iBayesLR_results/stm300")
    print("done")