import HeatmapLib
import csv
import os


# Parameters
data_folder = 'Tests'
folder_names = ['2022/04/16_16.55.40__Test_Problem_A__MILPbin_SMTboolMulticore',
                '2022/04/13_19.43.18__Test_Problem_A__MILPbin_SMTboolMulticore']
output_folder = 'Heatmaps2025'

# Collect data
directories = [x[0] for x in os.walk(data_folder)][1:]
data = dict()
for folder_name in folder_names:

    folder_path = data_folder + '/' + folder_name.replace('/', ':')
    folder_data = dict()

    if folder_path in directories:
        with open(folder_path + '/' + 'data.csv', 'r') as file:
            csvreader = csv.reader(file)
            rows = [row for row in csvreader]

        input_staff_index = 0
        input_shift_index = 1
        method1_avg_index = len(rows[0]) - 6
        method2_avg_index = len(rows[0]) - 5
        method1_status_index = len(rows[0]) - 4
        method2_status_index = len(rows[0]) - 3
        proportional_index = len(rows[0]) - 2
        ranking_index = len(rows[0]) - 1

        folder_data['Input_staff'] = [int(row[input_staff_index]) for row in rows[1:]]
        folder_data['Input_shifts'] = [int(row[input_shift_index]) for row in rows[1:]]
        folder_data['method1_name'] = rows[0][method1_avg_index][0:-4]
        folder_data['method2_name'] = rows[0][method2_avg_index][0:-4]
        folder_data['method1_avg_times'] = [float(row[method1_avg_index]) for row in rows[1:]]
        folder_data['method2_avg_times'] = [float(row[method2_avg_index]) for row in rows[1:]]
        folder_data['proportional_times'] = [float(row[proportional_index]) for row in rows[1:]]

        # Convert status to bool if true or false, if timed_out leave as str
        folder_data['method1_status'] = list()
        folder_data['method2_status'] = list()
        folder_data['rankings'] = list() #[int(row[ranking_index]) for row in rows[1:]]
        for row in rows[1:]:

            # Method 1 status
            if row[method1_status_index] == 'True':
                folder_data['method1_status'].append(True)
            elif row[method1_status_index] == 'False':
                folder_data['method1_status'].append(False)
            else:
                folder_data['method1_status'].append(row[method1_status_index])

            # Method 2 status
            if row[method2_status_index] == 'True':
                folder_data['method2_status'].append(True)
            elif row[method2_status_index] == 'False':
                folder_data['method2_status'].append(False)
            else:
                folder_data['method2_status'].append(row[method2_status_index])

            # Ranking
            try:
                folder_data['rankings'].append(int(row[ranking_index]))
            except:
                folder_data['rankings'].append(None)

    else:
        raise Exception('Folder {} not in Tests-folder'.format(folder_name))

    data[folder_name] = folder_data

# Calculate min/max for comparison plot
scale_min = None
scale_max = None
proportional_scale = [None, None]
times_scale = [None, None]
for key in data:

    for i_time, time in enumerate(data[key]['proportional_times']):
        if data[key]['method1_status'][i_time] is True and data[key]['method2_status'][i_time] is True:
            if proportional_scale[0] is None or proportional_scale[0] > time:
                proportional_scale[0] = time
            if proportional_scale[1] is None or proportional_scale[1] < time:
                proportional_scale[1] = time

    for i_time, time in enumerate(data[key]['method1_avg_times']):
        if data[key]['method1_status'][i_time] is True:
            if times_scale[0] is None or times_scale[0] > time:
                times_scale[0] = time
            if times_scale[1] is None or times_scale[1] < time:
                times_scale[1] = time

    for i_time, time in enumerate(data[key]['method2_avg_times']):
        if data[key]['method2_status'][i_time] is True:
            if times_scale[0] is None or times_scale[0] > time:
                times_scale[0] = time
            if times_scale[1] is None or times_scale[1] < time:
                times_scale[1] = time

# Plot
for key in data:

    HeatmapLib.comparison_heatmap(output_folder + '/' + key.replace('/', ':') + '_Comparison',
                                  data[key]['Input_staff'],
                                  data[key]['Input_shifts'],
                                  data[key]['proportional_times'],
                                  data[key]['method1_status'],
                                  data[key]['method2_status'],
                                  'Number of Staff Members',
                                  'Number of Shifts',
                                  '$Log_{10}$ ( Gurobi solve time $/$ Z3 solve time )\n Positive values: Z3 faster',
                                  vminmax=proportional_scale)

    HeatmapLib.ranking_heatmap(output_folder + '/' + key.replace('/', ':') + '_Ranking',
                                  data[key]['Input_staff'],
                                  data[key]['Input_shifts'],
                                  data[key]['rankings'],
                                  data[key]['method1_status'],
                                  data[key]['method2_status'],
                                  'Number of Staff Members',
                                  'Number of Shifts',
                                  ['Gurobi\nFaster', 'Equal\n(5%)', 'Z3\nFaster']
                                  )


    HeatmapLib.time_heatmap(output_folder + '/' + key.replace('/', ':') + '_MILP',
                            data[key]['Input_staff'],
                            data[key]['Input_shifts'],
                            data[key]['method1_avg_times'],
                            data[key]['method1_status'],
                            'Number of Staff Members', 'Number of Shifts',
                            vminmax=times_scale)
    HeatmapLib.time_heatmap(output_folder + '/' + key.replace('/', ':') + '_SMT',
                            data[key]['Input_staff'],
                            data[key]['Input_shifts'],
                            data[key]['method2_avg_times'],
                            data[key]['method2_status'],
                            'Number of Staff Members', 'Number of Shifts',
                            vminmax=times_scale)