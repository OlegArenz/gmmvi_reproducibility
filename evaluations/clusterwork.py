from gmmvi.gmmvi_runner import GmmviRunner

from cw2 import experiment, cw_error
from cw2.cw_data import cw_logging
from cw2 import cluster_work
from cw2.cw_data.cw_wandb_logger import WandBLogger
from gmmvi.configs import get_default_config, update_config


class VIPSIterativeExperiment(experiment.AbstractIterativeExperiment):
    def initialize(self, config: dict, rep: int, logger: cw_logging.LoggerArray) -> None:
        # Get configs for experiment and algorithm based on the provided strings
        default_cfg = get_default_config(config["algorithm_id"], config["experiment_id"])

        # overwrite default parameters
        gmmvi_cfg = update_config(default_cfg, config["params"])
        gmmvi_cfg["seed"] = gmmvi_cfg["start_seed"] + rep  # each repetition increments the seed
        print(f"using seed {gmmvi_cfg['seed']}")

        # We also update config["params"] (sent to wandb by WandBLogger) so that wandb knows about the hyperparameters
        config["params"] = update_config(config["params"], gmmvi_cfg)

        self.gmmvi_runner = GmmviRunner(gmmvi_cfg, **gmmvi_cfg["gmmvi_runner_config"])

    def iterate(self, cw_config: dict, rep: int, n: int):
        return self.gmmvi_runner.iterate_and_log(n)

    def save_state(self, cw_config: dict, rep: int, n: int) -> None:
        self.gmmvi_runner.log_to_disk(n)

    def finalize(self, surrender: cw_error.ExperimentSurrender = None, crash: bool = False):
        self.gmmvi_runner.finalize()


if __name__ == "__main__":
    cw = cluster_work.ClusterWork(VIPSIterativeExperiment)
    cw.add_logger(WandBLogger())
    cw.run()
