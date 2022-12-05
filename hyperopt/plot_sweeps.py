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
            best_run = os.path.join(experiment_path, algorithm_dir, 'best_runs', '0.csv')
            best_elbos.update({algorithm_dir: pd.read_csv(best_run)['-elbo'].values[-1]})
        best_elbos_per_experiment.update({experiment: best_elbos})
    return best_elbos_per_experiment

def best_elbo_per_choice(experiments, choices, reduction=np.min):
    best_elbos = get_best_elbos(experiments)
    for experiment in experiments:
        best_elbos_per_experiment = best_elbos[experiment]
        for choice in choices:
            best_elbos_this_choice = [value for key, value in best_elbos_per_experiment.items() if choice in key]
            print(f"Choice: {choice} \t Best Elbos: {reduction(best_elbos_this_choice)}")



if __name__ == "__main__":
    best_elbos = best_elbo_per_choice(["gmmvi_exp1_wine"], "siytfdr", reduction=np.mean)
    plot_list(["gmmvi_exp1_wine/septrux", "gmmvi_exp1_wine/sepyrux", "gmmvi_exp1_wine/sepirux"])
    print("done")