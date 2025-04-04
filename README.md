
<br>
<h1 align="center">A Comparative Study of SMT and MILP for the Nurse Rostering Problem</h1>
<br>

<p align="center">
  Alvin Combrink, Stephie Do, Kristofer Bengtsson, Sabino Franceso Roselli, and Martin Fabian.
</p>
<br>
<br>

This is the official repository for the article **A Comparative Study of SMT and MILP for the Nurse Rostering Problem** to be submitted to [CoDIT25](https://www.codit2025.org/). This repository contains
- the Python source code for generating instances and comparing the respective SMT and MILP solvers Z3 and Gurobi,
- additional descriptions, use-examples, and the full formulations of the generic constraints (GC1-GC9) using SMT and MILP,
- and additional details regarding the experimental evaluation together with supplementary results.
<br>

## Repository Structure

```
├── src/                           # Source code for the project
│   ├── Results/                   # Results from solver runs
│   ├── Scheduling_Problems/       # Problem instance generators
│   ├── Plots/                     # Result plots
│   ├── requirements.txt           # Required Python libraries and dependencies
├── docs/
│   ├── AppendixFormulations.pdf   # Appendix: Details on the SMT and MILP generic constraint formulations.
│   ├── AppendixExperiments.pdf    # Appendix: Details on the experimental evaluation.
├── README.md                      # Project documentation (this file)
└── LICENSE                        # License information
```


<br>

## Getting Started

### Prerequisites

1. **Python** (version 3.8 or higher)
2. Install required dependencies using:

```bash
pip install -r requirements.txt
```

3. Solvers:
    - [Z3 SMT Solver](https://github.com/Z3Prover/z3)
    - [Gurobi Optimizer](https://www.gurobi.com)

### Running the Code

Scheduler_tester.py - loads and runs a specified problem set on both the SMT and MILP solvers.
HeatmapPlotter.py - loads the results as heatmaps. 


<br>

## License

This project is licensed under the MIT License. See `LICENSE` for details.


