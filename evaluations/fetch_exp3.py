import numpy as np
import pandas as pd
import wandb
import os
import yaml
import json

api = wandb.Api(timeout=40)


def get_runs(run_name, group_name, project, exact_name=False, bad_run_ids=[]):
    runs = []
    bad_indexes = []
    if exact_name:
        all_runs = api.runs(project, {"group": {"$eq": group_name}})
    else:
        all_runs = api.runs(project, {"group": {"$regex": group_name}})
    for i in range(len(all_runs)):
        if run_name in all_runs[i].name:
            if all_runs[i].id in bad_run_ids:
                bad_indexes.append(i)
                print(f"found bad run {all_runs[i].name} with id {all_runs[i].id}")
            runs.append(all_runs[i])
    return runs, bad_indexes

def fetch_exp3_hyperopt(project, foldername, group_names, metric="-elbo"):
    def fetch_and_save(group_name, foldername, metric):
        runs, _ = get_runs("", group_name, project, exact_name=True)
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

def latex_format(metrics, format, larger_is_better=False):
    all_mean_metrics = np.array([np.mean(metric) for metric in metrics])
    all_ste_metrics = np.array([np.std(metric) * 3 / np.sqrt(len(metric)) for metric in metrics])
    if larger_is_better:
        pessimistic_mean_metric = all_mean_metrics - all_ste_metrics
        optimistic_mean_metric = all_mean_metrics + all_ste_metrics
        maybe_best_mean = optimistic_mean_metric >= np.max(pessimistic_mean_metric)
    else:
        pessimistic_mean_metric = all_mean_metrics + all_ste_metrics
        optimistic_mean_metric = all_mean_metrics - all_ste_metrics
        maybe_best_mean = optimistic_mean_metric < np.min(pessimistic_mean_metric)
    for mean_metric, ste_metric, maybe_best in zip(all_mean_metrics, all_ste_metrics, maybe_best_mean):
        if format == "elbo_format":
            if maybe_best:
                print(f"& \\thead{{$\\mathbf{{\\num{{{mean_metric:.2f}}}}}$ \\\\ "
                      f"$\\mathbf{{\\pm \\num{{{ste_metric:.2f}}}}}$}}")
            else:
                print(f"& \\thead{{$\\num{{{mean_metric:.2f}}}$ \\\\ "
                      f"$\\pm \\num{{{ste_metric:.2f}}}$}}")
        elif format == "mmd_format":
            if maybe_best:
                print(f"& \\thead{{$\\mathbf{{\\num{{{mean_metric:.1e}}}}}$ \\\\ "
                      f"$\\mathbf{{\\pm \\num{{{ste_metric:.0e}}}}}$}}")
            else:
                print(f"& \\thead{{$\\num{{{mean_metric:.1e}}}$ \\\\ "
                      f"$\\pm \\num{{{ste_metric:.0e}}}$}}")
    print("\\\\")

def fetch_exp3_eval(project, foldername, group_names, metric="-elbo", secondary_metrics=[], bad_run_ids=[]):
    np.set_printoptions(precision=3, linewidth=1000)
    def fetch_and_save(group_name, foldername, metric):
        runs, bad_indexes = get_runs("", group_name, project, exact_name=True, bad_run_ids=bad_run_ids)
        histories = [run.scan_history(["_step", "num_samples", "_runtime", metric]
                                                    + secondary_metrics, page_size=10000) for run in runs]
        dataframes = [pd.DataFrame(history) for history in histories]


        group_dir = os.path.join("results", foldername, group_name)
        os.makedirs(group_dir, exist_ok=True)
        all_elbos = []
        all_secondaries = []
        for i in range(len(dataframes)):
            if i in bad_indexes:
                csv_name = f"run_{i}.csv.bad"
            else:
                this_elbo = dataframes[i][metric].to_numpy()[-1]
                if metric == "elbo_fb:":
                    this_elbo = -this_elbo
                all_elbos.append(this_elbo)
                this_secondaries = [dataframes[i][secondary].to_numpy()[-1] for secondary in secondary_metrics]
                all_secondaries.append(np.sum(this_secondaries))
                csv_name = f"run_{i}.csv"
            dataframes[i].to_csv(os.path.join(group_dir, csv_name))
            with open(os.path.join(group_dir, f'run_{i}_config.yml'), 'w') as outfile:
                yaml.dump(json.loads(runs[i].json_config), outfile, default_flow_style=False)
        print(f"Elbo: {np.mean(all_elbos):.2f} +/- {3/np.sqrt(len(all_elbos)) * np.std(all_elbos):.2f}  "
              f"All Elbos: {np.sort(all_elbos)}")
        print(f"Secondary: {np.mean(all_secondaries):.1e} +/- "
              f"{3/np.sqrt(len(all_secondaries)) * np.std(all_secondaries):.0e} "
              f" All Secondaries: {np.sort(all_secondaries)}")
        return all_elbos, all_secondaries
        print("----------------------------")

    all_elbos = []
    all_secondaries = []
    for group_name in group_names:
        print(f"fetching {group_name}")
        this_elbos, this_secondaries = fetch_and_save(group_name, foldername, metric)
        all_elbos.append(this_elbos)
        all_secondaries.append(this_secondaries)
    latex_format(all_elbos, format="elbo_format")
    larger_is_better = False
    if secondary_metrics[0] == 'num_detected_modes':
        secondary_format = "elbo_format"
        larger_is_better = True
    elif secondary_metrics[0] == 'entropy':
        secondary_format = "elbo_format"
        larger_is_better = True
    elif secondary_metrics[0] == 'MMD:':
        secondary_format = "mmd_format"
    elif secondary_metrics[0] == "bi_test_loss":
        secondary_format = "elbo_format"
        larger_is_better = False
    latex_format(all_secondaries, format=secondary_format, larger_is_better=larger_is_better)

    print("done")

