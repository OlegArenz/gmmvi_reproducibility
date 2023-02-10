import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

import matplotlib
plt.ion()

colormap = matplotlib.cm.get_cmap(name="CMRmap")
colors = {
    "zamtrux": 0,
    "samtron": 1,
    "samtrox": 2,
    "samtrux": 3,
    "samyron": 4,
    "samyrox": 5,
    "samyrux": 6,
    "sepyfux": 7,
    "sepyrux": 8
}
linestyles = {
    "zamtrux": "-",
    "samtron": ":",
    "samtrox": "-.",
    "samtrux": "--",
    "samyron": ":",
    "samyrox": "-.",
    "samyrux": "--",
    "sepyfux": "-",
    "sepyrux": "--",
}

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


def interpolate_curves(root_path, x_axis, metric):
    samples = []
    metrics = []
    interpolations = []
    for file in sorted(os.listdir(root_path)):
        if not file.endswith("csv"):
            continue
        full_fname = os.path.join(root_path, file)
        data_frame = pd.read_csv(full_fname)
        samples.append(data_frame[x_axis].to_numpy())
        metrics.append(data_frame[metric].to_numpy())
        interpolations.append(interp1d(samples[-1], metrics[-1]))
    min_x = np.max([s[0] for s in samples])
    max_x = np.min([s[-1] for s in samples])
    xs = np.geomspace(min_x, max_x, 300)
    return xs, np.array([curve(xs) for curve in interpolations])

def plot_shaded(xs, curves, color):
    return plt.fill_between(xs, np.min(curves, axis=0), np.max(curves, axis=0), alpha=0.2, color=color)

def plot_means(xs, curves, color, linestyle):
    return plt.plot(xs, np.mean(curves, axis=0), color=color, linestyle=linestyle)[0]

def make_plots(root_dir, x_axis, y_axis, x_limits=None, y_limits=None, negate_y=False):
    plots = []
    legends = []
    for algorithm_dir in os.listdir(root_dir):
        codename = algorithm_dir[:7]
        color = colormap(colors[codename]/len(colors))

        xs, curves = interpolate_curves(os.path.join(root_dir, algorithm_dir), x_axis, y_axis)
        if negate_y:
            curves = -curves
        plot_shaded(xs, curves, color)
        plots.append(plot_means(xs, curves, color, linestyles[codename]))
        legends.append(codename)
    plt.xlim(x_limits)
    plt.ylim(y_limits)
    plt.legend(plots, legends)

if __name__ == "__main__":
    plt.figure(1)
    make_plots(root_dir=os.path.join(my_path, "../evaluations/results/BC_EVAL"),
               x_axis="_runtime",
               y_axis="-elbo",
               x_limits=(300, 3600),
               y_limits=(85, 78.))

    plt.figure(2)
    make_plots(root_dir=os.path.join(my_path, "../evaluations/results/BCMB_EVAL"),
               x_axis="_runtime",
               y_axis="elbo_fb:",
               x_limits=(300, 3600),
               y_limits=(100, 78),
               negate_y=True)

    plt.figure(3)
    make_plots(root_dir=os.path.join(my_path, "../evaluations/results/GC_EVAL"),
               x_axis="_runtime",
               y_axis="-elbo",
               x_limits=(250, 6900),
               y_limits=(585.09, 585.2))

    plt.figure(4)
    make_plots(root_dir=os.path.join(my_path, "../evaluations/results/GCMB_EVAL"),
               x_axis="_runtime",
               y_axis="elbo_fb:",
               x_limits=(300, 6900),
               y_limits=(585.09, 586.4),
               negate_y=True)

    plt.figure(5)
    make_plots(root_dir=os.path.join(my_path, "../evaluations/results/GMM20"),
               x_axis="_runtime",
               y_axis="-elbo",
               x_limits=(0, 1600),
               y_limits=(0., 1.))

    plt.figure(6)
    make_plots(root_dir=os.path.join(my_path, "../evaluations/results/GMM100"),
               x_axis="_runtime",
               y_axis="-elbo",
               x_limits=(0, 1600),
               y_limits=(0., 1.))

    plt.figure(7)
    make_plots(root_dir=os.path.join(my_path, "../evaluations/results/STM20"),
               x_axis="_runtime",
               y_axis="-elbo",
               x_limits=(0, 7100),
               y_limits=(0., 1.))

    plt.figure(8)
    make_plots(root_dir=os.path.join(my_path, "../evaluations/results/STM300"),
               x_axis="_runtime",
               y_axis="-elbo",
               x_limits=(0, 70000),
               y_limits=(14, 28))

    plt.figure(9)
    make_plots(root_dir=os.path.join(my_path, "../evaluations/results/Planar4"),
               x_axis="_runtime",
               y_axis="-elbo",
               x_limits=(0, 24000),
               y_limits=(11, 25))

    plt.figure(10)
    make_plots(root_dir=os.path.join(my_path, "../evaluations/results/WINE"),
               x_axis="_runtime",
               y_axis="-elbo",
               x_limits=(0, 70000),
               y_limits=(1350, 1560))

    plt.figure(11)
    make_plots(root_dir=os.path.join(my_path, "../evaluations/results/TALOS"),
               x_axis="_runtime",
               y_axis="-elbo",
               x_limits=(0, 82000),
               y_limits=(-25, -23))


    plot_list(["exp1_wine/septrux", "exp1_wine/sepyrux", "exp1_wine/sepirux"])
    print("done")
