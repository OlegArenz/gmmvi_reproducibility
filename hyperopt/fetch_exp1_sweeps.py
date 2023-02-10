from sweep_fetching import fetch_sweeps

fetch_sweeps(group_name="joa", project_names=["exp1_bc", "exp1_bcmb", "exp1_wine"],
             sweep_names=["zepyrux", "zepyfux", "zepydux",
                          "zeptrux", "zeptfux", "zeptdux",
                          "zepirux", "zepifux", "zepidux",
                          "sepyrux", "sepyfux", "sepydux",
                          "septrux", "septfux", "septdux",
                          "sepirux", "sepifux", "sepidux"])
