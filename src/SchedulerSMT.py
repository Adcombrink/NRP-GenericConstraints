from z3 import *
from time import time


def scheduler_smt(problem, time_out):

    shift_set = problem['Shift Set']
    staff_set = problem['Staff Set']
    overlap_set = problem['Overlap Set']
    scheduling_constraints = problem['Constraints']

    time_build_start = time()

    # ################ INIT SOLVER ################
    solver = Solver()
    solver.set("timeout", time_out * 1000)  # In Milliseconds

    # ################ DECISION VARS ################
    assignments = [Int('s_{}'.format(i_shift)) for i_shift in range(len(shift_set))]

    # ################ DOMAIN CONDITIONS ################
    # "-1" represents no one being assigned
    constraint_domain = [-1 <= assignments[i_shift] for i_shift in range(len(shift_set))] + \
                        [assignments[i_shift] <= len(shift_set)-1 for i_shift in range(len(shift_set))]

    # ################ SCHEDULING CONSTRAINTS ################
    constraint_scheduling = list()
    for constraint in scheduling_constraints:

        # Assignment of Shifts
        if constraint['Type'] == 0:
            num_unassigned_shifts = Sum([
             If(
                 And([
                     Not(assignments[i_shift] == i_person)
                     for i_person in constraint['Staff Indexes']
                 ]),
                 1,
                 0
             )
             for i_shift in constraint['Shift Indexes']
            ])
            constraint_scheduling += [constraint['x'] <= num_unassigned_shifts,
                                      num_unassigned_shifts <= constraint['y']]

        # Qualified Assignments
        if constraint['Type'] == 1:
            num_shifts_assigned_unqualified = Sum([
                If(
                    Or([assignments[i_shift] == i_person
                        for i_person in set(constraint['Staff Indexes']).difference(
                            set(shift_set.get_shifts(i_shift).qualified_staff)
                        )
                        ]),
                    1,
                    0
                )
                for i_shift in constraint['Shift Indexes']
            ])
            constraint_scheduling += [constraint['x'] <= num_shifts_assigned_unqualified,
                                      num_shifts_assigned_unqualified <= constraint['y']]

        # Overlapping Shifts
        if constraint['Type'] == 2:
            num_times_staff_assigned_unallowed_overlapping = Sum([
                If(
                    And([
                        assignments[i_shift] == i_person
                        for i_shift in overlap.shift_indexes
                    ]),
                    1,
                    0
                )
                for overlap in overlap_set
                for i_person in set(constraint['Staff Indexes']).difference(set(overlap.staff_indexes))
            ])
            constraint_scheduling += [
                constraint['x'] <= num_times_staff_assigned_unallowed_overlapping,
                num_times_staff_assigned_unallowed_overlapping <= constraint['y']
            ]

        # Assignment Fractions
        if constraint['Type'] == 3:
            for i_person in constraint['Staff Indexes']:

                wl_certain_shifts = Sum([
                    If(assignments[i_shift] == i_person,
                       shift_set.get_shifts(i_shift).workload,
                       0)
                    for i_shift in constraint['Shift Indexes']
                ])
                wl_all_shifts_x = Sum([
                    If(assignments[i_shift] == i_person,
                       shift_set.get_shifts(i_shift).workload * constraint['x'],
                       0)
                    for i_shift in range(len(shift_set))
                ])
                wl_all_shifts_y = Sum([
                    If(assignments[i_shift] == i_person,
                       shift_set.get_shifts(i_shift).workload * constraint['y'],
                       0)
                    for i_shift in range(len(shift_set))
                ])

                constraint_scheduling += [wl_all_shifts_x <= wl_certain_shifts]
                constraint_scheduling += [wl_certain_shifts <= wl_all_shifts_y]

        # Shift-to-Shift
        if constraint['Type'] == 4:

            num_assigned = Sum([
                If(assignments[i_shift] == i_person,
                   1,
                   0)
                for i_person in constraint['Staff Indexes 2']
                for i_shift in constraint['Shift Indexes 2']
            ])

            constraint_scheduling += [Implies(
                Or([assignments[i_shift] == i_person
                    for i_person in constraint['Staff Indexes 1']
                    for i_shift in constraint['Shift Indexes 1']
                ]),
                And(constraint['x'] <= num_assigned,
                    num_assigned <= constraint['y'])
            )]

        # Consecutive Days
        if constraint['Type'] == 5:

            for i_person in constraint['Staff Indexes']:
                for i_shift in constraint['Shift Indexes']:

                    # Limit on shortest consecutive days
                    constraint_scheduling += [
                        Implies(
                            And(
                                assignments[i_shift] == i_person,
                                And([ Not(assignments[j_shift] == i_person)
                                    for j_shift in shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                ])
                            ),
                            And([
                                Or([assignments[j_shift] == i_person
                                    for j_shift in shift_set.get_shift_indexes_on_day(k, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                ])
                                for k in range(1, constraint['x'])
                            ])
                        )
                    ]

                    # Limit on longest consecutive days
                    constraint_scheduling += [
                        Implies(
                            And(
                                assignments[i_shift] == i_person,
                                And([Not(assignments[j_shift] == i_person)
                                     for j_shift in shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                     ])
                            ),
                            Or([
                                And([Not(assignments[j_shift] == i_person)
                                    for j_shift in shift_set.get_shift_indexes_on_day(k, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                    ])
                                for k in range(1, constraint['y']+1)
                            ])
                        )
                    ]

        # Before and After Consecutive Days
        if constraint['Type'] == 6:
            for c in range(constraint['x'], constraint['y']+1):
                for d in shift_set.get_start_day_set():
                    for i_person in constraint['Staff Indexes']:

                        constraint_scheduling += [
                            Implies(
                                And(
                                    And([
                                        Or([assignments[i_shift] == i_person
                                            for i_shift in
                                            shift_set.get_shift_indexes_on_day(c_tilde, intersection_set=constraint['Shift Indexes'])])
                                        for c_tilde in range(d, d+c)
                                    ]),
                                    And([Not(assignments[i_shift] == i_person)
                                        for i_shift in
                                        set(shift_set.get_shift_indexes_on_day(d-1, intersection_set=constraint['Shift Indexes'])).union(
                                            set(shift_set.get_shift_indexes_on_day(d+c, intersection_set=constraint['Shift Indexes'])))
                                    ])
                                ),
                                And(
                                    And([Not(assignments[i_shift] == i_person)
                                        for n_tilde in range(d-constraint['n'], d)
                                        for i_shift in shift_set.get_shift_indexes_on_day(n_tilde, intersection_set=constraint['Shift Indexes n'])
                                    ]),
                                    And([Not(assignments[i_shift] == i_person)
                                        for m_tilde in range(d+c, d+c+constraint['m'])
                                        for i_shift in shift_set.get_shift_indexes_on_day(m_tilde, intersection_set=constraint['Shift Indexes m'])
                                    ])
                                )
                            )
                        ]

        # Consecutive Shift Types
        if constraint['Type'] == 7:
            for i_shift in constraint['Shift Indexes']:
                for i_person in constraint['Staff Indexes']:

                    constraint_scheduling += [
                        Implies(
                            assignments[i_shift] == i_person,
                            Or(
                                Or([assignments[j_shift] == i_person
                                    for j_shift in
                                    set(shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])).intersection(
                                        set(shift_set.get_shift_indexes_of_type(shift_set.get_shifts(i_shift))))
                                ]),
                                And([Not(assignments[j_shift] == i_person)
                                    for j_shift in
                                    shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                ])
                            )
                        )
                    ]

        # Fair Workload
        if constraint['Type'] == 8:

            r_e = sum([shift_set.get_shifts(i_shift).workload for i_shift in constraint['Shift Indexes']]) /\
                  sum([staff_set.get_person(i_person).desired_workload for i_person in constraint['Staff Indexes']])
            temp_lb = r_e * (1 - constraint['x'])
            temp_ub = r_e * (1 + constraint['x'])

            for i_person in constraint['Staff Indexes']:
                r = sum([
                    If(
                        assignments[i_shift] == i_person,
                        shift_set.get_shifts(i_shift).workload / staff_set.get_person(i_person).desired_workload,
                        0
                    )
                    for i_shift in constraint['Shift Indexes']
                ])

                constraint_scheduling += [
                    temp_lb <= r,
                    temp_ub >= r
                ]

    # ################ ADD CONSTRAINTS TO MODEL ################
    solver.add(constraint_domain + constraint_scheduling)
    time_build = time() - time_build_start

    # ################ SOLVE ################
    time_solve_start = time()
    satisfied = solver.check()
    time_solve = time() - time_solve_start

    # Output
    output = dict()
    output['Total Time'] = time_build + time_solve
    output['Build Time'] = time_build
    output['Solve Time'] = time_solve

    if satisfied == unknown:
        output['Satisfied'] = 'Timed_Out'

    elif satisfied == sat:
        output['Satisfied'] = True
        output['Assignments'] = [solver.model()[assignments[i_shift]].as_long() for i_shift in range(len(shift_set))]
    else:
        output['Satisfied'] = False

    return output


