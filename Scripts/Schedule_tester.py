from matplotlib import pyplot as plt
from matplotlib import cm
import seaborn as sns
import pandas as pd
import numpy as np
from time import time

import importlib
import sys
import os
from datetime import datetime
import csv

import SchedulerSMT
import SchedulerMILP
import SchedulePlotter
import HeatmapLib


sys.path.insert(0, './Scheduling_Problems')


def test_solvers(problem_name, nr_staff, day_input, time_out, method_1_label, method_2_label):

    problem = importlib.import_module(problem_name).get_problem(nr_staff, day_input)

    if method_1_label == 'SMTint':
        solution1 = SchedulerSMT.scheduler_smt(problem, time_out)
    elif method_1_label == 'SMTintMulticore':
        solution1 = SchedulerSMT.scheduler_smt_multicore(problem, time_out)
    elif method_1_label == 'SMTbool':
        solution1 = SchedulerSMT.scheduler_smt_boolmat(problem, time_out)
    elif method_1_label == 'SMTboolMulticore':
        solution1 = SchedulerSMT.scheduler_smt_boolmat_multicore(problem, time_out)
    elif method_1_label == 'MILPbin':
        solution1 = SchedulerMILP.scheduler_milp_binmat(problem, time_out)

    if method_2_label == 'SMTint':
        solution2 = SchedulerSMT.scheduler_smt(problem, time_out)
    elif method_2_label == 'SMTintMulticore':
        solution2 = SchedulerSMT.scheduler_smt_multicore(problem, time_out)
    elif method_2_label == 'SMTbool':
        solution2 = SchedulerSMT.scheduler_smt_boolmat(problem, time_out)
    elif method_2_label == 'SMTboolMulticore':
        solution2 = SchedulerSMT.scheduler_smt_boolmat_multicore(problem, time_out)
    elif method_2_label == 'MILPbin':
        solution2 = SchedulerMILP.scheduler_milp_binmat(problem, time_out)

    # solution1 = solution2

    plot_schedules = False
    if plot_schedules:

        if solution1['Satisfied'] is True:
            print('{}:  Build {:.4f} s\t\tSolver {:.4f} s'.format(
                method_1_label,
                solution1['Build Time'],
                solution1['Solve Time']))
        else:
            print('{}:  {}'.format(method_1_label, solution1['Satisfied']))

        if solution2['Satisfied'] is True:
            print('{}: Build {:.4f} s\t\tSolver {:.4f} s \t\t{:+.1f} % solve time'.format(
                method_2_label,
                solution2['Build Time'],
                solution2['Solve Time'],
                100*(solution2['Solve Time'] / solution1['Solve Time'] - 1)))
        else:
            print('{}: {}'.format(method_2_label, solution2['Satisfied']))

        if solution1['Satisfied'] is True:
            SchedulePlotter.plot_schedule(problem, solution1)
        if solution2['Satisfied'] is True:
            SchedulePlotter.plot_schedule(problem, solution2)

    return solution1, solution2, problem


