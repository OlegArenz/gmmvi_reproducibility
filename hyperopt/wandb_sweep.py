
import numpy as np

from gmmvi.gmmvi_runner import GmmviRunner
from gmmvi.configs import load_yaml, get_default_config

import wandb
from mergedeep import merge
import argparse
from time import time


def key_list_to_dict(keys, value):
    if len(keys) == 1:
        return {keys[0]: value}
    else:
        return {keys[0]: key_list_to_dict(keys[1:], value)}


class WandbWorker:
    def __init__(self):
        super().__init__()
        parser = argparse.ArgumentParser(description='Run a worker for a wandb sweep')
        parser.add_argument('--algorithm_id')
        parser.add_argument('--experiment_id')
        parser.add_argument('--sweep_config')
        parser.add_argument('--max_fevals', type=int)
        parser.add_argument('--max_seconds', type=int)
        args = parser.parse_args()
        self.max_fevals = args.max_fevals
        self.max_seconds = args.max_seconds

        config = get_default_config(args.algorithm_id, args.experiment_id)
        config.update({"seed": 1})

        # read the sweep_config to figure out which hyperparameters are chosen by wandb
        parameter_strings = list(load_yaml(args.sweep_config)['parameters'].keys())
        hyperparameter_defaults = dict([(k, -1) for k in parameter_strings])
        wandb.init(config=hyperparameter_defaults, project="gmmvi_sweeps", entity="joa",
                   dir="/work/scratch/j_arenz/wandb")

        # The hyperparameters chosen by wandb are in wandb.config. We use them to overwrite the default values.
        print(f"wandb.config: {wandb.config}")
        for k, v in wandb.config.items():
            parameter_as_dict = key_list_to_dict(k.split("."), v)
            merge(config, parameter_as_dict)
        print(f"Running with the following config: {config}")

        self.gmmvi_runner = GmmviRunner(config, **config["gmmvi_runner_config"])
        self.initial_entropy = self.gmmvi_runner.get_samples_and_entropy(2000)[1]


    def run(self):
        start_time = time()
        for n in range(self.max_fevals):
            runtime = time() - start_time
            if runtime > self.max_seconds:
                print("stopped due to time limits")
                break
            output_dict = self.gmmvi_runner.iterate_and_log(n)
            wandb.log(output_dict)

            if "-elbo" in output_dict.keys():
                if self.should_early_stop(runtime, output_dict):
                    output_dict.update({"-elbo": np.nan})
                    break

    def should_early_stop(self, runtime, output_dict):
        entropy = output_dict["entropy"]
        elbo = -output_dict["-elbo"]
        num_fevals = self.gmmvi_runner.gmmvi.sample_db.num_samples_written.numpy()
        if entropy - self.initial_entropy > self.gmmvi_runner.gmmvi.sample_selector.target_distribtion.num_dimensions:
            print("Early stopping due to bad conditioning")

        if self.gmmvi_runner.config["environment_name"] == "breastCancer":
          #  if entropy > 1000:
          #      print("Early stopping due to bad conditioning")
          #      return True
            if (runtime > 300) and (elbo < -1000000):
                print("Early stopping due to bad elbo")
                return True
            if ((runtime > 1800) or (num_fevals > 1e6)) and (elbo < -1000):
                print("Early stopping due to bad elbo")
                return True
        if self.gmmvi_runner.config["environment_name"] == "breastCancer_mb":
         #   if entropy > 1000:
         #       print("Early stopping due to bad conditioning")
         #       return True
            if (runtime > 300) and (elbo < -1000000):
                print("Early stopping due to bad elbo")
                return True
            if ((runtime > 1800) or (num_fevals > 1e6)) and (elbo < -5000):
                print("Early stopping due to bad elbo")
                return True
        return False


if __name__ == "__main__":
    worker = WandbWorker()
    worker.run()