def scheduler_smt_multicore(problem, time_out):

    shift_set = problem['Shift Set']
    staff_set = problem['Staff Set']
    overlap_set = problem['Overlap Set']
    scheduling_constraints = problem['Constraints']

    time_build_start = time()

    # ################ INIT SOLVER ################
    solver = Solver()
    solver.set("timeout", time_out * 1000)  # In Milliseconds
    set_param('parallel.enable', True)

    # ################ DECISION VARS ################
    assignments = [Int('s_{}'.format(i_shift)) for i_shift in range(len(shift_set))]

    # ################ DOMAIN CONDITIONS ################
    # "-1" represents no one being assigned
    constraint_domain = [-1 <= assignments[i_shift] for i_shift in range(len(shift_set))] + \
                        [assignments[i_shift] <= len(shift_set)-1 for i_shift in range(len(shift_set))]

    # ################ SCHEDULING CONSTRAINTS ################
    constraint_scheduling = list()
    for constraint in scheduling_constraints:

        # Assignment of Shifts
        if constraint['Type'] == 0:
            num_unassigned_shifts = Sum([
             If(
                 And([
                     Not(assignments[i_shift] == i_person)
                     for i_person in constraint['Staff Indexes']
                 ]),
                 1,
                 0
             )
             for i_shift in constraint['Shift Indexes']
            ])
            constraint_scheduling += [constraint['x'] <= num_unassigned_shifts,
                                      num_unassigned_shifts <= constraint['y']]

        # Qualified Assignments
        if constraint['Type'] == 1:
            num_shifts_assigned_unqualified = Sum([
                If(
                    Or([assignments[i_shift] == i_person
                        for i_person in set(constraint['Staff Indexes']).difference(
                            set(shift_set.get_shifts(i_shift).qualified_staff)
                        )
                        ]),
                    1,
                    0
                )
                for i_shift in constraint['Shift Indexes']
            ])
            constraint_scheduling += [constraint['x'] <= num_shifts_assigned_unqualified,
                                      num_shifts_assigned_unqualified <= constraint['y']]

        # Overlapping Shifts
        if constraint['Type'] == 2:
            num_times_staff_assigned_unallowed_overlapping = Sum([
                If(
                    And([
                        assignments[i_shift] == i_person
                        for i_shift in overlap.shift_indexes
                    ]),
                    1,
                    0
                )
                for overlap in overlap_set
                for i_person in set(constraint['Staff Indexes']).difference(set(overlap.staff_indexes))
            ])
            constraint_scheduling += [
                constraint['x'] <= num_times_staff_assigned_unallowed_overlapping,
                num_times_staff_assigned_unallowed_overlapping <= constraint['y']
            ]

        # Assignment Fractions
        if constraint['Type'] == 3:
            for i_person in constraint['Staff Indexes']:

                wl_certain_shifts = Sum([
                    If(assignments[i_shift] == i_person,
                       shift_set.get_shifts(i_shift).workload,
                       0)
                    for i_shift in constraint['Shift Indexes']
                ])
                wl_all_shifts_x = Sum([
                    If(assignments[i_shift] == i_person,
                       shift_set.get_shifts(i_shift).workload * constraint['x'],
                       0)
                    for i_shift in range(len(shift_set))
                ])
                wl_all_shifts_y = Sum([
                    If(assignments[i_shift] == i_person,
                       shift_set.get_shifts(i_shift).workload * constraint['y'],
                       0)
                    for i_shift in range(len(shift_set))
                ])

                constraint_scheduling += [wl_all_shifts_x <= wl_certain_shifts]
                constraint_scheduling += [wl_certain_shifts <= wl_all_shifts_y]

        # Shift-to-Shift
        if constraint['Type'] == 4:

            num_assigned = Sum([
                If(assignments[i_shift] == i_person,
                   1,
                   0)
                for i_person in constraint['Staff Indexes 2']
                for i_shift in constraint['Shift Indexes 2']
            ])

            constraint_scheduling += [Implies(
                Or([assignments[i_shift] == i_person
                    for i_person in constraint['Staff Indexes 1']
                    for i_shift in constraint['Shift Indexes 1']
                ]),
                And(constraint['x'] <= num_assigned,
                    num_assigned <= constraint['y'])
            )]

        # Consecutive Days
        if constraint['Type'] == 5:

            for i_person in constraint['Staff Indexes']:
                for i_shift in constraint['Shift Indexes']:

                    # Limit on shortest consecutive days
                    constraint_scheduling += [
                        Implies(
                            And(
                                assignments[i_shift] == i_person,
                                And([ Not(assignments[j_shift] == i_person)
                                    for j_shift in shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                ])
                            ),
                            And([
                                Or([assignments[j_shift] == i_person
                                    for j_shift in shift_set.get_shift_indexes_on_day(k, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                ])
                                for k in range(1, constraint['x'])
                            ])
                        )
                    ]

                    # Limit on longest consecutive days
                    constraint_scheduling += [
                        Implies(
                            And(
                                assignments[i_shift] == i_person,
                                And([Not(assignments[j_shift] == i_person)
                                     for j_shift in shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                     ])
                            ),
                            Or([
                                And([Not(assignments[j_shift] == i_person)
                                    for j_shift in shift_set.get_shift_indexes_on_day(k, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                    ])
                                for k in range(1, constraint['y']+1)
                            ])
                        )
                    ]

        # Before and After Consecutive Days
        if constraint['Type'] == 6:
            for c in range(constraint['x'], constraint['y']+1):
                for d in shift_set.get_start_day_set():
                    for i_person in constraint['Staff Indexes']:

                        constraint_scheduling += [
                            Implies(
                                And(
                                    And([
                                        Or([assignments[i_shift] == i_person
                                            for i_shift in
                                            shift_set.get_shift_indexes_on_day(c_tilde, intersection_set=constraint['Shift Indexes'])])
                                        for c_tilde in range(d, d+c)
                                    ]),
                                    And([Not(assignments[i_shift] == i_person)
                                        for i_shift in
                                        set(shift_set.get_shift_indexes_on_day(d-1, intersection_set=constraint['Shift Indexes'])).union(
                                            set(shift_set.get_shift_indexes_on_day(d+c, intersection_set=constraint['Shift Indexes'])))
                                    ])
                                ),
                                And(
                                    And([Not(assignments[i_shift] == i_person)
                                        for n_tilde in range(d-constraint['n'], d)
                                        for i_shift in shift_set.get_shift_indexes_on_day(n_tilde, intersection_set=constraint['Shift Indexes n'])
                                    ]),
                                    And([Not(assignments[i_shift] == i_person)
                                        for m_tilde in range(d+c, d+c+constraint['m'])
                                        for i_shift in shift_set.get_shift_indexes_on_day(m_tilde, intersection_set=constraint['Shift Indexes m'])
                                    ])
                                )
                            )
                        ]

        # Consecutive Shift Types
        if constraint['Type'] == 7:
            for i_shift in constraint['Shift Indexes']:
                for i_person in constraint['Staff Indexes']:

                    constraint_scheduling += [
                        Implies(
                            assignments[i_shift] == i_person,
                            Or(
                                Or([assignments[j_shift] == i_person
                                    for j_shift in
                                    set(shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])).intersection(
                                        set(shift_set.get_shift_indexes_of_type(shift_set.get_shifts(i_shift))))
                                ]),
                                And([Not(assignments[j_shift] == i_person)
                                    for j_shift in
                                    shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                ])
                            )
                        )
                    ]

        # Fair Workload
        if constraint['Type'] == 8:

            r_e = sum([shift_set.get_shifts(i_shift).workload for i_shift in constraint['Shift Indexes']]) /\
                  sum([staff_set.get_person(i_person).desired_workload for i_person in constraint['Staff Indexes']])
            temp_lb = r_e * (1 - constraint['x'])
            temp_ub = r_e * (1 + constraint['x'])

            for i_person in constraint['Staff Indexes']:
                r = sum([
                    If(
                        assignments[i_shift] == i_person,
                        shift_set.get_shifts(i_shift).workload / staff_set.get_person(i_person).desired_workload,
                        0
                    )
                    for i_shift in constraint['Shift Indexes']
                ])

                constraint_scheduling += [
                    temp_lb <= r,
                    temp_ub >= r
                ]

    # ################ ADD CONSTRAINTS TO MODEL ################
    solver.add(constraint_domain + constraint_scheduling)
    time_build = time() - time_build_start

    # ################ SOLVE ################
    time_solve_start = time()
    satisfied = solver.check()
    time_solve = time() - time_solve_start

    # Output
    output = dict()
    output['Total Time'] = time_build + time_solve
    output['Build Time'] = time_build
    output['Solve Time'] = time_solve

    if satisfied == unknown:
        output['Satisfied'] = 'Timed_Out'

    elif satisfied == sat:
        output['Satisfied'] = True
        output['Assignments'] = [solver.model()[assignments[i_shift]].as_long() for i_shift in range(len(shift_set))]
    else:
        output['Satisfied'] = False

    return output


