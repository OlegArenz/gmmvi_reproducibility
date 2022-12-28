import numpy as np
import pandas as pd
import wandb
import os
import yaml
import json

api = wandb.Api(timeout=30)


def get_runs(run_name, group_name, project):
    return [run for run in api.runs(project) if run_name in run.name and group_name in run.group]


def fetch_exp2_hyperopt(project, foldername, group_names):
    def fetch_and_save(group_name, foldername):
        runs = get_runs("", group_name, project)
        dataframes = [pd.DataFrame(run.scan_history(["_step", "num_samples", "_runtime", "-elbo", "num_samples"]))
                      for run in runs]

        group_dir = os.path.join("results", foldername, group_name)
        os.makedirs(group_dir, exist_ok=True)
        best_elbo = np.Inf
        for i in range(len(dataframes)):
            dataframes[i].to_csv(os.path.join(group_dir, f"run_{i}.csv"))
            with open(os.path.join(group_dir, f'run_{i}_config.yml'), 'w') as outfile:
                yaml.dump(json.loads(runs[i].json_config), outfile, default_flow_style=False)
            if dataframes[i]["-elbo"].to_numpy()[-1] < best_elbo:
                best_elbo = dataframes[i]["-elbo"].to_numpy()[-1]
                best_run = i
        print(f"Run {best_run} has best elbo ({best_elbo})")

    for group_name in group_names:
        print(f"fetching {group_name}")
        fetch_and_save(group_name, foldername)


if __name__ == "__main__":
    fetch_exp2_hyperopt("amortizedvips/gmmvi-exp3", "BC",
                        ["samtron_bc", "samtrux_bc", "samtrox_bc",
                         "samyron_bc", "samyrux_bc", "samyrox_bc",
                         "zamtrux_bc", "sepyfux_bc", "sepyrux_bc"])