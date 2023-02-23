import os
import pandas as pd
import numpy as np

def get_mean_and_standarderror(root, candidates, secondary_metric=None):
    print(f"\n\n Evaluating {root}")
    for candidate in candidates:
        elbos = []
        secondaries = []
        for file in os.listdir(os.path.join(root, candidate)):
            if not file.endswith("csv"):
                continue
            df = pd.read_csv(os.path.join(root, candidate, file))
            elbos.append(df['-elbo'].values[-1])
            if secondary_metric is not None:
                secondaries.append(df[secondary_metric].values[-1])
        print(f"{candidate}(-ELBO): {np.mean(elbos):.2f} \t  +/- {np.std(elbos) * 3 / np.sqrt(len(elbos)):.2f}")
        if secondary_metric is not None:
            print(f"{candidate}({secondary_metric}) {np.mean(secondaries):.3f} \t  +/- {np.std(secondaries) * 3 / np.sqrt(10):.3f}")

if __name__ == "__main__":
    get_mean_and_standarderror("results/exp1_breast_cancer", ["sepyrux", "septrux"], "MMD:")
    get_mean_and_standarderror("results/exp1_breast_cancer_mb", ["sepyrux", "septrux"], "MMD:")
    get_mean_and_standarderror("results/exp1_wine", ["sepyrux", "septrux"], "bi_test_loss")