import os
import pandas as pd
import numpy as np

def get_mean_and_standarderror(root, secondary_metric):
    print(f"\n\n Evaluating {root}")
    candidates = ["sepyrux", "septrux"]
    for candidate in candidates:
        elbos = []
        secondaries = []
        for file in os.listdir(os.path.join(root, candidate)):
            df = pd.read_csv(os.path.join(root, candidate, file))
            elbos.append(df['-elbo'].values[-1])
            secondaries.append(df[secondary_metric].values[-1])
        assert(len(elbos) == 10)
        assert(len(secondaries) == 10)
        print(f"{candidate}(-ELBO): {np.mean(elbos):.2f} \t  +/- {np.std(elbos) * 3 / np.sqrt(10):.2f}")
        print(f"{candidate}({secondary_metric}) {np.mean(secondaries):.3f} \t  +/- {np.std(secondaries) * 3 / np.sqrt(10):.3f}")

if __name__ == "__main__":
    get_mean_and_standarderror("results/exp1_breast_cancer", "MMD:")
    get_mean_and_standarderror("results/exp1_breast_cancer_mb", "MMD:")
    get_mean_and_standarderror("results/exp1_wine", "bi_test_loss")