problem_names = ['Test_Problem_A']
for problem_name in problem_names:

    # Parameters
    time_out = 60*60*1     # seconds
    nr_samples = 1
    shift_inputs = list(range(50, 301, 10))  # [20, 39, 59, 78, 98, 117, 137, 156, 176, 195, 215, 234, 254, 273, 293, 312, 332]
    staff_inputs = list(range(10, 41, 3))  # [28]

    method1_label = 'MILPbin'
    method2_label = 'SMTboolMulticore'

    # Initiate variables
    calculation_start_time = time()
    input_params = [(staff_input, day_input) for staff_input in staff_inputs for day_input in shift_inputs]
    write_data = dict()
    write_data['Input_Staff'] = list()
    write_data['Input_Shifts'] = list()
    for i_sample in range(nr_samples):
        write_data['{}_sat_{}'.format(method1_label, i_sample)] = list()
        write_data['{}_build_{}'.format(method1_label, i_sample)] = list()
        write_data['{}_solve_{}'.format(method1_label, i_sample)] = list()
        write_data['{}_sat_{}'.format(method2_label, i_sample)] = list()
        write_data['{}_build_{}'.format(method2_label, i_sample)] = list()
        write_data['{}_solve_{}'.format(method2_label, i_sample)] = list()

    # "Warm up" Gurobi (avoids increased time for first solve)
    problem = importlib.import_module(problem_name).get_problem(staff_inputs[0], shift_inputs[0])
    solution = SchedulerMILP.scheduler_milp_binmat(problem, time_out)
    print('Pre-test smallest instance status: {}'.format(solution['Satisfied']))

    # Solve Benchmark Instances
    for input_param in input_params:

        write_data['Input_Staff'].append(input_param[0])
        write_data['Input_Shifts'].append(input_param[1])

        for i_sample in range(nr_samples):

            # Solve and Print
            print('\n---- {} ----'.format(problem_name))
            print('\t Sample: {}/{}\t\tStaff param: {}\t\tShift param: {}'.format(i_sample + 1, nr_samples, input_param[0], input_param[1]))

            solution1, solution2, problem = test_solvers(problem_name, input_param[0], input_param[1], time_out, method1_label, method2_label)

            print('\t {}: {}\t\t {}: {}'.format(method1_label, solution1['Solve Time'],
                                                method2_label, solution2['Solve Time']))

            # Save Data
            write_data['{}_sat_{}'.format(method1_label, i_sample)].append(solution1['Satisfied'])
            write_data['{}_build_{}'.format(method1_label, i_sample)].append(solution1['Build Time'])
            write_data['{}_solve_{}'.format(method1_label, i_sample)].append(solution1['Solve Time'])
            write_data['{}_sat_{}'.format(method2_label, i_sample)].append(solution2['Satisfied'])
            write_data['{}_build_{}'.format(method2_label, i_sample)].append(solution2['Build Time'])
            write_data['{}_solve_{}'.format(method2_label, i_sample)].append(solution2['Solve Time'])

    # Get average times, proportional times, rankings and sat/unsat/timeout status
    method1_avg_times = [sum(write_data['{}_solve_{}'.format(method1_label, i_sample)][i_input] for i_sample in range(nr_samples)) / nr_samples for i_input, _ in enumerate(input_params)]
    method2_avg_times = [sum(write_data['{}_solve_{}'.format(method2_label, i_sample)][i_input] for i_sample in range(nr_samples)) / nr_samples for i_input, _ in enumerate(input_params)]
    proportional_time = [np.log10(method1_avg_times[i_input] / method2_avg_times[i_input]) for i_input, _ in enumerate(input_params)]

    method1_status = list()
    method2_status = list()
    for i_input, _ in enumerate(input_params):
        if any(write_data['{}_sat_{}'.format(method1_label, i_sample)][i_input] == 'Timed_Out' for i_sample in range(nr_samples)):
            method1_status.append('Timed_Out')
        else:
            method1_status.append(all(write_data['{}_sat_{}'.format(method1_label, i_sample)][i_input] for i_sample in range(nr_samples)))
        if any(write_data['{}_sat_{}'.format(method2_label, i_sample)][i_input] == 'Timed_Out' for i_sample in range(nr_samples)):
            method2_status.append('Timed_Out')
        else:
            method2_status.append(all(write_data['{}_sat_{}'.format(method2_label, i_sample)][i_input] for i_sample in range(nr_samples)))

    discrete_ranking = list()
    for i_input, _ in enumerate(input_params):
        if method1_status[i_input] == 'Timed_Out' and method2_status[i_input] == 'Timed_Out':
            discrete_ranking.append(None)
        elif method1_status[i_input] == 'Timed_Out':
            discrete_ranking.append(1)
        elif method2_status[i_input] == 'Timed_Out':
            discrete_ranking.append(-1)
        elif 0.95 <= method1_avg_times[i_input]/method2_avg_times[i_input] <= 1.05:
            discrete_ranking.append(0)
        elif method1_avg_times[i_input] < method2_avg_times[i_input]:
            discrete_ranking.append(-1)
        else:
            discrete_ranking.append(1)

    # Add extra data to write_data
    write_data[method1_label + '_avg'] = method1_avg_times
    write_data[method2_label + '_avg'] = method2_avg_times
    write_data[method1_label + '_status'] = method1_status
    write_data[method2_label + '_status'] = method2_status
    write_data['Proportional_time'] = proportional_time
    write_data['Ranking'] = discrete_ranking

    # Save Data File
    dt_string = datetime.now().strftime("%Y:%m:%d_%H.%M.%S")
    folder_name = 'Tests/' + dt_string + '__' + problem_name + '__' + method1_label + '_' + method2_label
    os.mkdir('./' + folder_name)
    with open(folder_name + '/' + 'data.csv', 'w', newline='') as file:
        csvwriter = csv.writer(file)
        csvwriter.writerow(list(write_data.keys()))
        for i_row in range(len(input_params)):
            row = [write_data[key][i_row] for key in list(write_data.keys())]
            csvwriter.writerow(row)
    with open(folder_name + '/' + 'parameters.csv', 'w', newline='') as file:

        calculation_time = time() - calculation_start_time
        calculation_time_hours = int(np.floor(calculation_time / 3600))
        calculation_time_minutes = int(np.floor((calculation_time - 3600*calculation_time_hours) / 60))
        calculation_time_seconds = int(calculation_time - 3600*calculation_time_hours - 60*calculation_time_minutes)

        csvwriter = csv.writer(file)
        csvwriter.writerow(['Time Out', 'Nr Samples', 'Method 1', 'Method 2', 'Total Time'])
        csvwriter.writerow([
            time_out,
            nr_samples,
            method1_label,
            method2_label,
            '{} h {} m {} s'.format(calculation_time_hours, calculation_time_minutes, calculation_time_seconds)
        ])

    # Save Heatmaps
    HeatmapLib.comparison_heatmap(folder_name + '/' + 'COMPARISON',
                       write_data['Input_Staff'],
                       write_data['Input_Shifts'],
                       proportional_time,
                       method1_status,
                       method2_status,
                       'Number of Staff Members', 'Number of Shifts', 'Log of {} / {}\nPositive value: {} faster'.format(method1_label, method2_label, method2_label))

    HeatmapLib.ranking_heatmap(folder_name + '/' + 'RANKING',
                    write_data['Input_Staff'],
                    write_data['Input_Shifts'],
                    discrete_ranking,
                    method1_status,
                    method2_status,
                    'Number of Staff Members', 'Number of Shifts',
                    ['{} faster'.format(method1_label), 'Equal (5%)', '{} faster'.format(method2_label)])

    HeatmapLib.time_heatmap(folder_name + '/' + '{}_TIME'.format(method1_label),
                 write_data['Input_Staff'],
                 write_data['Input_Shifts'],
                 method1_avg_times,
                 method1_status,
                 'Number of Staff Members', 'Number of Shifts')
    HeatmapLib.time_heatmap(folder_name + '/' + '{}_TIME'.format(method2_label),
                 write_data['Input_Staff'],
                 write_data['Input_Shifts'],
                 method2_avg_times,
                 method2_status,
                 'Number of Staff Members', 'Number of Shifts')