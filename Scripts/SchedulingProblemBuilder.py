from ScheduleLib import *
import csv
import os

# ###################### Add Parameters ######################
problems_folder = 'Scheduling_Problems'
problem_name = 'Problem_6'

# Staff
staff_set = StaffSet()
staff_set.add_person(Person('Alpha', 1, ['MD']))
staff_set.add_person(Person('Bravo', 1, ['MD']))
staff_set.add_person(Person('Charlie', 1, ['MD']))
staff_set.add_person(Person('Delta', 0.7, ['MD']))
staff_set.add_person(Person('Echo', 1, ['RN']))
staff_set.add_person(Person('Foxtrot', 1, ['RN']))
staff_set.add_person(Person('Golf', 0.5, ['RN']))
staff_set.add_person(Person('Hotel', 1, ['NA']))
staff_set.add_person(Person('India', 1, ['NA']))
staff_set.add_person(Person('Juliet', 1, ['NA']))
staff_set.add_person(Person('Kilo', 0.8, ['NA']))
staff_set.add_person(Person('Lima', 0.8, ['NA']))

# Shifts
shift_set = ShiftSet()
for day in range(30):
    shift_set.add_shift(Shift('Doctor Primary', day, 0, 24, 1, ['MD']))
    shift_set.add_shift(Shift('Doctor Secondary', day, 0, 24, 1, ['MD']))

    shift_set.add_shift(Shift('Nurse Primary', day, 0, 24, 1, ['RN']))
    shift_set.add_shift(Shift('Nurse Secondary', day, 0, 24, 1, ['RN']))

    shift_set.add_shift(Shift('Nurse Assistant Primary', day, 0, 24, 1, ['NA']))
    shift_set.add_shift(Shift('Nurse Assistant Secondary', day, 0, 24, 1, ['NA']))
    shift_set.add_shift(Shift('Nurse Assistant Tertiary', day, 0, 24, 1, ['NA']))

shift_set.set_shift_qualified_personnel(staff_set)


# Overlap
overlap_set = OverlapSet(shift_set)
#for i_day in shift_set.get_start_day_set():
    #overlap_set.add_allowed_personnel([i_day*5 + 2, i_day*5 + 4], list(range(len(staff_set))))

# -------------- Constraints --------------
constraints = list()

# Assignment of Shifts
constraints.append({'Type': 0,
                    'Shift Indexes': list(range(len(shift_set))),
                    'Staff Indexes': list(range(len(staff_set))),
                    'x': 0,
                    'y': 0})

# Qualified Assignments
constraints.append({'Type': 1,
                    'Shift Indexes': list(range(len(shift_set))),
                    'Staff Indexes': list(range(len(staff_set))),
                    'x': 0,
                    'y': 0})

"""
# Overlapping Shifts
constraints.append({'Type': 2,
                    'Staff Indexes': list(range(len(staff_set))),
                    'x': 0,
                    'y': 0})
"""

# Assignment Fractions
"""
constraints.append({'Type': 3,
                    'Staff Indexes': [0, 1, 2, 3],
                    'Shift Indexes': [7*day for day in shift_set.get_start_day_set()],
                    'x': 0.2,
                    'y': 1})
constraints.append({'Type': 3,
                    'Staff Indexes': [0],
                    'Shift Indexes': shift_set.get_shift_indexes_on_day(range(10, 16)),
                    'x': 0,
                    'y': 0})
constraints.append({'Type': 3,
                    'Staff Indexes': [10],
                    'Shift Indexes': shift_set.get_shift_indexes_on_day(range(17, 23)),
                    'x': 0,
                    'y': 0})
"""


"""
# Shift-to-Shift
constraints.append({'Type': 4,
                    'Staff Indexes 1': [0],
                    'Shift Indexes 1': [0, 2, 4, 6, 8, 10, 12, 14, 16, 18],
                    'Staff Indexes 2': [1],
                    'Shift Indexes 2': [0, 2, 4, 6, 8, 10, 12, 14, 16, 18],
                    'x': 2,
                    'y': 2})
"""

