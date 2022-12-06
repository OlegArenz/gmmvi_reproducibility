import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import matplotlib
plt.ion()

my_path = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(my_path, "results")

def plot_best_runs(root_path, num_best, x_column, y_column, axes, subtract_y=0., style=['k']):
    i = 1
    for file in sorted(os.listdir(root_path)):
        full_fname = os.path.join(root_path, file)
        data_frame = pd.read_csv(full_fname)
        data_frame[y_column] -= subtract_y
        data_frame.plot(x_column, y_column, ax=axes, legend=False, color=style, logy=True, alpha=3/(3*i))
        print(data_frame[y_column].min())
        if data_frame[y_column].min() < 0:
            print("debug")
        i += 1
        if i > num_best:
            break

def plot_list(algorithm_names):
    figure = plt.figure()
    colormap = matplotlib.cm.get_cmap(name="tab10", lut=len(algorithm_names))
    for i in range(len(algorithm_names)):
        print(f"plotting {algorithm_names[i]}")
        plot_best_runs(os.path.join(data_path, algorithm_names[i], "best_runs"),
                       3,
                       "runtime",
                       "-elbo",
                       figure.gca(),
                       1320.,
                       style=[colormap(i / len(algorithm_names))])

def get_best_elbos(experiments):
    best_elbos_per_experiment = dict()
    for experiment in experiments:
        experiment_path = os.path.join(data_path, experiment)
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
                best_elbos.update({algorithm_dir: [ best_elbo, config.values[0]] })
            else:
                best_elbos.update({algorithm_dir: [ best_elbo, config.values[0]] })

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
    best_elbos = best_elbo_per_choice(["gmmvi_exp1_wine", "gmmvi_exp1_bc", "gmmvi_exp1_bcmb"], "siytfdr")


    plot_list(["gmmvi_exp1_wine/septrux", "gmmvi_exp1_wine/sepyrux", "gmmvi_exp1_wine/sepirux"])
    print("done")