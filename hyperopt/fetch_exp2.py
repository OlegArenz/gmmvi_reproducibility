from sweep_fetching import fetch_sweeps

if __name__ == "__main__":
    fetch_sweeps(group_name="joa", project_names=["exp2_stm"],
                  sweep_names=["septrun", "septron", "septrux", "septrox", "septrug", "septrog",
                               "semtrun", "semtron", "semtrux", "semtrox", "semtrug", "semtrog",
                               "saptrun", "saptron", "saptrux", "saptrox", "saptrug", "saptrog",
                               "samtrun", "samtron", "samtrux", "samtrox", "samtrug", "samtrog"
                               ])

    fetch_sweeps(group_name="joa", project_names=["exp2_gmm"],
                  sweep_names=["septrun", "septron", "septrux", "septrox", "septrug", "septrog",
                               "semtrun", "semtron", "semtrux", "semtrox", "semtrug", "semtrog",
                               "saptrun", "saptron", "saptrux", "saptrox", "saptrug", "saptrog",
                               "samtrun", "samtron", "samtrux", "samtrox", "samtrug", "samtrog"
                               ])
    print("done")
