import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
plt.ion()

def plot_best_runs(root_path, num_best, x_column, y_column, axes, subtract_y=0., style=['k']):
    i = 1
    for file in sorted(os.listdir(root_path)):
        full_fname = os.path.join(root_path, file)
        data_frame = pd.read_csv(full_fname)
        data_frame[y_column] -= subtract_y
        data_frame.plot(x_column, y_column, ax=axes, legend=False, style={"color": style}, logy=True, alpha=1/i)
        print(data_frame[y_column].min())
        if data_frame[y_column].min() < 0:
            print("debug")
        i+=1
        if i > num_best:
            break

def plot_list(algorithm_names):
    my_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(my_path, "../../../data")
    figure = plt.figure()
    colormap = matplotlib.cm.get_cmap(name="tab10", lut=len(algorithm_names))
    for i in range(len(algorithm_names)):
        print(f"plotting {algorithm_names[i]}")
        plot_best_runs(os.path.join(data_path, algorithm_names[i], "best_runs"),
                       1,
                       "_runtime",
                       "-elbo",
                       figure.gca(),
                       78.,
                       style=[colormap(i / len(algorithm_names))])

if __name__ == "__main__":
    plot_list(["pismok", "pismou",
                "pizmok", "pizmol", "pizmou",
                "pysmok", "pysmol", "pysmou",
                "pyzmok", "pyzmol",
                "prsmok", "prsmol", "prsmou",
                "przmok", "przmol", "przmou"])
    print("done")