# Consecutive Days
constraints.append({'Type': 5,
                    'Staff Indexes': list(range(len(staff_set))),
                    'Shift Indexes': list(range(len(shift_set))),
                    'x': 3,
                    'y': 5})

# Before and After Consecutive Days
constraints.append({'Type': 6,
                    'Staff Indexes': list(range(len(staff_set))),
                    'Shift Indexes': list(range(len(shift_set))),
                    'x': 3,
                    'y': 5,
                    'n': 2,
                    'Shift Indexes n': list(range(len(shift_set))),
                    'm': 2,
                    'Shift Indexes m': list(range(len(shift_set)))})
constraints.append({'Type': 6,
                    'Staff Indexes': list(range(len(staff_set))),
                    'Shift Indexes': list(range(len(shift_set))),
                    'x': 6,
                    'y': 6,
                    'n': 3,
                    'Shift Indexes n': list(range(len(shift_set))),
                    'm': 3,
                    'Shift Indexes m': list(range(len(shift_set)))})


# Consecutive Shift Types
constraints.append({'Type': 7,
                    'Staff Indexes': list(range(len(staff_set))),
                    'Shift Indexes': list(range(len(shift_set)))})


# Fair Workload
constraints.append({'Type': 8,
                    'Staff Indexes': [0, 1, 2, 3],
                    'Shift Indexes': shift_set.get_shift_indexes_of_type(['Doctor Primary', 'Doctor Secondary']),
                    'x': 0.25})
constraints.append({'Type': 8,
                    'Staff Indexes': [4, 5, 6],
                    'Shift Indexes': shift_set.get_shift_indexes_of_type(['Nurse Primary', 'Nurse Secondary']),
                    'x': 0.5})
constraints.append({'Type': 8,
                    'Staff Indexes': [7, 8, 9, 10, 11],
                    'Shift Indexes': shift_set.get_shift_indexes_of_type(['Nurse Assistant Primary', 'Nurse Assistant Secondary', 'Nurse Assistant Tertiary']),
                    'x': 0.5})


# ###################### Write to file ######################
directories = [x[0] for x in os.walk(problems_folder)][1:]
folder_path = problems_folder + '/' + problem_name

# Make sure there are no problems with the same name, and add a new folder if all is ok
if any(folder_path == folder for folder in directories):
    pass
    #raise Exception('There is already a problem with the name {} in {}'.format(problem_name, problems_folder))
else:
    os.mkdir('./' + folder_path)

# Create staff file
with open(folder_path + '/' + 'Staff.csv', 'w', newline='') as file:
    csvwriter = csv.writer(file)
    csvwriter.writerow(['Name', 'Desired Workload', 'Qualifications'])

    for person in staff_set:
        csvwriter.writerow([person.name, person.desired_workload, '|'.join(person.qualifications)])

# Create shift file
with open(folder_path + '/' + 'Shifts.csv', 'w', newline='') as file:

    csvwriter = csv.writer(file)
    csvwriter.writerow(['Type','Start Day','Start Hour','Duration','Burden','Qualifications'])

    for shift in shift_set:
        csvwriter.writerow([shift.type,
                            shift.start_day,
                            shift.start_hour,
                            shift.duration,
                            shift.burden,
                            '|'.join(shift.qualification_requirements)])

# Create overlap file
with open(folder_path + '/' + 'Overlap.csv', 'w', newline='') as file:

    csvwriter = csv.writer(file)
    csvwriter.writerow(['Shift Indexes', 'Staff Indexes'])

    for overlap in overlap_set:
        if len(overlap.staff_indexes) != 0:
            csvwriter.writerow(['|'.join([str(elem) for elem in overlap.staff_indexes]),
                                '|'.join([str(elem) for elem in overlap.shift_indexes])])

# Create constraints file
with open(folder_path + '/' + 'Constraints.csv', 'w', newline='') as file:

    csvwriter = csv.writer(file)
    csvwriter.writerow(['All Constraints'])

    for constraint in constraints:
        row = list()
        for key in constraint.keys():
            if type(constraint[key]) is list:
                row.append('|'.join([str(elem) for elem in constraint[key]]))
            else:
                row.append(constraint[key])

        csvwriter.writerow([])
        csvwriter.writerow(row)
