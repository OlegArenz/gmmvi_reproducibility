import os.path

import numpy as np
import wandb
import pandas as pd
import pathlib
from tqdm import tqdm

def summarize_sweep(sweep):
    summary_list, config_list, name_list, elbo_list, history_list = [], [], [], [], []
    for run in tqdm(sweep.runs):
        # .summary contains the output keys/values for metrics like accuracy.
        #  We call ._json_dict to omit large files
        summary_list.append(run.summary._json_dict)
        history_list.append(run.history())
        try:
            elbo_list.append(history_list[-1]["-elbo"].to_numpy()[-1])
        except:
            elbo_list.append(np.Inf)
        # .config contains the hyperparameters.
        #  We remove special values that start with _.
        config_list.append(
            {k: v for k,v in run.config.items()
             if not k.startswith('_')})

        # .name is the human-readable name of the run.
        name_list.append(run.name)

    return summary_list, config_list, name_list, history_list, elbo_list

def process_sweep(api, sweep_names):
    sweep_name_to_id = get_sweep_ids()
    for sweep_name in sweep_names:
        print(f"processing sweep {sweep_name}")
        path = os.path.join("../../../data", sweep_name)
        best_run_path = pathlib.Path(os.path.join(path, "best_runs"))
        best_run_path.mkdir(parents=True, exist_ok=True)
        fully_fetched = pathlib.Path(os.path.join(path, "FETCHED"))

        sweep_id = sweep_name_to_id[sweep_name]
        sweep = api.sweep("joa/SteinVIPS/"+sweep_id)
        if sweep_name != sweep.name:
            print(f"{sweep_name} vs {sweep.name}")
        assert (sweep_name == sweep.name)

        if os.path.exists(fully_fetched):
            print(f"sweep {sweep_name} was already fetched")
            continue

        summary_list, config_list, name_list, history_list, elbo_list = summarize_sweep(sweep)

        runs_df = pd.DataFrame({
            "summary": summary_list,
            "config": config_list,
            "name": name_list,
            "-elbos": elbo_list
        })

        runs_df.to_csv(os.path.join(path,"all_sweeps.csv"))
        best_run_ids = np.argsort(elbo_list)[0:30]
        for i in range(len(best_run_ids)):
            history_list[best_run_ids[i]].to_csv(os.path.join(best_run_path, str(i) + ".csv"))
        fully_fetched.touch()

def get_sweep_ids():
    sweep_name_to_id = dict()
    with open('sweep_names.txt', 'r') as file:
        for line in file:
            key, value = line.split()
            sweep_name_to_id.update({key: value})
    return sweep_name_to_id

if __name__ == "__main__":
    api = wandb.Api(timeout=30)

    process_sweep(api, sweep_names=["pismok", "pismol", "pismou",
                                    "pizmok", "pizmol", "pizmou",
                                    "pysmok", "pysmol", "pysmou",
                                    "pyzmok", "pyzmol",  #"pyzmou_bc",
                                    "prsmok", "prsmol", "prsmou",
                                    "przmok", "przmol", "przmou",
                                    "pismok_bc64", "pismol_bc64", "pismou_bc64",
                                    "pizmok_bc64", "pizmol_bc64", "pizmou_bc64",
                                    "pysmok_bc64", "pysmol_bc64", "pysmou_bc64",
                                    "pyzmok_bc64", "pyzmol_bc64",  # "pyzmou_bc64",
                                    "prsmok_bc64", "prsmol_bc64", "prsmou_bc64",
                                    "przmok_bc64", "przmol_bc64", "przmou_bc64",
                                    ])
    print("done")




