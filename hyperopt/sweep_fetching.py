import os.path

import numpy as np
import wandb
import pandas as pd
import pathlib
from tqdm import tqdm


def summarize_sweep(sweep):
    summary_list, config_list, name_list, elbo_list, history_list = [], [], [], [], []
    for run in tqdm(sweep.runs):
        cheap_metrics = pd.DataFrame(run.scan_history(keys=["_step", "walltime", "num_samples", "num_components"]))
        expensive_metrics = pd.DataFrame(run.scan_history(keys=["-elbo", "entropy", "target_density", "_step"]))
        if len(expensive_metrics) < 10:
            print(f"\n skipping run {run.name} because it only has {len(expensive_metrics)} elbo evaluations")
            continue
        if expensive_metrics["-elbo"].min() < -1000:
            print(f"\n skipping run {run.name} because it suffered from bad conditioning")
            continue
        summary_list.append(run.summary._json_dict)

        # add runtime to the dataframe
        if cheap_metrics['_step'].max() == len(cheap_metrics['walltime'].cumsum().values) -1:
            runtimes = cheap_metrics['walltime'].cumsum().values
            expensive_metrics["runtime"] = runtimes[expensive_metrics['_step'].values]
        else:
            print("some walltimes have been lost")

        history_list.append(expensive_metrics)
        try:
            elbo_list.append(expensive_metrics['-elbo'].iloc[-1])
        except:
            elbo_list.append(np.Inf)

        config_list.append(
            {k: v for k, v in run.config.items()
             if not k.startswith('_')})

        name_list.append(run.name)

    return summary_list, config_list, name_list, history_list, elbo_list


def fetch_sweeps(group_name, project_names, sweep_names):
    api = wandb.Api(timeout=30)
    for project_name in project_names:
        print(f"processing project {project_name}")
        full_project_name = f"gmmvi_{project_name}"
        sweep_name_to_id = get_sweep_ids(full_project_name)
        for sweep_name in sweep_names:
            print(f"processing sweep {sweep_name}")
            path = os.path.join("results", project_name, sweep_name)
            best_run_path = pathlib.Path(os.path.join(path, "best_runs"))
            best_run_path.mkdir(parents=True, exist_ok=True)
            fully_fetched = pathlib.Path(os.path.join(path, "FETCHED"))

            sweep_id = sweep_name_to_id[sweep_name]
            sweep = api.sweep(f"{group_name}/{full_project_name}/{sweep_id}")
            if f"{project_name}_{sweep_name}" != sweep.name:
                print(f"{project_name}_{sweep_name} vs {sweep.name}")
            assert (f"{project_name}_{sweep_name}" == sweep.name)

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

            runs_df.to_csv(os.path.join(path, "all_sweeps.csv"))
            best_run_ids = np.argsort(elbo_list)[0:30]
            for i in range(len(best_run_ids)):
                pd.DataFrame(history_list[best_run_ids[i]]).to_csv(os.path.join(best_run_path, str(i) + ".csv"))
            fully_fetched.touch()


def get_sweep_ids(project_name):
    sweep_name_to_id = dict()
    with open('sweep_names.txt', 'r') as file:
        for line in file:
            this_project_name, key, value = line.split()
            if this_project_name == project_name:
                sweep_name_to_id.update({key: value})
    return sweep_name_to_id



