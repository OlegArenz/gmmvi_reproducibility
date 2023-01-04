import numpy as np
import pandas as pd
import wandb
import os
import yaml
import json

api = wandb.Api(timeout=40)


def get_runs(run_name, group_name, project):
    return [run for run in api.runs(project) if run_name in run.name and group_name in run.group]


def fetch_exp3_hyperopt(project, foldername, group_names, metric="-elbo"):
    def fetch_and_save(group_name, foldername, metric):
        runs = get_runs("", group_name, project)
        dataframes = [pd.DataFrame(run.scan_history(["_step", "num_samples", "_runtime", metric, "num_samples"]))
                      for run in runs]

        group_dir = os.path.join("results", foldername, group_name)
        os.makedirs(group_dir, exist_ok=True)
        best_elbo = np.Inf
        for i in range(len(dataframes)):
            dataframes[i].to_csv(os.path.join(group_dir, f"run_{i}.csv"))
            with open(os.path.join(group_dir, f'run_{i}_config.yml'), 'w') as outfile:
                yaml.dump(json.loads(runs[i].json_config), outfile, default_flow_style=False)
            this_elbo = dataframes[i][metric].to_numpy()[-1]
            if metric == "elbo_fb:":
                this_elbo = -this_elbo
            if this_elbo < best_elbo:
                best_elbo = this_elbo
                best_run = i
        print(f"Run {best_run} has best elbo ({best_elbo})")
        print(json.loads(runs[best_run].json_config))
        print("----------------------------")

    for group_name in group_names:
        print(f"fetching {group_name}")
        fetch_and_save(group_name, foldername, metric)


if __name__ == "__main__":
    #fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "BC",
    #                    ["samtron_bc", "samtrux_bc", "samtrox_bc",
    #                     "samyron_bc", "samyrux_bc", "samyrox_bc",
    #                     "zamtrux_bc", "sepyfux_bc", "sepyrux_bc"])
    # fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "GC",
    #                     ["samtron_gc", "samtrux_gc", "samtrox_gc",
    #                      "samyron_gc", "samyrux_gc", "samyrox_gc",
    #                      "zamtrux_gc", "sepyfux_gc", "sepyrux_gc"])
    # fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "BC_MB",
    #                     ["samtron_bcmb", "samtrux_bcmb", "samtrox_bcmb",
    #                      "samyron_bcmb", "samyrux_bcmb", "samyrox_bcmb",
    #                      "zamtrux_bcmb", "sepyfux_bcmb", "sepyrux_bcmb"],
    #                     metric="elbo_fb:")
    # fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "GC_MB",
    #                     ["samtron_gcmb", "samtrux_gcmb", "samtrox_gcmb",
    #                      "samyron_gcmb", "samyrux_gcmb", "samyrox_gcmb",
    #                      "zamtrux_gcmb", "sepyfux_gcmb", "sepyrux_gcmb"],
    #                     metric="elbo_fb:")
    # fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "Planar4",
    #                      ["samtron_planar_4", "samtrux_planar_4", "samtrox_planar_4",
    #                       "samyron_planar_4", "samyrux_planar_4", "samyrox_planar_4",
    #                       "zamtrux_planar_4", "sepyfux_planar_4", "sepyrux_planar_4"])
    # fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "GMM20",
    #                     ["samtron_gmm20", "samtrux_gmm20", "samtrox_gmm20",
    #                      "samyron_gmm20", "samyrux_gmm20", "samyrox_gmm20",
    #                      "zamtrux_gmm20", "sepyfux_gmm20", "sepyrux_gmm20"])
    fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "GMM100",
                         ["samtron_gmm100", "samtrux_gmm100", "samtrox_gmm100",
                          "samyron_gmm100", "samyrux_gmm100", "samyrox_gmm100",
                          "zamtrux_gmm100", "sepyfux_gmm100", "sepyrux_gmm100"])