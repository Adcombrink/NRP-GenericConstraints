from ScheduleLib import *
import math


def get_problem(staff_input, shift_input):

    # ########## Staff ###########
    staff_set = StaffSet()
    staff_pool = [('Adam', 1, ['A', 'N']),
                  ('Bertil', 1, ['N']),
                  ('Caesar', 1, ['N']),
                  ('David', 0.5, ['N']),
                  ]
    for i in range(math.floor(staff_input / len(staff_pool))):
        for j, person_params in enumerate(staff_pool):
            staff_set.add_person(Person(person_params[0] + '_{}'.format(i),
                                        person_params[1],
                                        person_params[2]))
    for j in range(staff_input % len(staff_pool)):
        staff_set.add_person(Person(staff_pool[j][0] + '_{}'.format(math.floor(staff_input / len(staff_pool))),
                                    staff_pool[j][1],
                                    staff_pool[j][2]))

    # ########### Shifts ###########
    shift_set = ShiftSet()
    shift_pool = [('Nurse D 1', 6, 9, 1, ['A', 'N']),
                  ('Nurse D 2', 6, 9, 1, ['N']),
                  ('Nurse E 1', 14, 9, 1, ['N']),
                  ('Nurse E 2', 14, 9, 1, ['N']),
                  ('Nurse N 1', 22, 9, 1, ['N']),
                  ('Nurse N 2', 22, 9, 1, ['N'])
                  ]
    for i in range(math.floor(shift_input / len(shift_pool))):
        for j, shift_params in enumerate(shift_pool):
            shift_set.add_shift(Shift(shift_params[0],
                                      i,
                                      shift_params[1],
                                      shift_params[2],
                                      shift_params[3],
                                      shift_params[4])
                                )
    for j in range(shift_input % len(shift_pool)):
        shift_set.add_shift(Shift(shift_pool[j][0],
                                  math.floor(shift_input / len(shift_pool)),
                                  shift_pool[j][1],
                                  shift_pool[j][2],
                                  shift_pool[j][3],
                                  shift_pool[j][4])
                            )
    shift_set.set_shift_qualified_personnel(staff_set)

    # ########### Overlap ###########
    overlap_set = OverlapSet(shift_set)
    # No overlapping
    # for i_day in shift_set.get_start_day_set():
    #    if len(shift_set.get_shift_indexes_on_day(i_day)) > 2:
    #        overlap_set.add_allowed_personnel([i_day*len(shift_pool), i_day*len(shift_pool)+2],
    #                                          list(range(len(staff_set))))

    # ########### Constraints ###########
    constraints = list()

    # Assignment of Shifts
    constraints.append({'Type': 0,
                        'Shift Indexes': list(range(len(shift_set))),
                        'Staff Indexes': list(range(len(staff_set))),
                        'x': 0,
                        'y': 0})

    constraints.append({'Type': 0,  # Person 0 is not supposed to work any shifts  starting on days 2 - 4
                        'Shift Indexes': shift_set.get_shift_indexes_on_day([2, 3, 4]),
                        'Staff Indexes': [0],
                        'x': len(shift_set.get_shift_indexes_on_day([2, 3, 4])),
                        'y': len(shift_set.get_shift_indexes_on_day([2, 3, 4]))})

    # Qualified Assignments
    constraints.append({'Type': 1,
                        'Shift Indexes': list(range(len(shift_set))),
                        'Staff Indexes': list(range(len(staff_set))),
                        'x': 0,
                        'y': 0})

    # Overlapping Shifts
    constraints.append({'Type': 2,
                        'Staff Indexes': list(range(len(staff_set))),
                        'x': 0,
                        'y': 0})

    # Assignment Fractions
    constraints.append({'Type': 3,  # 50-100 % of person 0 shifts should be of type Nurse D 1
                        'Staff Indexes': [0],
                        'Shift Indexes': shift_set.get_shift_indexes_of_type(['Nurse D 1', 'Nurse D 2']),
                        'x': 0.5,
                        'y': 1})

    # Shift-to-Shift
    constraints.append({'Type': 4,  # If person 0 works any shifts on days 0-1, persons 3 and 4 not allowed to work then
                        'Staff Indexes 1': [0],
                        'Shift Indexes 1': shift_set.get_shift_indexes_on_day([0, 1]),
                        'Staff Indexes 2': [3, 4],
                        'Shift Indexes 2': shift_set.get_shift_indexes_on_day([0, 1]),
                        'x': 0,
                        'y': 0})
    for i_person, _ in enumerate(staff_set):

        shifts_nurse_day = shift_set.get_shift_indexes_of_type(['Nurse D 1', 'Nurse D 2'])
        shifts_nurse_night = shift_set.get_shift_indexes_of_type(['Nurse N 1', 'Nurse N 2'])
        for i_day in shift_set.get_start_day_set():
            shifts_on_day = shift_set.get_shift_indexes_on_day(i_day)
            shifts_on_day_nurse_day = set(shifts_nurse_day).intersection(shifts_on_day)
            shifts_on_day_nurse_night = set(shifts_nurse_night).intersection(shifts_on_day)

            if len(shifts_on_day_nurse_day) > 0 and len(shifts_on_day_nurse_night) > 0:
                constraints.append({'Type': 4,
                                    'Staff Indexes 1': [i_person],
                                    'Shift Indexes 1': shifts_on_day_nurse_day,
                                    'Staff Indexes 2': [i_person],
                                    'Shift Indexes 2': shifts_on_day_nurse_night,
                                    'x': 0,
                                    'y': 0})

    # Consecutive Days
    constraints.append({'Type': 5,
                        'Staff Indexes': list(range(len(staff_set))),
                        'Shift Indexes': list(range(len(shift_set))),
                        'x': 0,
                        'y': 6})

    # Before and After Consecutive Days
    constraints.append({'Type': 6,
                        'Staff Indexes': list(range(len(staff_set))),
                        'Shift Indexes': list(range(len(shift_set))),
                        'x': 4,
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
                        'Staff Indexes': list(range(len(staff_set))),
                        'Shift Indexes': list(range(len(shift_set))),
                        'x': 0.3})

    # Output problem
    problem = {'Shift Set': shift_set,
               'Staff Set': staff_set,
               'Overlap Set': overlap_set,
               'Constraints': constraints}

    return problem