def scheduler_smt_boolmat(problem, time_out):

    shift_set = problem['Shift Set']
    staff_set = problem['Staff Set']
    overlap_set = problem['Overlap Set']
    scheduling_constraints = problem['Constraints']

    time_build_start = time()

    # ################ INIT SOLVER ################
    solver = Solver()
    solver.set("timeout", time_out * 1000)  # In Milliseconds

    # ################ DECISION VARS ################
    assignments = [[Bool('s_{}_p_{}'.format(i_shift, i_person))
                    for i_person in range(len(staff_set))]
                   for i_shift in range(len(shift_set))]

    # ################ DOMAIN CONDITIONS ################
    # Only one person per shift
    constraint_domain = [PbLe([(assignments[i_shift][i_person], 1) for i_person in range(len(staff_set))], 1)
                         for i_shift in range(len(shift_set))]

    # ################ SCHEDULING CONSTRAINTS ################
    constraint_scheduling = list()
    for constraint in scheduling_constraints:

        # Assignment of Shifts
        if constraint['Type'] == 0:
            num_unassigned_shifts = Sum([
             If(
                 And([
                     Not(assignments[i_shift][i_person])
                     for i_person in constraint['Staff Indexes']
                 ]),
                 1,
                 0
             )
             for i_shift in constraint['Shift Indexes']
            ])
            constraint_scheduling += [constraint['x'] <= num_unassigned_shifts,
                                      num_unassigned_shifts <= constraint['y']]

        # Qualified Assignments
        if constraint['Type'] == 1:
            num_shifts_assigned_unqualified = Sum([
                If(
                    Or([assignments[i_shift][i_person]
                        for i_person in set(constraint['Staff Indexes']).difference(
                            set(shift_set.get_shifts(i_shift).qualified_staff)
                        )
                        ]),
                    1,
                    0
                )
                for i_shift in constraint['Shift Indexes']
            ])
            constraint_scheduling += [constraint['x'] <= num_shifts_assigned_unqualified,
                                      num_shifts_assigned_unqualified <= constraint['y']]

        # Overlapping Shifts
        if constraint['Type'] == 2:
            num_times_staff_assigned_unallowed_overlapping = Sum([
                If(
                    And([
                        assignments[i_shift][i_person]
                        for i_shift in overlap.shift_indexes
                    ]),
                    1,
                    0
                )
                for overlap in overlap_set
                for i_person in set(constraint['Staff Indexes']).difference(set(overlap.staff_indexes))
            ])
            constraint_scheduling += [
                constraint['x'] <= num_times_staff_assigned_unallowed_overlapping,
                num_times_staff_assigned_unallowed_overlapping <= constraint['y']
            ]

        # Assignment Fractions
        if constraint['Type'] == 3:
            for i_person in constraint['Staff Indexes']:

                wl_certain_shifts = Sum([
                    If(assignments[i_shift][i_person],
                       shift_set.get_shifts(i_shift).workload,
                       0)
                    for i_shift in constraint['Shift Indexes']
                ])
                wl_all_shifts_x = Sum([
                    If(assignments[i_shift][i_person],
                       shift_set.get_shifts(i_shift).workload * constraint['x'],
                       0)
                    for i_shift in range(len(shift_set))
                ])
                wl_all_shifts_y = Sum([
                    If(assignments[i_shift][i_person],
                       shift_set.get_shifts(i_shift).workload * constraint['y'],
                       0)
                    for i_shift in range(len(shift_set))
                ])

                constraint_scheduling += [wl_all_shifts_x <= wl_certain_shifts]
                constraint_scheduling += [wl_certain_shifts <= wl_all_shifts_y]

        # Shift-to-Shift
        if constraint['Type'] == 4:

            num_assigned = Sum([
                If(assignments[i_shift][i_person],
                   1,
                   0)
                for i_person in constraint['Staff Indexes 2']
                for i_shift in constraint['Shift Indexes 2']
            ])

            constraint_scheduling += [Implies(
                Or([assignments[i_shift][i_person]
                    for i_person in constraint['Staff Indexes 1']
                    for i_shift in constraint['Shift Indexes 1']
                ]),
                And(constraint['x'] <= num_assigned,
                    num_assigned <= constraint['y'])
            )]

        # Consecutive Days
        if constraint['Type'] == 5:

            for i_person in constraint['Staff Indexes']:
                for i_shift in constraint['Shift Indexes']:

                    # Limit on shortest consecutive days
                    constraint_scheduling += [
                        Implies(
                            And(
                                assignments[i_shift][i_person],
                                And([ Not(assignments[j_shift][i_person])
                                    for j_shift in shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                ])
                            ),
                            And([
                                Or([assignments[j_shift][i_person]
                                    for j_shift in shift_set.get_shift_indexes_on_day(k, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                ])
                                for k in range(1, constraint['x'])
                            ])
                        )
                    ]

                    # Limit on longest consecutive days
                    constraint_scheduling += [
                        Implies(
                            And(
                                assignments[i_shift][i_person],
                                And([Not(assignments[j_shift][i_person])
                                     for j_shift in shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                     ])
                            ),
                            Or([
                                And([Not(assignments[j_shift][i_person])
                                    for j_shift in shift_set.get_shift_indexes_on_day(k, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                    ])
                                for k in range(1, constraint['y']+1)
                            ])
                        )
                    ]

        # Before and After Consecutive Days
        if constraint['Type'] == 6:
            for c in range(constraint['x'], constraint['y']+1):
                for d in shift_set.get_start_day_set():
                    for i_person in constraint['Staff Indexes']:

                        constraint_scheduling += [
                            Implies(
                                And(
                                    And([
                                        Or([assignments[i_shift][i_person]
                                            for i_shift in
                                            shift_set.get_shift_indexes_on_day(c_tilde, intersection_set=constraint['Shift Indexes'])])
                                        for c_tilde in range(d, d+c)
                                    ]),
                                    And([Not(assignments[i_shift][i_person])
                                        for i_shift in
                                        set(shift_set.get_shift_indexes_on_day(d-1, intersection_set=constraint['Shift Indexes'])).union(
                                            set(shift_set.get_shift_indexes_on_day(d+c, intersection_set=constraint['Shift Indexes'])))
                                    ])
                                ),
                                And(
                                    And([Not(assignments[i_shift][i_person])
                                        for n_tilde in range(d-constraint['n'], d)
                                        for i_shift in shift_set.get_shift_indexes_on_day(n_tilde, intersection_set=constraint['Shift Indexes n'])
                                    ]),
                                    And([Not(assignments[i_shift][i_person])
                                        for m_tilde in range(d+c, d+c+constraint['m'])
                                        for i_shift in shift_set.get_shift_indexes_on_day(m_tilde, intersection_set=constraint['Shift Indexes m'])
                                    ])
                                )
                            )
                        ]

        # Consecutive Shift Types
        if constraint['Type'] == 7:
            for i_shift in constraint['Shift Indexes']:
                for i_person in constraint['Staff Indexes']:

                    constraint_scheduling += [
                        Implies(
                            assignments[i_shift][i_person],
                            Or(
                                Or([assignments[j_shift][i_person]
                                    for j_shift in
                                    set(shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])).intersection(
                                        set(shift_set.get_shift_indexes_of_type(shift_set.get_shifts(i_shift))))
                                ]),
                                And([Not(assignments[j_shift][i_person])
                                    for j_shift in
                                    shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                                ])
                            )
                        )
                    ]

        # Fair Workload
        if constraint['Type'] == 8:

            r_e = sum([shift_set.get_shifts(i_shift).workload for i_shift in constraint['Shift Indexes']]) /\
                  sum([staff_set.get_person(i_person).desired_workload for i_person in constraint['Staff Indexes']])
            temp_lb = r_e * (1 - constraint['x'])
            temp_ub = r_e * (1 + constraint['x'])

            for i_person in constraint['Staff Indexes']:
                r = sum([
                    If(
                        assignments[i_shift][i_person],
                        shift_set.get_shifts(i_shift).workload / staff_set.get_person(i_person).desired_workload,
                        0
                    )
                    for i_shift in constraint['Shift Indexes']
                ])

                constraint_scheduling += [
                    temp_lb <= r,
                    temp_ub >= r
                ]

    # ################ ADD CONSTRAINTS TO MODEL ################
    solver.add(constraint_domain + constraint_scheduling)
    time_build = time() - time_build_start

    # ################ SOLVE ################
    time_solve_start = time()
    satisfied = solver.check()
    time_solve = time() - time_solve_start

    # Output
    output = dict()
    output['Total Time'] = time_build + time_solve
    output['Build Time'] = time_build
    output['Solve Time'] = time_solve

    if satisfied == unknown:
        output['Satisfied'] = 'Timed_Out'

    elif satisfied == sat:
        output['Satisfied'] = True
        output['Assignments'] = list()
        for i_shift in range(len(shift_set)):
            try:
                output['Assignments'].append(next(i_person for i_person in range(len(staff_set))
                                                  if solver.model()[assignments[i_shift][i_person]] == True)
                                             )
            except:
                output['Assignments'].append(-1)

    else:
        output['Satisfied'] = False

    return output


