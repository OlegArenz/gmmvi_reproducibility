from fetch_from_wandb import process_sweep


if __name__ == "__main__":

    process_sweep(group_name="joa", project_names=["exp2_gmm20"],
                  sweep_names=["septrun", "septron", "septrux", "septrox", "septrug", "septrog",
                               "semtrun", "semtron", "semtrux", "semtrox", "semtrug", "semtrog",
                               "saptrun", "saptron", "saptrux", "saptrox", "saptrug", "saptrog",
                               "samtrun", "samtron", "samtrux", "samtrox", "samtrug", "samtrog"
                               ])
    print("done")
