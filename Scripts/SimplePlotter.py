import matplotlib.pyplot as plt

MILP_times = [0.01796412468, 0.2973899841, 0.6379168034, 2.186705828, 5.802005053, 9.793164015, 69.00687194, 476.6156170, 605.397619, 2815.904601, None, None, None, None, None, None, None]
SMT_times = [0.01853609, 0.09453607, 0.14457703, 0.21942019, 0.55433702, 2.70451093, 10.71365714, 28.26616096, 133.51425314, 1048.88218212, 354.47363877, 1261.77726483, 2936.16145396, 1849.66065407, 9614.34002829, 4347.58145308, None]

days = range(1,18)

fig, ax = plt.subplots(figsize=(5.1, 4))
plt.plot(days, SMT_times, '-o', color=(204/255, 227/255, 0/255), label='Z3')
plt.plot(days, MILP_times, '-o', color=(0/255, 107/255, 145/255), label='Gurobi')

plt.yscale('log', base=10)
plt.xlim((0,18))
plt.grid()
plt.hlines(y=60*60*5, xmin=0, xmax=18, colors='black', linestyles='--', lw=1, label='Time Limit (5 h)')
plt.legend(loc='lower right')
plt.xlabel('Number of Days')
plt.ylabel('\n Solve Time [s]')

plt.savefig('SMT_MILP_ProblemB' + '.png', dpi=600)
plt.show()