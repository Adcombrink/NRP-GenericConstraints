# HealthcareScheduling-GenericConstraints-SMT-MILP

This repository contains the implementation and additional details of 
_**A Comparative Study of SMT and MILP for the Nurse Rostering Problem**_ 
by Alvin Combrink, Stephie Do, Kristofer Bengtsson, Sabino Franceso Roselli, and Martin Fabian.



## Features

- **Generic Constraints**: A set of constraint formulations capable of modeling diverse scheduling requirements found in healthcare environments.
- **SMT and MILP Implementations**: Comparative implementations using state-of-the-art solvers:
    - SMT Solver: Z3
    - MILP Solver: Gurobi
- **Experimental Evaluation**: Benchmarks comparing solver performance on both synthetic and real-world-inspired scheduling problems.



## Repository Structure

```
├── src/                         # Source code for the project
│   ├── Results/                 # Results from solver runs
│   ├── Scheduling_Problems      # Problem instance generators
│   ├── Plots/                   # Result plots
├── docs/
│   ├── AppendixFormulations.pdf # Appendix: Details on the SMT and MILP generic constraint formulations.
│   ├── AppendixExperiment.pdf   # Appendix: Details on the experimental evaluation.
├── README.md                    # Project documentation (this file)
├── LICENSE                      # License information
└── requirements.txt             # Required Python libraries and dependencies
```



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



## License

This project is licensed under the MIT License. See `LICENSE` for details.


