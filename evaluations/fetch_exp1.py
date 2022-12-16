import pandas as pd
import wandb
import os

api = wandb.Api(timeout=30)


def get_runs(run_name, group_name, project):
    return [run for run in api.runs(project) if run_name in run.name and group_name in run.group]


def fetch_exp1(project):
    def fetch_and_save(run_name, second_metric, foldername, max_time):
        septrux_runs = get_runs(run_name, "septrux", project)
        sepyrux_runs = get_runs(run_name, "sepyrux", project)
        septrux_dfs = [pd.DataFrame(run.scan_history(["_step", "_runtime", "-elbo", "num_samples", second_metric]))
                            for run in septrux_runs]
        sepyrux_dfs = [pd.DataFrame(run.scan_history(["_step", "_runtime", "-elbo", "num_samples", second_metric]))
                            for run in sepyrux_runs]
        septrux_cut = [dataframe[dataframe["_runtime"] <= max_time] for dataframe in septrux_dfs]
        sepyrux_cut = [dataframe[dataframe["_runtime"] <= max_time] for dataframe in sepyrux_dfs]

        septrux_dir = os.path.join("results", foldername, "septrux")
        os.makedirs(septrux_dir, exist_ok=True)
        for i in range(len(septrux_cut)):
            septrux_cut[i].to_csv(os.path.join(septrux_dir, f"run_{i}.csv"))

        sepyrux_dir = os.path.join("results", foldername, "sepyrux")
        os.makedirs(sepyrux_dir, exist_ok=True)
        for i in range(len(sepyrux_cut)):
            sepyrux_cut[i].to_csv(os.path.join(sepyrux_dir, f"run_{i}.csv"))

    fetch_and_save("WINE", "bi_test_loss", "exp1_wine", 10800)  # First runs went OOM shortly after 3 hours
    fetch_and_save("BC_", "MMD:", "exp1_breast_cancer", 18000)
    fetch_and_save("BCMB", "MMD:", "exp1_breast_cancer_mb", 18000)

if __name__ == "__main__":
    fetch_exp1("amortizedvips/gmmvi-evals")