
<br>
<h1 align="center">A Comparative Study of SMT and MILP for the Nurse Rostering Problem</h1>
<br>

<p align="center">
  Alvin Combrink, Stephie Do, Kristofer Bengtsson, Sabino Franceso Roselli, and Martin Fabian.
</p>
<br>
<div align="center">
  <p>
    <img src="https://github.com/user-attachments/assets/08b2f059-6b73-4a3b-a322-4146851ae218" width="28%" hspace="10">
    <img src="https://github.com/user-attachments/assets/8d19102a-8988-4481-a4d1-c55ef58716df" width="28%" hspace="10">
    <img src="https://github.com/user-attachments/assets/f06158fb-586f-4185-a6c1-4772e9618384" width="28%" hspace="10">
  </p>
</div>
<br>

This is the official repository for the article **A Comparative Study of SMT and MILP for the Nurse Rostering Problem** accepted to [CoDIT25](https://www.codit2025.org/). This repository contains
- the Python source code for generating instances and comparing the respective SMT and MILP solvers Z3 and Gurobi,
- additional descriptions, use-examples, and the full formulations of the generic constraints (GC1-GC9) for SMT and MILP,
- and additional details regarding the experimental evaluation together with supplementary results.

<br>

## Abstract
_The effects of personnel scheduling on the quality of care and working conditions for healthcare personnel have been thoroughly documented. However, the ever-present demand and large variation of constraints make healthcare scheduling particularly challenging. This problem has been studied for decades, with limited research aimed at applying Satisfiability Modulo Theories (SMT). SMT has gained momentum within the formal verification community in the last decades, leading to the advancement of SMT solvers that have been shown to outperform standard mathematical programming techniques._

_In this work, we propose generic constraint formulations that can model a wide range of real-world scheduling constraints. Then, the generic constraints are formulated as SMT and MILP problems and used to compare the respective state-of-the-art solvers, Z3 and Gurobi, on academic and real-world inspired rostering problems. Experimental results show how each solver excels for certain types of problems; the MILP solver generally performs better when the problem is highly constrained or infeasible, while the SMT solver performs better otherwise. On real-world inspired problems containing a more varied set of shifts and personnel, the SMT solver excelled. Additionally, it was noted during experimentation that the SMT solver was more sensitive to the way generic constraint were formulated, requiring careful consideration and experimentation to achieve better performance. We conclude that SMT-based methods present a promising avenue for future research within the domain of personnel scheduling._


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


