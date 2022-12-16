import os
import pandas as pd

DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "results")

def get_best_elbos(experiments):
    best_elbos_per_experiment = dict()
    for experiment in experiments:
        experiment_path = os.path.join(DATA_PATH, experiment)
        best_elbos = dict()
        for algorithm_dir in sorted(os.listdir(experiment_path)):
            all_sweeps = pd.read_csv(os.path.join(experiment_path, algorithm_dir, 'all_sweeps.csv'))
            best_run = os.path.join(experiment_path, algorithm_dir, 'best_runs', '0.csv')
            best_elbo = pd.read_csv(best_run)['-elbo'].values[-1]
            config = all_sweeps[all_sweeps["-elbos"] == best_elbo]['config']
            if len(config) != 1:
                # We recover the config by searching for the final elbo in all_sweeps.csv.
                # If this failed, we could still get it from wandb
                print(f"could not recover config for best run with elbo {best_elbo}")
                best_elbos.update({algorithm_dir: [best_elbo, config.values[0]]})
            else:
                best_elbos.update({algorithm_dir: [best_elbo, config.values[0]]})

        best_elbos_per_experiment.update({experiment: best_elbos})
    return best_elbos_per_experiment

def best_elbo_per_choice(experiments, choices):
    best_elbos = get_best_elbos(experiments)
    for experiment in experiments:
        print(f"processing experiment {experiment}")
        best_elbos_per_experiment = best_elbos[experiment]
        for choice in choices:
            best_candidate_this_choice = sorted([value for key, value in best_elbos_per_experiment.items() if choice in key])[0]
            print(f"Choice: {choice} \t Best Elbo: {best_candidate_this_choice[0]:.2f} \t "
                  f"config: {best_candidate_this_choice[1]}")

if __name__ == "__main__":
    best_elbos_bc = best_elbo_per_choice(["exp1_bc", "exp1_bcmb"], "zsiytfdr")
    best_elbos_wine = best_elbo_per_choice(["exp1_wine"], "siytfdr")