if __name__ == "__main__":
    fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "BC",
                       ["samtron_bc", "samtrux_bc", "samtrox_bc",
                        "samyron_bc", "samyrux_bc", "samyrox_bc",
                        "zamtrux_bc", "sepyfux_bc", "sepyrux_bc"])
    fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "GC",
                        ["samtron_gc", "samtrux_gc", "samtrox_gc",
                         "samyron_gc", "samyrux_gc", "samyrox_gc",
                         "zamtrux_gc", "sepyfux_gc", "sepyrux_gc"])
    fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "BC_MB",
                        ["samtron_bcmb", "samtrux_bcmb", "samtrox_bcmb",
                         "samyron_bcmb", "samyrux_bcmb", "samyrox_bcmb",
                         "zamtrux_bcmb", "sepyfux_bcmb", "sepyrux_bcmb"],
                        metric="elbo_fb:")
    fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "GC_MB",
                        ["samtron_gcmb", "samtrux_gcmb", "samtrox_gcmb",
                         "samyron_gcmb", "samyrux_gcmb", "samyrox_gcmb",
                         "zamtrux_gcmb", "sepyfux_gcmb", "sepyrux_gcmb"],
                        metric="elbo_fb:")
    fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "Planar4",
                         ["samtron_planar_4", "samtrux_planar_4", "samtrox_planar_4",
                          "samyron_planar_4", "samyrux_planar_4", "samyrox_planar_4",
                          "zamtrux_planar_4", "sepyfux_planar_4", "sepyrux_planar_4"])
    fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "GMM20",
                        ["samtron_gmm20", "samtrux_gmm20", "samtrox_gmm20",
                         "samyron_gmm20", "samyrux_gmm20", "samyrox_gmm20",
                         "zamtrux_gmm20", "sepyfux_gmm20", "sepyrux_gmm20"])
    fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "GMM100",
                        ["samtron_gmm100", "samtrux_gmm100", "samtrox_gmm100",
                         "samyron_gmm100", "samyrux_gmm100", "samyrox_gmm100",
                         "zamtrux_gmm100", "sepyfux_gmm100", "sepyrux_gmm100"])
    fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "STM20",
                         ["samtron_stm20", "samtrux_stm20", "samtrox_stm20",
                          "samyron_stm20", "samyrux_stm20", "samyrox_stm20",
                          "zamtrux_stm20", "sepyfux_stm20", "sepyrux_stm20"])
    fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "STM300",
                         ["samtron_stm300", "samtrux_stm300", "samtrox_stm300",
                          "samyron_stm300", "samyrux_stm300", "samyrox_stm300",
                          "sepyfux_stm300", "sepyrux_stm300"])
    fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "WINE",
                         ["samtron_WINE", "samtrux_WINE", "samtrox_WINE",
                          "samyron_WINE", "samyrux_WINE", "samyrox_WINE",
                          "zamtrux_WINE", "sepyfux_WINE", "sepyrux_WINE"])
    fetch_exp3_hyperopt("amortizedvips/gmmvi-exp3", "TALOS",
                    ["samtrux_talos", "samtrox_talos", "samtron_talos",
                     "samyrux_talos", "samyrox_talos", "samyron_talos",
                     "sepyfux_talos", "sepyrux_talos", "zamtrux_talos"])
    # fetch_exp3_eval("amortizedvips/gmmvi-exp3-eval", "BC_EVAL",
    #                     [ "samtrux_bc", "samtrox_bc", "samtron_bc",
    #                       "samyrux_bc", "samyrox_bc", "samyron_bc",
    #                       "sepyfux_bc", "sepyrux_bc", "zamtrux_bc"],
    #                 secondary_metrics=["MMD:"])
    # fetch_exp3_eval("amortizedvips/gmmvi-exp3-eval", "BCMB_EVAL",
    #                     [ "samtrux_bcmb2", "samtrox_bcmb2", "samtron_bcmb2",
    #                       "samyrux_bcmb2", "samyrox_bcmb2", "samyron_bcmb2",
    #                       "sepyfux_bcmb2", "sepyrux_bcmb2", "zamtrux_bcmb2"],
    #                 metric="elbo_fb:", secondary_metrics=["MMD:"])
    # fetch_exp3_eval("amortizedvips/gmmvi-exp3-eval", "GC_EVAL",
    #                     [ "samtrux_gc", "samtrox_gc", "samtron_gc",
    #                       "samyrux_gc", "samyrox_gc", "samyron_gc",
    #                       "sepyfux_gc", "sepyrux_gc", "zamtrux_gc"],
    #                 secondary_metrics=["MMD:"])
    # fetch_exp3_eval("amortizedvips/gmmvi-exp3-eval", "GCMB_EVAL",
    #                     [ "samtrux_gcmb", "samtrox_gcmb", "samtron_gcmb",
    #                       "samyrux_gcmb", "samyrox_gcmb", "samyron_gcmb",
    #                       "sepyfux_gcmb", "sepyrux_gcmb", "zamtrux_gcmb"],
    #                 metric="elbo_fb:", secondary_metrics=["MMD:"])
    # fetch_exp3_eval("amortizedvips/gmmvi-exp3-eval", "Planar4_EVAL",
    #                 ["samtrux_planar_4", "samtrox_planar_4", "samtron_planar_4",
    #                  "samyrux_planar_4", "samyrox_planar_4", "samyron_planar_4",
    #                  "sepyfux_planar_4", "sepyrux_planar_4", "zamtrux_planar_4"],
    #                 secondary_metrics=["MMD:"],
    #                 bad_run_ids=["3hfd8d6r", "3ptff3cu", "19lh811c", "3qhcxgvh", "2b9xffe6", # sepyfux
    #                              "jibizjlr", "2v0v0r5s", "1jh2pf0h", # sepyrux
    #                              "3oca1dfq", "2ls1np1b" # zamtrux
    #                             ])
    # fetch_exp3_eval("amortizedvips/gmmvi-exp3-eval", "GMM20_EVAL",
    #                      ["samtrux_gmm20", "samtrox_gmm20", "samtron_gmm20",
    #                       "samyrux_gmm20", "samyrox_gmm20", "samyron_gmm20",
    #                       "sepyfux_gmm20", "sepyrux_gmm20", "zamtrux_gmm20"],
    #                 secondary_metrics=["num_detected_modes"])
    # fetch_exp3_eval("amortizedvips/gmmvi-exp3-eval", "GMM100_EVAL",
    #                      ["samtrux_gmm100", "samtrox_gmm100", "samtron_gmm100",
    #                       "samyrux_gmm100", "samyrox_gmm100", "samyron_gmm100",
    #                       "sepyfux_gmm100", "sepyrux_gmm100", "zamtrux_gmm100"],
    #                 secondary_metrics=["num_detected_modes"])
    # fetch_exp3_eval("amortizedvips/gmmvi-exp3-eval", "STM20_EVAL",
    #                 ["samtrux_stm20", "samtrox_stm20", "samtron_stm20",
    #                  "samyrux_stm20", "samyrox_stm20", "samyron_stm20",
    #                  "sepyfux_stm20", "sepyrux_stm20", "zamtrux_stm20"],
    #                 secondary_metrics=["num_detected_modes"])
    # fetch_exp3_eval("amortizedvips/gmmvi-exp3-eval", "STM300_EVAL",
    #                 ["samtrux_stm300", "samtrox_stm300", "samtron_stm300",
    #                  "samyrux_stm300", "samyrox_stm300", "samyron_stm300",
    #                  "sepyfux_stm300", "sepyrux_stm300"],
    #                 secondary_metrics=["num_detected_modes"])
    # fetch_exp3_eval("amortizedvips/gmmvi-exp3-eval", "WINE_EVAL",
    #                 ["samtrux_WINE", "samtrox_WINE", "samtron_WINE",
    #                  "samyrux_WINE", "samyrox_WINE", "samyron_WINE",
    #                  "sepyfux_WINE", "sepyrux_WINE", "zamtrux_WINE"],
    #                 secondary_metrics=["bi_test_loss"])
    fetch_exp3_eval("amortizedvips/gmmvi-exp3-eval", "TALOS_EVAL",
                    ["samtrux_talos", "samtrox_talos", "samtron_talos",
                     "samyrux_talos", "samyrox_talos", "samyron_talos",
                     "sepyfux_talos", "sepyrux_talos", "zamtrux_talos"],
                    secondary_metrics=["entropy"],
                    bad_run_ids=["30xiwyyd", "hw5zpafl", "1a1bjuvk", "18gvcw2y", "38a7rluc", "1xwafa5", #sepyfux
                                 "3nueuvbg", "33r9flgq", "3rl7tjx8", "38e8uont", "26owio9t", "1u2ddtm0" # sepyrux
                    ])
