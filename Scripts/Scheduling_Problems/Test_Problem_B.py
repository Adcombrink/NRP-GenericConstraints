from ScheduleLib import *
import math


def get_problem(staff_input, shift_input):

    # ########## Staff ###########
    staff_set = StaffSet()
    staff_set.add_person(Person('Nurse1, N, CN', 1, ['N', 'CN']))
    staff_set.add_person(Person('Nurse2, N, CN', 1, ['N', 'CN']))
    staff_set.add_person(Person('Nurse3, N, CN', 1, ['N', 'CN']))
    staff_set.add_person(Person('Nurse4, A', 1, ['N', 'A']))
    staff_set.add_person(Person('Nurse5', 1, ['N']))
    staff_set.add_person(Person('Nurse6', 1, ['N']))
    staff_set.add_person(Person('Nurse7', 1, ['N']))
    staff_set.add_person(Person('Nurse8', 1, ['N']))
    staff_set.add_person(Person('Nurse9', 1, ['N']))
    staff_set.add_person(Person('Nurse10', 1, ['N']))
    staff_set.add_person(Person('Nurse11', 1, ['N']))
    staff_set.add_person(Person('Nurse12', 1, ['N']))
    staff_set.add_person(Person('Nurse13', 1, ['N']))
    staff_set.add_person(Person('Nurse14', 1, ['N']))
    staff_set.add_person(Person('Nurse15', 0.75, ['N']))
    staff_set.add_person(Person('Nurse16', 0.5, ['N']))
    staff_set.add_person(Person('Nurse17', 0.5, ['N']))
    staff_set.add_person(Person('Doctor1, Sp1, Sp2', 1, ['D', 'Sp1', 'Sp2']))
    staff_set.add_person(Person('Doctor2, Sp1', 1, ['D', 'Sp1']))
    staff_set.add_person(Person('Doctor3, Sp1', 1, ['D', 'Sp1']))
    staff_set.add_person(Person('Doctor4, Sp2', 1, ['D', 'Sp2']))
    staff_set.add_person(Person('Doctor5, Sp2', 1, ['D', 'Sp2']))
    staff_set.add_person(Person('Doctor6, Sp2', 0.75, ['D', 'Sp2']))
    staff_set.add_person(Person('Doctor7', 1, ['D']))
    staff_set.add_person(Person('Doctor8', 1, ['D']))
    staff_set.add_person(Person('Doctor9', 1, ['D']))
    staff_set.add_person(Person('Doctor10', 0.5, ['D']))
    staff_set.add_person(Person('Admin1', 1, ['A']))

    """
    staff_pool = [('Adam', 1, ['CN', 'N']),
                  ('Bertil', 1, ['N', 'A']),
                  ('Caesar', 1, ['N']),
                  ('David', 1, ['N']),
                  ('Erik', 1, ['N']),
                  ('Filip', 1, ['D', 'Sp1', 'Sp2']),
                  ('Gustav', 1, ['D', 'Sp1']),
                  ('Helge', 1, ['D', 'Sp2']),
                  # ('Ivar', 1, ['D']),
                  ('Johan', 1, ['D']),
                  ('Kalle', 1, ['A']),
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
    """

    # ########### Shifts ###########
    shift_set = ShiftSet()
    shift_pool = [('Nurse D 1', 6, 9, 1, ['N']),
                  ('Nurse D 2', 6, 9, 1, ['N']),
                  ('Nurse D 3', 6, 9, 1, ['N']),
                  ('Nurse D 4', 6, 9, 1, ['N']),
                  ('Nurse D 5', 6, 9, 1, ['N']),

                  ('Nurse E 1', 14, 9, 1, ['N']),
                  ('Nurse E 2', 14, 9, 1, ['N']),
                  ('Nurse E 3', 14, 9, 1, ['N']),
                  ('Nurse E 4', 14, 9, 1, ['N']),

                  ('Nurse N 1', 22, 9, 0.777, ['N']),
                  ('Nurse N 2', 22, 9, 0.777, ['N']),

                  ('Doctor D 1', 6, 10, 1, ['D']),
                  ('Doctor D 2', 6, 10, 1, ['D']),
                  ('Doctor E 1', 12, 10, 1, ['D']),
                  ('Doctor N 1', 19, 9, 0.777, ['D']),

                  ('Doctor S 1', 5, 9, 1, ['D', 'Sp1']),
                  ('Doctor S 2', 5, 9, 1, ['D', 'Sp2']),

                  ('C.Nurse D', 6, 10, 1, ['CN']),
                  ('C.Nurse E', 16, 8, 1, ['CN'])]

    shift_pool_place = 0
    day = 0
    while len(shift_set) < shift_input:

        if shift_pool_place == len(shift_pool):
            shift_pool_place = 0

            if day % 2 == 0:
                shift_set.add_shift(Shift('Admin', day, 8, 5, 1, ['A']))
                day += 1
                continue
            day += 1

        shift_params = shift_pool[shift_pool_place]
        shift_set.add_shift(Shift(shift_params[0],
                                  day,
                                  shift_params[1],
                                  shift_params[2],
                                  shift_params[3],
                                  shift_params[4]
                                  )
                            )
        shift_pool_place += 1
    """
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
    """
    shift_set.set_shift_qualified_personnel(staff_set)

    # ########### Overlap ###########
    overlap_set = OverlapSet(shift_set)
    for i_day in shift_set.get_start_day_set():

        shifts_on_i_day = shift_set.get_shift_indexes_on_day(i_day)

        # C.Nurse Day + Nurse Day
        shift_c_nurse_d_indexes = set(shift_set.get_shift_indexes_of_type('C.Nurse D')).intersection(shifts_on_i_day)
        shift_nurse_d_indexes = set(shift_set.get_shift_indexes_of_type(
            ['Nurse D 1', 'Nurse D 2', 'Nurse D 3', 'Nurse D 4', 'Nurse D 5'])).intersection(shifts_on_i_day)
        for shift_c_nurse_d in shift_c_nurse_d_indexes:
            for shift_nurse_d in shift_nurse_d_indexes:
                overlap_set.add_allowed_personnel([shift_c_nurse_d, shift_nurse_d], staff_set.get_all_person_indexes())

        # C.Nurse Day + Admin
        shift_admin_indexes = set(shift_set.get_shift_indexes_of_type('Admin')).intersection(shifts_on_i_day)
        for shift_c_nurse_d in shift_c_nurse_d_indexes:
            for shift_admin in shift_admin_indexes:
                overlap_set.add_allowed_personnel([shift_c_nurse_d, shift_admin], staff_set.get_all_person_indexes())

        # C.Nurse Evening + Nurse Evening
        shift_c_nurse_e_indexes = set(shift_set.get_shift_indexes_of_type('C.Nurse E')).intersection(shifts_on_i_day)
        shift_nurse_e_indexes = set(shift_set.get_shift_indexes_of_type(
            ['Nurse E 1', 'Nurse E 2', 'Nurse E 3', 'Nurse E 4'])).intersection(shifts_on_i_day)
        for shift_c_nurse_e in shift_c_nurse_e_indexes:
            for shift_nurse_e in shift_nurse_e_indexes:
                overlap_set.add_allowed_personnel([shift_c_nurse_e, shift_nurse_e], staff_set.get_all_person_indexes())

        # Doctor Day + Doctor Spec
        shift_doctor_d_indexes = set(shift_set.get_shift_indexes_of_type(['Doctor D 1', 'Doctor D 2'])).intersection(shifts_on_i_day)
        shift_doctor_spec_indexes = set(shift_set.get_shift_indexes_of_type(['Doctor S 1', 'Doctor S 2'])).intersection(shifts_on_i_day)
        for shift_doctor_d in shift_doctor_d_indexes:
            for shift_doctor_spec in shift_doctor_spec_indexes:
                overlap_set.add_allowed_personnel([shift_doctor_d, shift_doctor_spec], staff_set.get_all_person_indexes())

    # ########### Constraints ###########
    constraints = list()

    # Assignment of Shifts
    constraints.append({'Type': 0,      # All shifts assigned someone
                        'Shift Indexes': list(range(len(shift_set))),
                        'Staff Indexes': list(range(len(staff_set))),
                        'x': 0,
                        'y': 0})

    # Qualified Assignments
    constraints.append({'Type': 1,      # All shifts assigned qualified staff
                        'Shift Indexes': list(range(len(shift_set))),
                        'Staff Indexes': list(range(len(staff_set))),
                        'x': 0,
                        'y': 0})

    # Overlapping Shifts
    constraints.append({'Type': 2,      # No unallowed overlapping shifts
                        'Staff Indexes': list(range(len(staff_set))),
                        'x': 0,
                        'y': 0})

    # Assignment Fractions
    constraints.append({'Type': 3,      # Between 10-100 % of 0's shifts should be Charge Nurse
                        'Staff Indexes': [0],
                        'Shift Indexes': shift_set.get_shift_indexes_of_type(['C.Nurse D', 'C.Nurse E']),
                        'x': 0.1,
                        'y': 1})

    # Shift-to-Shift
    for i_day in shift_set.get_start_day_set():

        shifts_on_day = set(shift_set.get_shift_indexes_on_day(i_day))
        shifts_on_next_day = set(shift_set.get_shift_indexes_on_day(i_day + 1))
        shifts_on_prev_day = set(shift_set.get_shift_indexes_on_day(i_day - 1))

        # Doctor D, Doctor S --X--> Doctor N
        shift_group_1 = set(shift_set.get_shift_indexes_of_type(['Doctor D 1', 'Doctor D 2', 'Doctor S 1', 'Doctor S 2'])).intersection(shifts_on_day)
        shift_group_2 = set(shift_set.get_shift_indexes_of_type('Doctor N 1')).intersection(shifts_on_day)
        constraints += [{'Type': 4,
                         'Staff Indexes 1': [i_person],
                         'Shift Indexes 1': shift_group_1,
                         'Staff Indexes 2': [i_person],
                         'Shift Indexes 2': shift_group_2,
                         'x': 0,
                         'y': 0}
                        for i_person in staff_set.get_all_person_indexes()]

        # Nurse D, C.Nurse D --X--> Nurse N, C.Nurse E
        shift_group_1 = set(shift_set.get_shift_indexes_of_type(['Nurse D 1', 'Nurse D 2', 'Nurse D 3', 'Nurse D 4', 'Nurse D 5', 'C.Nurse D'])).intersection(shifts_on_day)
        shift_group_2 = set(shift_set.get_shift_indexes_of_type(['Nurse N 1', 'Nurse N 2', 'C.Nurse E'],)).intersection(shifts_on_day)
        constraints += [{'Type': 4,
                         'Staff Indexes 1': [i_person],
                         'Shift Indexes 1': shift_group_1,
                         'Staff Indexes 2': [i_person],
                         'Shift Indexes 2': shift_group_2,
                         'x': 0,
                         'y': 0}
                        for i_person in staff_set.get_all_person_indexes()]

        # Admin --X--> Nurse E, Nurse N, C.Nurse E, Doctor N 1, Nurse E (-1), Nurse N (-1), C.Nurse E (-1), Doctor N 1 (-1)
        shift_group_1 = set(shift_set.get_shift_indexes_of_type(['Admin'])).intersection(shifts_on_day)
        shift_group_2 = set(shift_set.get_shift_indexes_of_type(['Nurse E 1', 'Nurse E 2', 'Nurse E 3', 'Nurse E 4', 'Nurse N 1', 'Nurse N 2', 'C.Nurse E', 'Doctor N 1'])).intersection(shifts_on_day)
        shift_group_2 = shift_group_2 | set(shift_set.get_shift_indexes_of_type(['Nurse E 1', 'Nurse E 2', 'Nurse E 3', 'Nurse E 4', 'Nurse N 1', 'Nurse N 2', 'C.Nurse E', 'Doctor N 1'])).intersection(shifts_on_prev_day)
        constraints += [{'Type': 4,
                         'Staff Indexes 1': [i_person],
                         'Shift Indexes 1': shift_group_1,
                         'Staff Indexes 2': [i_person],
                         'Shift Indexes 2': shift_group_2,
                         'x': 0,
                         'y': 0}
                        for i_person in staff_set.get_all_person_indexes()]

    # Consecutive Days
    constraints.append({'Type': 5,  # Min 1 and max 6 days of work in a row
                        'Staff Indexes': list(range(len(staff_set))),
                        'Shift Indexes': list(range(len(shift_set))),
                        'x': 1,
                        'y': 6})
    constraints.append({'Type': 5,  # Max 3 days of night shifts in a row
                        'Staff Indexes': list(range(len(staff_set))),
                        'Shift Indexes': shift_set.get_shift_indexes_of_type(['Nurse E 1', 'Nurse E 2', 'Nurse E 3', 'Nurse E 4',
                                                                              'Nurse N 1', 'Nurse N 2',
                                                                              'C.Nurse E',
                                                                              'Doctor E 1',
                                                                              'Doctor N 1']),
                        'x': 1,
                        'y': 3})

    # Before and After Consecutive Days
    constraints.append({'Type': 6,  # Free for 2 days before and after 3-5 consecutive days of working
                        'Staff Indexes': list(range(len(staff_set))),
                        'Shift Indexes': list(range(len(shift_set))),
                        'x': 3,
                        'y': 5,
                        'n': 2,
                        'Shift Indexes n': list(range(len(shift_set))),
                        'm': 2,
                        'Shift Indexes m': list(range(len(shift_set)))})
    constraints.append({'Type': 6,  # Free for 3 days before and after 6 consecutive days of working
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
                        'Staff Indexes': staff_set.get_all_person_indexes(),
                        'Shift Indexes': set(shift_set.get_all_shift_indexes()).difference(shift_set.get_shift_indexes_of_type('Admin'))
                        })

    # Fair Workload
    constraints.append({'Type': 8,  # Even for all nurses wrt all nurse shifts
                        'Staff Indexes': staff_set.get_staff_indexes_with_qualifications('N'),
                        'Shift Indexes': shift_set.get_shift_indexes_of_type(['Nurse D 1',
                                                                              'Nurse D 2',
                                                                              'Nurse D 3',
                                                                              'Nurse D 4',
                                                                              'Nurse D 5',
                                                                              'Nurse E 1',
                                                                              'Nurse E 2',
                                                                              'Nurse E 3',
                                                                              'Nurse E 4',
                                                                              'Nurse N 1',
                                                                              'Nurse N 2',
                                                                              'C.Nurse D',
                                                                              'C.Nurse E']),
                        'x': 0.6})
    constraints.append({'Type': 8,  # Even for all doctors wrt all doctor shifts
                        'Staff Indexes': staff_set.get_staff_indexes_with_qualifications(['D']),
                        'Shift Indexes': shift_set.get_shift_indexes_of_type(['Doctor D 1',
                                                                              'Doctor D 2',
                                                                              'Doctor E 1',
                                                                              'Doctor N 1',
                                                                              'Doctor S 1',
                                                                              'Doctor S 2']),
                        'x': 0.6})

    # Output problem
    problem = {'Shift Set': shift_set,
               'Staff Set': staff_set,
               'Overlap Set': overlap_set,
               'Constraints': constraints}

    return problem

