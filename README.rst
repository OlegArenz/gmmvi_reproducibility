This repository contains scripts and config files that were used for running the experiments in the submission.
The primary motivation for this repository is to document the exact conditions under which the experiments have been
conducted, including hyperparameter search. The scripts for fetching the data can not be used without our
wandb-credentials, however, the fetched raw-data is stored within this repository.

Setting up the Python environment
=================================
You need to install the following python packages:

.. code-block:: console

    pip install gmmvi # from supplementary
    pip install tf-robot-learning # from supplementary, only needed for Talos experiments
    pip install cw2
    pip install wandb # You need to create an account at wandb.com, and provide your credentials afterwards (via `wandb login`)


Running the scripts
===================
The repository can be used to rerun the experiments, however, as the experiments were run on a cluster with
`Slurm <https://slurm.schedmd.com>`_ and the data was logged via `WandB <https://www.wandb.com>`_, the corresponding
config files / project ids need to be adapted.

Namely, the following files need to be adapted:

- `evaluations/clusterwork_slurm.sbatch <evaluations/clusterwork_slurm.sbatch>`_

- `hyperopt/wandb_sweep_slurm.sbatch-template <hyperopt/wandb_sweep_slurm.sbatch-template>`_

The slurm-configs use variables such as %%account%% to replace some parameters from the yml-files. However, when
hard-coding the correct values in the sbatch-files, it should not be necessary to modify the yml files.


Experiment Protocol
===================
In the following we describe for every experiment, which scripts have been run and refer to the relevant config files.

Experiment 1: Component Update Stability
----------------------------------------
The first experiment only compares the design choices related to the component updates (ComponentNgEstimation,
NgBasedComponentUpdater, ComponentStepsizeAdaptation) and evaluates all 18 combinations. Each combination was optimized
on the environments *BreastCancer* and *BreastCancerMB*. On *WINE* we did not evaluate zero-order gradient estimation,
which does not scale well to the higher dimensionality.

Running the Sweeps
~~~~~~~~~~~~~~~~~~
We used the Bayesian optimizer provided by WandB for hyperparameter optimization. The config files showing the
considered hyperparameters and their ranges (or prior distributions) can be found in

- `hyperopt/configs/experiments/exp1 (update stability for single gaussians)/breast_cancer <hyperopt/configs/experiments/exp1 (update stability for single gaussians)/breast_cancer>`_

- `hyperopt/configs/experiments/exp1 (update stability for single gaussians)/breast_cancer_mb <hyperopt/configs/experiments/exp1 (update stability for single gaussians)/breast_cancer_mb>`_

- `hyperopt/configs/experiments/exp1 (update stability for single gaussians)/wine <hyperopt/configs/experiments/exp1 (update stability for single gaussians)/wine>`_

The "command" section in these files also define the maximum time per worker ("--max_seconds").

The hyperparameter search was started by running the following batch-scripts:

- `hyperopt/run_exp1_bc.sh <hyperopt/run_exp1_bc.sh>`_

- `hyperopt/run_exp1_bcmb.sh <hyperopt/run_exp1_bcmb.sh>`_

- `hyperopt/run_exp1_wine.sh <hyperopt/run_exp1_wine.sh>`_

These scripts define $NUM_WORKERS and $CORES_PER_WORKER and execute for every config file the
`hyperopt/run_sweep.sh <hyperopt/run_sweep.sh>`_ script, which creates the wandb sweep and a temporary slurm-script
(based on a `template <hyperopt/wandb_sweep_slurm.sbatch-template>`_), and starts the corresponding slurm job.
Each job will start $NUM_WORKERS parallel workers that use `hyperopt/wandb_sweep.py <hyperopt/wandb_sweep.py>`_
to run a gmmvi optimization, whenever they are provided with new hyperparameters by WandB.

Evaluating the Sweeps
~~~~~~~~~~~~~~~~~~~~~
For evaluating the sweeps, we fetched the logged data from wandb by running
`hyperopt/fetch_exp1_sweeps.py <hyperopt/fetch_exp1_sweeps.py>`. This script created
the folders `hyperopt/results/exp1_bc <hyperopt/results/exp1_bc>`_,
`hyperopt/results/exp1_bcmb <hyperopt/results/exp1_bcmb>`_, and
`hyperopt/results/exp1_wine <hyperopt/results/exp1_wine>`_ and stored
the learning curves of the best runs, and the final performance for every run in csv-files in the corresponding folders.
The table for Experiment 1, was generated using the script `hyperopt/table_exp1.py <hyperopt/table_exp1.py>`_.

Running the 10-seed evaluations for SEPTRUX and SEPYRUX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The script `hyperopt/table_exp1.py <hyperopt/table_exp1.py>`_ also outputs the hyperparameters of the best runs,
which were used in the configs for the 10 seed evaluations for SEPTRUX and SEPYRUX, which can be found in
`evaluations/configs/exp1 (update stability)/ <evaluations/configs/exp1 (update stability)/>`_.
These evaluations were started by running
`evaluations/run_exp1_evals.sh <evaluations/run_exp1_evals.sh>`_. The results of the 10-seed evaluations were fetched
from wandb using `evaluations/fetch_exp1.py <evaluations/fetch_exp1.py>`, which outputs the data for the second table of
Experiment 1.

Experiment 2: Weight Update and Exploration
-------------------------------------------
Hyperoptimization for the second experiment was performed akin to the hyperoptimization for the Experiment 1.