def scheduler_smt_boolmat_multicore(problem, time_out):

    # Reload z3 to reset context
    # importlib.reload(z3)

    shift_set = problem['Shift Set']
    staff_set = problem['Staff Set']
    overlap_set = problem['Overlap Set']
    scheduling_constraints = problem['Constraints']

    time_build_start = time()

    # ################ INIT SOLVER ################
    new_ctx = Context()
    solver = Solver(ctx=new_ctx)

    solver.set("timeout", time_out * 1000)  # In Milliseconds
    set_param('parallel.enable', True)  # Enable use of multiple cores

    # ################ DECISION VARS ################
    assignments = [[Bool('s_{}_p_{}'.format(i_shift, i_person), ctx=new_ctx)
                    for i_person in range(len(staff_set))]
                   for i_shift in range(len(shift_set))]

    # ################ DOMAIN CONDITIONS ################
    # Only one person per shift
    constraint_domain = [PbLe([(assignments[i_shift][i_person], 1) for i_person in range(len(staff_set))], 1)
                         for i_shift in range(len(shift_set))]

    # ################ SCHEDULING CONSTRAINTS ################
    constraint_scheduling = list()
    constraint_creation_times = [0 for _ in range(9)]

    for constraint in scheduling_constraints:

        constraint_time_start = time()

        # Assignment of Shifts
        if constraint['Type'] == 0:
            num_unassigned_shifts = Sum([
             If(
                 And([
                     Not(assignments[i_shift][i_person])
                     for i_person in constraint['Staff Indexes']
                 ]),
                 1,
                 0
             )
             for i_shift in constraint['Shift Indexes']
            ])
            constraint_scheduling += [constraint['x'] <= num_unassigned_shifts,
                                      num_unassigned_shifts <= constraint['y']]
        # Assignment of Shifts V2
        """
        if constraint['Type'] == 0:
            constraint_scheduling += [
                PbLe(
                    [
                        (And([
                            Not(assignments[i_shift][i_person]) for i_person in constraint['Staff Indexes']
                        ]), 1)
                        for i_shift in constraint['Shift Indexes']
                    ],
                    constraint['y']
                )
            ]
            constraint_scheduling += [
                PbGe(
                    [
                        (And([
                            Not(assignments[i_shift][i_person]) for i_person in constraint['Staff Indexes']
                        ]), 1)
                        for i_shift in constraint['Shift Indexes']
                    ],
                    constraint['x']
                )
            ]
        """

        # Qualified Assignments
        """
        if constraint['Type'] == 1:
            num_shifts_assigned_unqualified = Sum([
                If(
                    Or([assignments[i_shift][i_person]
                        for i_person in set(constraint['Staff Indexes']).difference(
                            set(shift_set.get_shifts(i_shift).qualified_staff)
                        )
                        ]),
                    1,
                    0
                )
                for i_shift in constraint['Shift Indexes']
            ])
            constraint_scheduling += [constraint['x'] <= num_shifts_assigned_unqualified,
                                      num_shifts_assigned_unqualified <= constraint['y']]
        """
        # Qualified Assignments V2
        if constraint['Type'] == 1:
            constraint_scheduling += [
                PbLe(
                    [(Or([assignments[i_shift][i_person]
                          for i_person in set(constraint['Staff Indexes']).difference(
                            set(shift_set.get_shifts(i_shift).qualified_staff))]
                         , new_ctx), 1)
                     for i_shift in constraint['Shift Indexes']],
                    constraint['y']
                )
            ]
            constraint_scheduling += [
                PbGe(
                    [(Or([assignments[i_shift][i_person]
                          for i_person in set(constraint['Staff Indexes']).difference(
                            set(shift_set.get_shifts(i_shift).qualified_staff))]
                         , new_ctx), 1)
                     for i_shift in constraint['Shift Indexes']],
                    constraint['x']
                )
            ]

        # Overlapping Shifts
        """
        if constraint['Type'] == 2:

            num_times_staff_assigned_unallowed_overlapping = Sum([
                If(
                    And([
                        assignments[i_shift][i_person]
                        for i_shift in overlap.shift_indexes
                    ]),
                    1,
                    0
                )
                for overlap in overlap_set
                for i_person in set(constraint['Staff Indexes']).difference(set(overlap.staff_indexes))
            ])
            constraint_scheduling += [
                constraint['x'] <= num_times_staff_assigned_unallowed_overlapping,
                num_times_staff_assigned_unallowed_overlapping <= constraint['y']
            ]
        """
        # Overlapping Shifts V3
        if constraint['Type'] == 2:

            """
            start_time = time()
            temp = [(And([assignments[i_shift][i_person] for i_shift in overlap.shift_indexes]), 1)
                    for overlap in overlap_set
                    for i_person in set(constraint['Staff Indexes']).difference(set(overlap.staff_indexes))]
            print('\t\tTemp creation time: {}'.format(time()-start_time))
            constraint_scheduling += [
                PbLe(temp, constraint['y'])
            ]
            constraint_scheduling += [
                PbGe(temp, constraint['x'])
            ]
            """

            """ 
            # No overlap allowed
            constraint_scheduling += [
                Not(
                    And(
                        assignments[overlap.shift_indexes[0]][person.index],
                        assignments[overlap.shift_indexes[1]][person.index]
                    )
                )
                for person in staff_set
                for overlap in overlap_set if len(overlap.shift_indexes) == 2
            ]
            """

            # All subsets of allowed shift set are also allowed
            all_pairs = [k for k in overlap_set if len(k.shift_indexes) == 2]

            staff_allowed_overlaps = [[k for k in overlap_set if person_index in k.staff_indexes]
                                      for person_index in constraint['Staff Indexes']]

            forbidden_pairs = [
                (
                    And(
                        assignments[overlap_pair.shift_indexes[0]][person_index],
                        assignments[overlap_pair.shift_indexes[1]][person_index]
                    ),
                    1
                )
                for i_person, person_index in enumerate(constraint['Staff Indexes'])
                for overlap_pair in all_pairs
                if not any(set(overlap_pair.shift_indexes).issubset(allowed_overlap.shift_indexes)
                           for allowed_overlap in staff_allowed_overlaps[i_person])
            ]

            constraint_scheduling += [
                PbGe(forbidden_pairs, constraint['x']),
                PbLe(forbidden_pairs, constraint['y'])
            ]

        # Assignment Fractions
        """
        if constraint['Type'] == 3:
            for i_person in constraint['Staff Indexes']:

                wl_certain_shifts = Sum([
                    If(assignments[i_shift][i_person],
                       shift_set.get_shifts(i_shift).workload,
                       0)
                    for i_shift in constraint['Shift Indexes']
                ])
                wl_all_shifts_x = Sum([
                    If(assignments[i_shift][i_person],
                       shift_set.get_shifts(i_shift).workload * constraint['x'],
                       0)
                    for i_shift in range(len(shift_set))
                ])
                wl_all_shifts_y = Sum([
                    If(assignments[i_shift][i_person],
                       shift_set.get_shifts(i_shift).workload * constraint['y'],
                       0)
                    for i_shift in range(len(shift_set))
                ])

                constraint_scheduling += [wl_all_shifts_x <= wl_certain_shifts]
                constraint_scheduling += [wl_certain_shifts <= wl_all_shifts_y]
        """
        # Assignment Fractions V2
        if constraint['Type'] == 3:
            precision_factor = 1000

            for i_person in constraint['Staff Indexes']:

                wl_certain_shifts = Sum([
                    If(assignments[i_shift][i_person],
                       int( precision_factor * shift_set.get_shifts(i_shift).workload ),
                       0)
                    for i_shift in constraint['Shift Indexes']
                ])
                wl_all_shifts_x = Sum([
                    If(assignments[i_shift][i_person],
                       int( precision_factor * shift_set.get_shifts(i_shift).workload * constraint['x'] ),
                       0)
                    for i_shift in range(len(shift_set))
                ])
                wl_all_shifts_y = Sum([
                    If(assignments[i_shift][i_person],
                       int( precision_factor * shift_set.get_shifts(i_shift).workload * constraint['y'] ),
                       0)
                    for i_shift in range(len(shift_set))
                ])

                constraint_scheduling += [wl_all_shifts_x <= wl_certain_shifts]
                constraint_scheduling += [wl_certain_shifts <= wl_all_shifts_y]

        # Shift-to-Shift
        if constraint['Type'] == 4:

            num_assigned = Sum([
                If(assignments[i_shift][i_person],
                   1,
                   0)
                for i_person in constraint['Staff Indexes 2']
                for i_shift in constraint['Shift Indexes 2']
            ])

            constraint_scheduling += [Implies(
                Or([assignments[i_shift][i_person]
                    for i_person in constraint['Staff Indexes 1']
                    for i_shift in constraint['Shift Indexes 1']
                ], new_ctx),
                And(constraint['x'] <= num_assigned,
                    num_assigned <= constraint['y'], new_ctx)
            )]

        # Consecutive Days
        if constraint['Type'] == 5:

            # for i_person in constraint['Staff Indexes']:
                # for i_shift in constraint['Shift Indexes']:

            # Limit on shortest consecutive days
            constraint_scheduling += [
                Implies(
                    And([
                        assignments[i_shift][i_person],
                        And([Not(assignments[j_shift][i_person])
                            for j_shift in shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                        ], new_ctx)
                    ], new_ctx),
                    And([
                        Or([assignments[j_shift][i_person]
                            for j_shift in shift_set.get_shift_indexes_on_day(k, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                        ], new_ctx)
                        for k in range(1, constraint['x'])
                    ], new_ctx)
                )
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]

            # Limit on longest consecutive days
            constraint_scheduling += [
                Implies(
                    And(
                        assignments[i_shift][i_person],
                        And([Not(assignments[j_shift][i_person])
                             for j_shift in shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                             ], new_ctx),
                        new_ctx
                    ),
                    Or([
                        And([Not(assignments[j_shift][i_person])
                            for j_shift in shift_set.get_shift_indexes_on_day(k, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                            ], new_ctx)
                        for k in range(1, constraint['y']+1)
                    ], new_ctx)
                )
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]

        # Before and After Consecutive Days
        if constraint['Type'] == 6:
            # for c in range(constraint['x'], constraint['y']+1):
                # for d in shift_set.get_start_day_set():
                    # for i_person in constraint['Staff Indexes']:

            constraint_scheduling += [
                Implies(
                    And(
                        And([
                            Or([assignments[i_shift][i_person]
                                for i_shift in
                                shift_set.get_shift_indexes_on_day(c_tilde, intersection_set=constraint['Shift Indexes'])],
                               new_ctx)
                            for c_tilde in range(d, d+c)
                        ], new_ctx),
                        And([Not(assignments[i_shift][i_person])
                            for i_shift in
                            set(shift_set.get_shift_indexes_on_day(d-1, intersection_set=constraint['Shift Indexes'])).union(
                                set(shift_set.get_shift_indexes_on_day(d+c, intersection_set=constraint['Shift Indexes'])))
                        ], new_ctx),
                        new_ctx
                    ),
                    And(
                        And([Not(assignments[i_shift][i_person])
                            for n_tilde in range(d-constraint['n'], d)
                            for i_shift in shift_set.get_shift_indexes_on_day(n_tilde, intersection_set=constraint['Shift Indexes n'])
                        ], new_ctx),
                        And([Not(assignments[i_shift][i_person])
                            for m_tilde in range(d+c, d+c+constraint['m'])
                            for i_shift in shift_set.get_shift_indexes_on_day(m_tilde, intersection_set=constraint['Shift Indexes m'])
                        ], new_ctx),
                        new_ctx)
                )
                for i_person in constraint['Staff Indexes']
                for d in shift_set.get_start_day_set()
                for c in range(constraint['x'], constraint['y'] + 1)
            ]

        # Consecutive Shift Types
        if constraint['Type'] == 7:
            constraint_scheduling += [
                Implies(
                    assignments[i_shift][i_person],
                    Or(
                        Or([assignments[j_shift][i_person]
                            for j_shift in
                            set(shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])).intersection(
                                set(shift_set.get_shift_indexes_of_type(shift_set.get_shifts(i_shift))))
                        ], new_ctx),
                        And([Not(assignments[j_shift][i_person])
                            for j_shift in
                            shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                        ], new_ctx)
                    ),
                new_ctx)
                for i_person in constraint['Staff Indexes']
                for i_shift in constraint['Shift Indexes']
            ]

        # Fair Workload
        """
        if constraint['Type'] == 8:

            r_e = sum([shift_set.get_shifts(i_shift).workload for i_shift in constraint['Shift Indexes']]) /\
                  sum([staff_set.get_person(i_person).desired_workload for i_person in constraint['Staff Indexes']])
            temp_lb = r_e * (1 - constraint['x'])
            temp_ub = r_e * (1 + constraint['x'])

            for i_person in constraint['Staff Indexes']:
                r = sum([
                    If(
                        assignments[i_shift][i_person],
                        shift_set.get_shifts(i_shift).workload / staff_set.get_person(i_person).desired_workload,
                        0
                    )
                    for i_shift in constraint['Shift Indexes']
                ])

                constraint_scheduling += [
                    temp_lb <= r,
                    temp_ub >= r
                ]
        """
        # Fair Workload V5
        if constraint['Type'] == 8:

            precision_factor = 1000

            r_e = sum([shift_set.get_shifts(i_shift).workload for i_shift in constraint['Shift Indexes']]) / \
                  sum([staff_set.get_person(i_person).desired_workload for i_person in constraint['Staff Indexes']])
            temp_lb = r_e * (1 - constraint['x'])
            temp_ub = r_e * (1 + constraint['x'])

            constraint_scheduling += [
                PbLe(
                    [
                        (assignments[i_shift][i_person],
                         int(precision_factor * shift_set.get_shifts(i_shift).workload /
                             staff_set.get_person(i_person).desired_workload)
                         ) for i_shift in constraint['Shift Indexes']
                    ],
                    int(temp_ub * precision_factor)
                )
                for i_person in constraint['Staff Indexes']
            ]
            constraint_scheduling += [
                PbGe(
                    [
                        (assignments[i_shift][i_person],
                         int(precision_factor * shift_set.get_shifts(i_shift).workload /
                             staff_set.get_person(i_person).desired_workload)
                         ) for i_shift in constraint['Shift Indexes']
                    ],
                    int(temp_lb * precision_factor)
                )
                for i_person in constraint['Staff Indexes']
            ]
        # Fair Workload V4
        """
        if constraint['Type'] == 8:

            precision_factor = 1000

            r_e = sum([shift_set.get_shifts(i_shift).workload for i_shift in constraint['Shift Indexes']]) /\
                  sum([staff_set.get_person(i_person).desired_workload for i_person in constraint['Staff Indexes']])
            temp_lb = r_e * (1 - constraint['x'])
            temp_ub = r_e * (1 + constraint['x'])

            for i_person in constraint['Staff Indexes']:
                r = sum([
                    If(
                        assignments[i_shift][i_person],
                        int(precision_factor * shift_set.get_shifts(i_shift).workload / staff_set.get_person(i_person).desired_workload),
                        0
                    )
                    for i_shift in constraint['Shift Indexes']
                ])

                constraint_scheduling += [
                    temp_lb <= int(r*precision_factor),
                    temp_ub >= int(r*precision_factor)
                ]
        """
        # Fair Workload V3
        """
        if constraint['Type'] == 8:

            r_e = sum([shift_set.get_shifts(i_shift).workload for i_shift in constraint['Shift Indexes']]) / \
                  sum([staff_set.get_person(i_person).desired_workload for i_person in
                       constraint['Staff Indexes']])
            temp_lb = r_e * (1 - constraint['x'])
            temp_ub = r_e * (1 + constraint['x'])

            constraint_scheduling += [
                Sum(
                    [
                        If(assignments[i_shift][i_person],
                           shift_set.get_shifts(i_shift).workload,
                           0)
                        for i_shift in constraint['Shift Indexes']
                    ]
                ) <= (temp_ub * staff_set.get_person(i_person).desired_workload)
                for i_person in constraint['Staff Indexes']
            ]
            constraint_scheduling += [
                Sum(
                    [
                        If(assignments[i_shift][i_person],
                           shift_set.get_shifts(i_shift).workload,
                           0)
                        for i_shift in constraint['Shift Indexes']
                    ]
                ) >= (temp_lb * staff_set.get_person(i_person).desired_workload)
                for i_person in constraint['Staff Indexes']
            ]
        """
        # Fair Workload V2 (Not working, PbLe and PbGe need ints, not floats)
        """
        if constraint['Type'] == 8:

            r_e = sum([shift_set.get_shifts(i_shift).workload for i_shift in constraint['Shift Indexes']]) / \
                  sum([staff_set.get_person(i_person).desired_workload for i_person in constraint['Staff Indexes']])
            temp_lb = r_e * (1 - constraint['x'])
            temp_ub = r_e * (1 + constraint['x'])

            constraint_scheduling += [
                PbLe(
                    [
                        (assignments[i_shift][i_person], 1) * shift_set.get_shifts(i_shift).workload / staff_set.get_person(i_person).desired_workload
                        for i_shift in constraint['Shift Indexes']
                    ],
                    temp_ub
                )
                for i_person in constraint['Staff Indexes']
            ]
            constraint_scheduling += [
                PbGe(
                    [
                        (assignments[i_shift][i_person], 1) * shift_set.get_shifts(i_shift).workload / staff_set.get_person(i_person).desired_workload
                        for i_shift in constraint['Shift Indexes']
                    ],
                    temp_lb
                )
                for i_person in constraint['Staff Indexes']
            ]
        """

        constraint_creation_times[constraint['Type']] += time() - constraint_time_start

    """
    print('\nSMT Model Constraint Times´')
    for type_i in range(9):
        print('\t\t Type {}: {} s'.format(type_i, constraint_creation_times[type_i]))
    """

    # ################ ADD CONSTRAINTS TO MODEL ################
    solver.add(constraint_domain + constraint_scheduling)
    time_build = time() - time_build_start

    # ################ SOLVE ################
    time_solve_start = time()
    satisfied = solver.check()
    time_solve = time() - time_solve_start

    # Output
    output = dict()
    output['Total Time'] = time_build + time_solve
    output['Build Time'] = time_build
    output['Solve Time'] = time_solve

    if satisfied == unknown:
        output['Satisfied'] = 'Timed_Out'
    elif satisfied == sat:
        output['Satisfied'] = True
        output['Assignments'] = list()
        for i_shift in range(len(shift_set)):
            try:
                output['Assignments'].append(next(i_person for i_person in range(len(staff_set))
                                                  if solver.model()[assignments[i_shift][i_person]] == True))
            except:
                output['Assignments'].append(-1)
    else:
        output['Satisfied'] = False

    return output
