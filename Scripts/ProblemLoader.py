from ScheduleLib import *
import csv
import os


def load_problem_from_file(problem_name):

    problems_folder = 'Scheduling_Problems'
    directories = [x[0] for x in os.walk(problems_folder)][1:]

    for directory in directories:
        if directory == problems_folder + '/' + problem_name:

            # Staff
            with open(directory + '/' + 'Staff.csv', 'r') as file:

                csvreader = csv.reader(file)
                header = next(csvreader)

                staff_set = StaffSet()
                for row in csvreader:
                    if len(row) == 0:
                        continue
                    staff_set.add_person(Person(row[0],              # Name
                                              float(row[1]),        # Desired Workload
                                              row[2].split('|')))   # Qualification
                file.close()

            # Shifts
            with open(directory + '/' + 'Shifts.csv', 'r') as file:

                csvreader = csv.reader(file)
                header = next(csvreader)

                shift_set = ShiftSet()
                for row in csvreader:
                    if len(row) == 0:
                        continue

                    shift_set.add_shift(Shift(row[0],  # Type
                                              int(row[1]),  # Start Day
                                              int(row[2]),  # Start Hour
                                              int(row[3]),  # Duration
                                              float(row[4]),  # Burden
                                              row[5].split('|')))  # Qualification Requirements
                file.close()
                shift_set.set_shift_qualified_personnel(staff_set)

            # Overlap
            with open(directory + '/' + 'Overlap.csv', 'r') as file:

                csvreader = csv.reader(file)
                header = next(csvreader)

                overlap_set = OverlapSet(shift_set)
                for row in csvreader:
                    if len(row) == 0:
                        continue
                    overlap_set.add_allowed_personnel([int(elem) for elem in row[1].split('|')],
                                                      [int(elem) for elem in row[0].split('|')])
                file.close()

            # Constraints
            with open(directory + '/' + 'Constraints.csv', 'r') as file:

                csvreader = csv.reader(file)
                header = next(csvreader)

                constraints = list()
                for row in csvreader:
                    if len(row) == 0:
                        continue

                    constraint_type = int(row[0])

                    # Assignment of Shifts
                    if constraint_type == 0:
                        constraints.append({'Type': constraint_type,
                                            'Shift Indexes': [int(elem) for elem in row[1].split('|')],
                                            'Staff Indexes': [int(elem) for elem in row[2].split('|')],
                                            'x': int(row[3]),
                                            'y': int(row[4])})

                    # Qualified Assignments
                    if constraint_type == 1:
                        constraints.append({'Type': constraint_type,
                                            'Shift Indexes': [int(elem) for elem in row[1].split('|')],
                                            'Staff Indexes': [int(elem) for elem in row[2].split('|')],
                                            'x': int(row[3]),
                                            'y': int(row[4])})

                    # Overlapping Shifts
                    if constraint_type == 2:
                        constraints.append({'Type': constraint_type,
                                            'Staff Indexes': [int(elem) for elem in row[1].split('|')],
                                            'x': int(row[2]),
                                            'y': int(row[3])})

                    # Assignment Fractions
                    if constraint_type == 3:
                        constraints.append({'Type': constraint_type,
                                            'Staff Indexes': [int(elem) for elem in row[1].split('|')],
                                            'Shift Indexes': [int(elem) for elem in row[2].split('|')],
                                            'x': float(row[3]),
                                            'y': float(row[4])})

                    # Shift-to-Shift
                    if constraint_type == 4:
                        constraints.append({'Type': constraint_type,
                                            'Staff Indexes 1': [int(elem) for elem in row[1].split('|')],
                                            'Shift Indexes 1': [int(elem) for elem in row[2].split('|')],
                                            'Staff Indexes 2': [int(elem) for elem in row[3].split('|')],
                                            'Shift Indexes 2': [int(elem) for elem in row[4].split('|')],
                                            'x': int(row[5]),
                                            'y': int(row[6])})

                    # Consecutive Days
                    if constraint_type == 5:
                        constraints.append({'Type': constraint_type,
                                            'Staff Indexes': [int(elem) for elem in row[1].split('|')],
                                            'Shift Indexes': [int(elem) for elem in row[2].split('|')],
                                            'x': int(row[3]),
                                            'y': int(row[4])})

                    # Before and After Consecutive Days
                    if constraint_type == 6:
                        constraints.append({'Type': constraint_type,
                                            'Staff Indexes': [int(elem) for elem in row[1].split('|')],
                                            'Shift Indexes': [int(elem) for elem in row[2].split('|')],
                                            'x': int(row[3]),
                                            'y': int(row[4]),
                                            'n': int(row[5]),
                                            'Shift Indexes n': [int(elem) for elem in row[6].split('|')],
                                            'm': int(row[7]),
                                            'Shift Indexes m': [int(elem) for elem in row[8].split('|')]})

                    # Consecutive Shift Types
                    if constraint_type == 7:
                        constraints.append({'Type': constraint_type,
                                            'Staff Indexes': [int(elem) for elem in row[1].split('|')],
                                            'Shift Indexes': [int(elem) for elem in row[2].split('|')]})

                    # Fair Workload
                    if constraint_type == 8:
                        constraints.append({'Type': constraint_type,
                                            'Staff Indexes': [int(elem) for elem in row[1].split('|')],
                                            'Shift Indexes': [int(elem) for elem in row[2].split('|')],
                                            'x': float(row[3])})

                file.close()

    # Output problem
    problem = {'Shift Set': shift_set,
               'Staff Set': staff_set,
               'Overlap Set': overlap_set,
               'Constraints': constraints}
    return problem

