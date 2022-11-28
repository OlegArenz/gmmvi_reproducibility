import os.path

import numpy as np
import wandb
import pandas as pd
import pathlib
from tqdm import tqdm


def summarize_sweep(sweep):
    summary_list, config_list, name_list, elbo_list, history_list = [], [], [], [], []
    for run in tqdm(sweep.runs):
        summary_list.append(run.summary._json_dict)
        cheap_metrics = run.scan_history(keys=["_step", "walltime", "num_samples", "num_components"])
        expensive_metrics = pd.DataFrame(run.scan_history(keys=["-elbo", "entropy", "target_density", "_step"]))
        if len(expensive_metrics) < 10:
            print(f"\n skipping run {run.name} because it only has {len(expensive_metrics)} elbo evaluations")
            continue
        # add runtime to the dataframe
        runtimes = np.cumsum([row["walltime"] for row in cheap_metrics])
        expensive_metrics["runtime"] = runtimes[expensive_metrics['_step'].values]

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


def process_sweep(api, sweep_names):
    sweep_name_to_id = get_sweep_ids()
    for sweep_name in sweep_names:
        print(f"processing sweep {sweep_name}")
        path = os.path.join("results", sweep_name)
        best_run_path = pathlib.Path(os.path.join(path, "best_runs"))
        best_run_path.mkdir(parents=True, exist_ok=True)
        fully_fetched = pathlib.Path(os.path.join(path, "FETCHED"))

        sweep_id = sweep_name_to_id[sweep_name]
        sweep = api.sweep(sweep_id)
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

        runs_df.to_csv(os.path.join(path, "all_sweeps.csv"))
        best_run_ids = np.argsort(elbo_list)[0:30]
        for i in range(len(best_run_ids)):
            pd.DataFrame(history_list[best_run_ids[i]]).to_csv(os.path.join(best_run_path, str(i) + ".csv"))
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

    process_sweep(api, sweep_names=["zemifux_bc", "zemidux_bc"])
    print("done")