1. The config files that specify the hyperparameter-ranges can be found in
   `hyperopt/configs/experiments/exp2 (multimodal targets) <hyperopt/configs/experiments/exp2 (multimodal targets)>`_.

2. The sweeps and workers were started by executing `hyperopt/run_exp2_gmm20.sh <hyperopt/run_exp2_gmm20.sh>`_,
   `hyperopt/run_exp2_planar4.sh <hyperopt/run_exp2_planar4.sh>`_,
   and `hyperopt/run_exp2_stm20.sh <hyperopt/run_exp2_stm20.sh>`_.

3. The logged data was fetched from WandB and saved to `hyperopt/results <hyperopt/results>`_ by running
   `hyperopt/fetch_exp2.py <hyperopt/fetch_exp2.py>`_.

4. The values for the Table for Experiment 2 were computed by running
   `hyperopt/table_exp2.py <hyperopt/table_exp2.py>`_.


Experiment 3: Evaluating the Promising Candidates
-------------------------------------------------

Hyperparameter Search
~~~~~~~~~~~~~~~~~~~~~

For the main experiment, we performed little hyperparameter search based on manually defined grids, were we used our
experience from the previous experiments to select promising hyperparameters. Originally, we planned to test exactly
24 different parameter-settings for every candidate. However, we had to deviate from this procedure for several reasons:

1. For SEPYFUX and SEPYRUX we usually required several iterations of hyperparameter search to obtain reasonable
   parameters.

2. In our original evaluations on the planar robot experiment, SAMTRON performed signifcantly worse compared to
   SAMTRUX and SAMTROX in terms of the MMD, although it achieved a similar ELBO. We found that the reason for this
   discrepency was only based on chance during the hyperparameter search. During our first hyperparameter search
   SAMTRON achieved slightly better ELBO when starting with only 10 initial components, whereas SAMTRUX and SAMTROX
   achieved best ELBO when starting with 300 components. To avoid misleading conclusions, we reran the hyperparameter
   search, where we only considered larger numbers for the initial number of components. Still, as mentioned in the
   paper, the hyperparameters are in general not optimized with respect to the secondary metrics.

3. We had to rerun the GermanCreditMB experiments because we originally forgot to log the secondary metric (MMD). We
   also made minor adjustments to hyperparameters, putting more focus on the stepsize for the component update for most
   algorithms.

4. We also had to restart several hyperparameter searches due to typos.

The previously tried configs can be found under
`evaluations/configs/exp3 (hyperopt)/previously_tried_grids <evaluations/configs/exp3 (hyperopt)/previously_tried_grids>`_
The 24 parameter-settings that were eventually used the select the best settings for the 10-seed evaluations can be
found in `evaluations/configs/exp3 (hyperopt) <evaluations/configs/exp3 (hyperopt)>`_. We stress that the additional
evaluations mainly benefited SEPYFUX and SEPYRUX (which still perform worst among the tested candidates overall).
The experiments were started using the run_exp3_<environment>.sh scripts that can be found in
`evaluations <evaluations>`_.

10-Seed Evaluations
~~~~~~~~~~~~~~~~~~~
The results of the hyperparameter search were fetched from WandB using
`evaluations/fetch_exp3.py <evaluations/fetch_exp3.py>` and stored under `evaluations/results <evaluations/results>`.
This script also prints the hyperparameters for the best run (with respect to final ELBO). These hyperparameters were
used for the configs in `evaluations/configs/exp3 (eval) <evaluations/configs/exp3 (eval)>` which were used for the
10-seed evaluations. The 10-seed evaluations were started by running the run_exp3_<environment>_eval.sh scripts that
can be found in `evaluations <evaluations>`_. We ran into "out of memory"-errors for ZAMTRUX on STM300 and PlanarRobot4,
and for SAMYRUX on STM300. For ZAMTRUX, the higher memory requirements stem from the fact that it requires significantly
more samples due to zero-order optimization. For SAMYRUX the OOM-errors seem to be somewhat coincidentally caused by
the chosen hyperparameters. We decided to rerun these experiments with larger number of cores (which translates to
more memory), using the scripts `evaluations/run_exp3_p4_eval_zamtrux.sh <evaluations/run_exp3_p4_eval_zamtrux.sh>`_,
`evaluations/run_exp3_stm300_eval_samyrux.sh <evaluations/run_exp3_stm300_eval_samyrux.sh>`_, and
`evaluations/run_exp3_wine_eval_zamtrux.sh <evaluations/run_exp3_wine_eval_zamtrux.sh>`_.

The results were fetched from WandB using the script `evaluations/fetch_exp3.py <evaluations/fetch_exp3.py>`_.
This script also creates the Latex-code for the table for experiment 3. Despite the additional hyperparameter search,
the optimization for SEPYFUX and SEPYRUX was sometimes unstable leading to outliers with very high ELBOs. We decided
to exclude the corresponding seeds for computing the values / latex-code for the table. The affected seeds
can be found in `evaluations/fetch_exp3.py <evaluations/fetch_exp3.py>`_,  where they are passed as "bad_run_ids" to
the fetch_exp3_eval()-call.  The following experiments were affected:

- SEPYFUX on Planar Robot: 5 bad seeds
- SEPRUX on Planar Robot: 3 bad seeds
- SEPYFUX on TALOS: 5 bad seeds
- SEPYRUX on TALOS: 6 bad seeds
- We also ignored two seeds for ZAMTRUX on Planar Robot, as the corresponding runs terminated early due to OOM.