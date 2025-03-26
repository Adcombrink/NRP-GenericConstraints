from gurobipy import *
from time import time


def scheduler_milp_binmat(problem, time_out):

    shift_set = problem['Shift Set']
    staff_set = problem['Staff Set']
    overlap_set = problem['Overlap Set']
    scheduling_constraints = problem['Constraints']

    time_build_start = time()

    # ################ INIT SOLVER ################
    m = Model('Scheduling')
    m.Params.OutputFlag = 0
    m.Params.TimeLimit = time_out   # In Seconds
    # m.setParam('Threads', 1)
    # m.setParam('Method', 1)

    # ################ DECISION VARS ################
    assignments = m.addVars(range(len(staff_set)), range(len(shift_set)), vtype=GRB.BINARY, name='Assignments')

    # ################ INHERENT CONSTRAINTS ################
    # Max one person per shift
    constraint_inherent = [
        sum(assignments[i_person, i_shift] for i_person in range(len(staff_set))) <= 1
        for i_shift in range(len(shift_set))
    ]

    # ################ SCHEDULING CONSTRAINTS ################

    constraint_scheduling = list()
    for i_constraint, constraint in enumerate(scheduling_constraints):

        # Assignment of Shifts
        if constraint['Type'] == 0:

            # Add intermittent variables
            inter1 = m.addVars(constraint['Shift Indexes'],
                               vtype=GRB.BINARY,
                               name='C{}_Inter1'.format(i_constraint))

            # Add constraints
            constraint_scheduling += [
                constraint['x'] <= sum(inter1[i_shift] for i_shift in constraint['Shift Indexes']),
                sum(inter1[i_shift] for i_shift in constraint['Shift Indexes']) <= constraint['y']
            ]

            M = len(constraint['Staff Indexes'])
            constraint_scheduling += [
                sum(assignments[i_person, i_shift] for i_person in constraint['Staff Indexes']) <= M*(1-inter1[i_shift])
                for i_shift in constraint['Shift Indexes']
            ]
            constraint_scheduling += [
                sum(assignments[i_person, i_shift] for i_person in constraint['Staff Indexes']) >= 1 - inter1[i_shift]
                for i_shift in constraint['Shift Indexes']
            ]

        # Qualified Assignments
        if constraint['Type'] == 1:

            # Add intermittent variables
            inter1 = m.addVars(constraint['Shift Indexes'],
                               vtype=GRB.BINARY,
                               name='C{}_Inter1'.format(i_constraint))

            # Add constraint
            constraint_scheduling += [
                constraint['x'] <= sum(inter1[i_shift] for i_shift in constraint['Shift Indexes']),
                sum(inter1[i_shift] for i_shift in constraint['Shift Indexes']) <= constraint['y']
            ]

            M = len(constraint['Staff Indexes'])
            constraint_scheduling += [
                sum(assignments[i_person, i_shift] for i_person in set(constraint['Staff Indexes']).difference(
                    shift_set.get_shifts(i_shift).qualified_staff)) >= inter1[i_shift]
                for i_shift in constraint['Shift Indexes']
            ]
            constraint_scheduling += [
                sum(assignments[i_person, i_shift] for i_person in set(constraint['Staff Indexes']).difference(
                    shift_set.get_shifts(i_shift).qualified_staff)) <= M * inter1[i_shift]
                for i_shift in constraint['Shift Indexes']
            ]

        # Overlapping Shifts
        if constraint['Type'] == 2:

            """
            # ---- Original ----
            # Add intermittent variables
            inter1 = dict()
            for i_overlap, overlap in enumerate(overlap_set):
                for i_person in set(constraint['Staff Indexes']).difference(overlap.staff_indexes):
                    inter1[(i_overlap, i_person)] = m.addVar(vtype=GRB.BINARY,
                                                             name='C{}_Inter1'.format(i_constraint))

            # Add constraints
            constraint_scheduling += [
                constraint['x'] <= sum(
                    sum(inter1[(i_overlap, i_person)]
                        for i_person in set(constraint['Staff Indexes']).difference(overlap.staff_indexes))
                    for i_overlap, overlap in enumerate(overlap_set)
                ),
                sum(
                    sum(inter1[(i_overlap, i_person)]
                        for i_person in set(constraint['Staff Indexes']).difference(overlap.staff_indexes))
                    for i_overlap, overlap in enumerate(overlap_set)
                ) <= constraint['y']
            ]
            constraint_scheduling += [
                sum(1 - assignments[i_person, i_shift] for i_shift in overlap.shift_indexes) >= 1 - inter1[(i_overlap, i_person)]
                for i_overlap, overlap in enumerate(overlap_set)
                for i_person in set(constraint['Staff Indexes']).difference(overlap.staff_indexes)
            ]
            constraint_scheduling += [
                assignments[i_person, i_shift] >= inter1[(i_overlap, i_person)]
                for i_overlap, overlap in enumerate(overlap_set)
                for i_shift in overlap.shift_indexes
                for i_person in set(constraint['Staff Indexes']).difference(overlap.staff_indexes)
            ]
            """

            # ---- Subsets of allowed shift combos are also allowed ----
            all_pairs = [k for k in overlap_set if len(k.shift_indexes) == 2]

            staff_allowed_overlaps = [[k for k in overlap_set if person_index in k.staff_indexes]
                                      for person_index in constraint['Staff Indexes']]

            forbidden_pairs = [
                (
                    assignments[person_index, overlap_pair.shift_indexes[0]],
                    assignments[person_index, overlap_pair.shift_indexes[1]]
                )
                for i_person, person_index in enumerate(constraint['Staff Indexes'])
                for overlap_pair in all_pairs
                if not any(set(overlap_pair.shift_indexes).issubset(allowed_overlap.shift_indexes)
                           for allowed_overlap in staff_allowed_overlaps[i_person])
            ]

            # Add intermittent variables
            inter1 = [m.addVar(vtype=GRB.BINARY, name='C{}_Inter1'.format(i_constraint))
                      for _, _ in forbidden_pairs]

            # Add intermediate constraint
            constraint_scheduling += [
                forbidden_pair[0] + forbidden_pair[1] - 1 <= inter1[i_pair]
                for i_pair, forbidden_pair in enumerate(forbidden_pairs)
            ]
            constraint_scheduling += [
                forbidden_pair[0] + forbidden_pair[1] >= inter1[i_pair]
                for i_pair, forbidden_pair in enumerate(forbidden_pairs)
            ]

            # Add constraint
            constraint_scheduling += [
                sum(inter1[i_pair] for i_pair, _ in enumerate(forbidden_pairs)) >= constraint['x'],
                sum(inter1[i_pair] for i_pair, _ in enumerate(forbidden_pairs)) <= constraint['y']
            ]

        # Assignment Fractions
        """
        if constraint['Type'] == 3:
            constraint_scheduling += [
                sum(shift_set.get_shifts(i_shift).workload * assignments[i_person, i_shift]
                    for i_shift in constraint['Shift Indexes'])
                >= constraint['x'] *
                sum(shift_set.get_shifts(i_shift).workload * assignments[i_person, i_shift]
                    for i_shift in range(len(shift_set)))
                for i_person in constraint['Staff Indexes']
            ]
            constraint_scheduling += [
                sum(shift_set.get_shifts(i_shift).workload * assignments[i_person, i_shift]
                    for i_shift in constraint['Shift Indexes'])
                <= constraint['y'] *
                sum(shift_set.get_shifts(i_shift).workload * assignments[i_person, i_shift]
                    for i_shift in range(len(shift_set)))
                for i_person in constraint['Staff Indexes']
            ]
        """
        # Assignment Fractions V2
        """
        if constraint['Type'] == 3:
            precision_factor = 1000

            constraint_scheduling += [
                sum( int( precision_factor * shift_set.get_shifts(i_shift).workload ) * assignments[i_person, i_shift]
                    for i_shift in constraint['Shift Indexes'])
                >= constraint['x'] *
                sum( int( precision_factor * shift_set.get_shifts(i_shift).workload ) * assignments[i_person, i_shift]
                    for i_shift in range(len(shift_set)))
                for i_person in constraint['Staff Indexes']
            ]
            constraint_scheduling += [
                sum( int( precision_factor * shift_set.get_shifts(i_shift).workload ) * assignments[i_person, i_shift]
                    for i_shift in constraint['Shift Indexes'])
                <= constraint['y'] *
                sum( int( precision_factor * shift_set.get_shifts(i_shift).workload ) * assignments[i_person, i_shift]
                    for i_shift in range(len(shift_set)))
                for i_person in constraint['Staff Indexes']
            ]
        """
        # Assignment Fractions V3
        if constraint['Type'] == 3:
            precision_factor = 1000

            constraint_scheduling += [
                sum(int(precision_factor * shift_set.get_shifts(i_shift).workload) * assignments[i_person, i_shift]
                    for i_shift in constraint['Shift Indexes'])
                >=
                sum(int(constraint['x'] * precision_factor * shift_set.get_shifts(i_shift).workload) * assignments[i_person, i_shift]
                    for i_shift in range(len(shift_set)))
                for i_person in constraint['Staff Indexes']
            ]
            constraint_scheduling += [
                sum(int(precision_factor * shift_set.get_shifts(i_shift).workload) * assignments[i_person, i_shift]
                    for i_shift in constraint['Shift Indexes'])
                <=
                sum(int(constraint['y'] * precision_factor * shift_set.get_shifts(i_shift).workload) * assignments[i_person, i_shift]
                    for i_shift in range(len(shift_set)))
                for i_person in constraint['Staff Indexes']
            ]

        # Shift-to-Shift
        if constraint['Type'] == 4:

            # Add intermittent variables
            inter1 = m.addVar(vtype=GRB.BINARY, name='C{}_Inter1'.format(i_constraint))
            inter2 = m.addVars(constraint['Staff Indexes 2'], constraint['Shift Indexes 2'],
                               vtype=GRB.BINARY,
                               name='C{}_Inter2'.format(i_constraint))

            # Add constraints
            constraint_scheduling += [
                constraint['x'] <= sum(inter2[i_person, i_shift]
                                       for i_person in constraint['Staff Indexes 2']
                                       for i_shift in constraint['Shift Indexes 2']),
                constraint['y'] >= sum(inter2[i_person, i_shift]
                                       for i_person in constraint['Staff Indexes 2']
                                       for i_shift in constraint['Shift Indexes 2'])
            ]

            M = len(constraint['Staff Indexes 1']) * len(constraint['Shift Indexes 1'])
            constraint_scheduling += [
                sum(assignments[i_person, i_shift]
                    for i_person in constraint['Staff Indexes 1']
                    for i_shift in constraint['Shift Indexes 1']) >= inter1,
                sum(assignments[i_person, i_shift]
                    for i_person in constraint['Staff Indexes 1']
                    for i_shift in constraint['Shift Indexes 1']) <= M * inter1
            ]

            constraint_scheduling += [
                inter1 + assignments[i_person, i_shift] <= 1 + inter2[i_person, i_shift]
                for i_person in constraint['Staff Indexes 2']
                for i_shift in constraint['Shift Indexes 2']
            ]
            constraint_scheduling += [
                inter1 >= inter2[i_person, i_shift]
                for i_person in constraint['Staff Indexes 2']
                for i_shift in constraint['Shift Indexes 2']
            ]
            constraint_scheduling += [
                assignments[i_person, i_shift] >= inter2[i_person, i_shift]
                for i_person in constraint['Staff Indexes 2']
                for i_shift in constraint['Shift Indexes 2']
            ]

        # Consecutive Days
        if constraint['Type'] == 5:

            # Add intermittent variables
            inter1 = m.addVars(constraint['Shift Indexes'], constraint['Staff Indexes'],
                               vtype=GRB.BINARY, name='C{}_Inter1'.format(i_constraint))
            interA1 = m.addVars(constraint['Shift Indexes'], constraint['Staff Indexes'], range(1, constraint['x']),
                               vtype=GRB.BINARY, name='C{}_InterA1'.format(i_constraint))
            interA2 = m.addVars(constraint['Shift Indexes'], constraint['Staff Indexes'],
                               vtype=GRB.BINARY, name='C{}_InterA2'.format(i_constraint))
            interB1 = m.addVars(constraint['Shift Indexes'], constraint['Staff Indexes'], range(1, constraint['y']+1),
                                vtype=GRB.BINARY, name='C{}_InterB1'.format(i_constraint))
            interB2 = m.addVars(constraint['Shift Indexes'], constraint['Staff Indexes'],
                                vtype=GRB.BINARY, name='C{}_InterB2'.format(i_constraint))

            # ---- Add constraints
            # LHS
            constraint_scheduling += [
                (1 - assignments[i_person, i_shift]) +
                sum(assignments[i_person, j_shift]
                    for j_shift in shift_set.get_shift_indexes_on_day(-1,
                                                                      relative_shift=i_shift,
                                                                      intersection_set=constraint['Shift Indexes'])
                    )
                >= 1 - inter1[i_shift, i_person]
                for i_person in constraint['Staff Indexes']
                for i_shift in constraint['Shift Indexes']
            ]
            M1 = len(constraint['Shift Indexes'])
            constraint_scheduling += [
                (1 - assignments[i_person, i_shift]) +
                sum(assignments[i_person, j_shift]
                    for j_shift in shift_set.get_shift_indexes_on_day(-1,
                                                                      relative_shift=i_shift,
                                                                      intersection_set=constraint['Shift Indexes'])
                    )
                <= M1 * (1 - inter1[i_shift, i_person])
                for i_person in constraint['Staff Indexes']
                for i_shift in constraint['Shift Indexes']
            ]

            # Minimum x constraint
            constraint_scheduling += [
                sum(assignments[i_person, j_shift] for j_shift in
                    shift_set.get_shift_indexes_on_day(k, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])
                    )
                >= interA1[i_shift, i_person, k]
                for k in range(1, constraint['x'])
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]
            constraint_scheduling += [
                sum(assignments[i_person, j_shift] for j_shift in
                    shift_set.get_shift_indexes_on_day(k, relative_shift=i_shift,
                                                       intersection_set=constraint['Shift Indexes'])
                    )
                <= M1 * interA1[i_shift, i_person, k]
                for k in range(1, constraint['x'])
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]

            constraint_scheduling += [
                sum(1-interA1[i_shift, i_person, k] for k in range(1, constraint['x'])) >= 1 - interA2[i_shift, i_person]
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]
            M2 = constraint['x'] - 1
            constraint_scheduling += [
                sum(1-interA1[i_shift, i_person, k] for k in range(1, constraint['x'])) <= M2 * (1 - interA2[i_shift, i_person])
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]
            constraint_scheduling += [
                inter1[i_shift, i_person] - interA2[i_shift, i_person] <= 0
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]

            # Maximum y constraint
            constraint_scheduling += [
                sum(assignments[i_person, j_shift] for j_shift in
                    shift_set.get_shift_indexes_on_day(k,
                                                       relative_shift=i_shift,
                                                       intersection_set=constraint['Shift Indexes']))
                >= 1 - interB1[i_shift, i_person, k]
                for k in range(1, constraint['y'] + 1)
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]
            M1 = len(constraint['Shift Indexes'])
            constraint_scheduling += [
                sum(assignments[i_person, j_shift] for j_shift in
                    shift_set.get_shift_indexes_on_day(k,
                                                       relative_shift=i_shift,
                                                       intersection_set=constraint['Shift Indexes']))
                <= M1 * (1 - interB1[i_shift, i_person, k])
                for k in range(1, constraint['y'] + 1)
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]

            constraint_scheduling += [
                sum(interB1[i_shift, i_person, k] for k in range(1, constraint['y']+1)) >= interB2[i_shift, i_person]
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]
            M3 = constraint['y']
            constraint_scheduling += [
                sum(interB1[i_shift, i_person, k] for k in range(1, constraint['y'] + 1)) <= M3 * interB2[i_shift, i_person]
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]
            constraint_scheduling += [
                inter1[i_shift, i_person] - interB2[i_shift, i_person] <= 0
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]

        # Before and After Consecutive Days
        if constraint['Type'] == 6:

            # Add intermittent variables
            inter1 = m.addVars(constraint['Staff Indexes'], shift_set.get_start_day_set().union(range(max(shift_set.get_start_day_set()) + constraint['y'])),
                               vtype=GRB.BINARY, name='C{}_Inter1'.format(i_constraint))
            interA = m.addVars(constraint['Staff Indexes'], shift_set.get_start_day_set(),
                               range(constraint['x'], constraint['y']+1),
                               vtype=GRB.BINARY, name='C{}_InterA'.format(i_constraint))
            interB = m.addVars(constraint['Staff Indexes'], shift_set.get_start_day_set(),
                               range(constraint['x'], constraint['y'] + 1),
                               vtype=GRB.BINARY, name='C{}_InterB'.format(i_constraint))

            # Add constraints
            constraint_scheduling += [
                sum(assignments[i_person, i_shift] for i_shift in
                    shift_set.get_shift_indexes_on_day(d, intersection_set=constraint['Shift Indexes']))
                >= inter1[i_person, d]
                for d in shift_set.get_start_day_set()
                for i_person in constraint['Staff Indexes']
            ]
            M1 = len(constraint['Shift Indexes'])
            constraint_scheduling += [
                sum(assignments[i_person, i_shift] for i_shift in
                    shift_set.get_shift_indexes_on_day(d, intersection_set=constraint['Shift Indexes']))
                <= M1 * inter1[i_person, d]
                for d in shift_set.get_start_day_set()
                for i_person in constraint['Staff Indexes']
            ]

            constraint_scheduling += [
                sum(1 - inter1[i_person, c_tilde] for c_tilde in range(d, d + c)) +
                sum(assignments[i_person, i_shift] for i_shift in
                    set(shift_set.get_shift_indexes_on_day(d-1, intersection_set=constraint['Shift Indexes'])).union(
                        shift_set.get_shift_indexes_on_day(d+c, intersection_set=constraint['Shift Indexes']))
                    )
                >= 1 - interA[i_person, d, c]
                for c in range(constraint['x'], constraint['y']+1)
                for d in shift_set.get_start_day_set()
                for i_person in constraint['Staff Indexes']
            ]
            M2 = constraint['y'] + len(constraint['Shift Indexes'])
            constraint_scheduling += [
                sum(1 - inter1[i_person, c_tilde] for c_tilde in range(d, d + c)) +
                sum(assignments[i_person, i_shift] for i_shift in
                    set(shift_set.get_shift_indexes_on_day(d - 1, intersection_set=constraint['Shift Indexes'])).union(
                        shift_set.get_shift_indexes_on_day(d + c, intersection_set=constraint['Shift Indexes']))
                    )
                <= M2 * (1 - interA[i_person, d, c])
                for c in range(constraint['x'], constraint['y'] + 1)
                for d in shift_set.get_start_day_set()
                for i_person in constraint['Staff Indexes']
            ]

            constraint_scheduling += [
                sum(assignments[i_person, i_shift]
                    for n_tilde in range(d - constraint['n'], d)
                    for i_shift in shift_set.get_shift_indexes_on_day(n_tilde, intersection_set=constraint['Shift Indexes n'])
                    ) +
                sum(assignments[i_person, i_shift]
                    for m_tilde in range(d + c, d + c + constraint['m'])
                    for i_shift in shift_set.get_shift_indexes_on_day(m_tilde, intersection_set=constraint['Shift Indexes m'])
                    )
                >= 1 - interB[i_person, d, c]
                for c in range(constraint['x'], constraint['y']+1)
                for d in shift_set.get_start_day_set()
                for i_person in constraint['Staff Indexes']
            ]
            M3 = len(constraint['Shift Indexes n']) + len(constraint['Shift Indexes m'])
            constraint_scheduling += [
                sum(assignments[i_person, i_shift]
                    for n_tilde in range(d - constraint['n'], d)
                    for i_shift in
                    shift_set.get_shift_indexes_on_day(n_tilde, intersection_set=constraint['Shift Indexes n'])
                    ) +
                sum(assignments[i_person, i_shift]
                    for m_tilde in range(d + c, d + c + constraint['m'])
                    for i_shift in
                    shift_set.get_shift_indexes_on_day(m_tilde, intersection_set=constraint['Shift Indexes m'])
                    )
                <= M3 * (1 - interB[i_person, d, c])
                for c in range(constraint['x'], constraint['y'] + 1)
                for d in shift_set.get_start_day_set()
                for i_person in constraint['Staff Indexes']
            ]

            constraint_scheduling += [
                interA[i_person, d, c] - interB[i_person, d, c] <= 0
                for c in range(constraint['x'], constraint['y'] + 1)
                for d in shift_set.get_start_day_set()
                for i_person in constraint['Staff Indexes']
            ]

        # Consecutive Shift Types
        if constraint['Type'] == 7:

            # Add intermittent variables
            interA = m.addVars(constraint['Shift Indexes'], constraint['Staff Indexes'],
                               vtype=GRB.BINARY, name='C{}_InterA'.format(i_constraint))
            interB = m.addVars(constraint['Shift Indexes'], constraint['Staff Indexes'],
                               vtype=GRB.BINARY, name='C{}_InterA'.format(i_constraint))

            # Add constraints
            constraint_scheduling += [
                sum(assignments[i_person, j_shift] for j_shift in
                    set(shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes'])).intersection(
                        shift_set.get_shift_indexes_of_type(shift_set.get_shifts(i_shift), intersection_set=constraint['Shift Indexes']))
                    )
                >= interA[i_shift, i_person]
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]
            M = len(constraint['Shift Indexes'])
            constraint_scheduling += [
                sum(assignments[i_person, j_shift] for j_shift in
                    set(shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift,
                                                           intersection_set=constraint['Shift Indexes'])).intersection(
                        shift_set.get_shift_indexes_of_type(shift_set.get_shifts(i_shift),
                                                            intersection_set=constraint['Shift Indexes']))
                    )
                <= M * interA[i_shift, i_person]
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]

            constraint_scheduling += [
                sum(assignments[i_person, j_shift] for j_shift in
                    shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes']))
                >= 1 - interB[i_shift, i_person]
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]
            constraint_scheduling += [
                sum(assignments[i_person, j_shift] for j_shift in
                    shift_set.get_shift_indexes_on_day(-1, relative_shift=i_shift, intersection_set=constraint['Shift Indexes']))
                <= M * (1 - interB[i_shift, i_person])
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]
            constraint_scheduling += [
                assignments[i_person, i_shift] - interA[i_shift, i_person] - interB[i_shift, i_person] <= 0
                for i_shift in constraint['Shift Indexes']
                for i_person in constraint['Staff Indexes']
            ]

        # Fair Workload
        if constraint['Type'] == 8:

            precision_factor = 1000

            re = sum(shift_set.get_shifts(i_shift).workload for i_shift in constraint['Shift Indexes']) / \
                 sum(staff_set.get_person(i_person).desired_workload for i_person in constraint['Staff Indexes'])

            for i_person in constraint['Staff Indexes']:
                constraint_scheduling += [
                    int(precision_factor * re * (1 - constraint['x']))
                    <= sum(
                        assignments[i_person, i_shift] * int(precision_factor * shift_set.get_shifts(i_shift).workload / staff_set.get_person(i_person).desired_workload)
                        for i_shift in constraint['Shift Indexes']
                    )
                ]
                constraint_scheduling += [
                    sum(
                        assignments[i_person, i_shift] * int(precision_factor * shift_set.get_shifts(i_shift).workload / staff_set.get_person(i_person).desired_workload)
                        for i_shift in constraint['Shift Indexes']
                        )
                    <= int(precision_factor * re * (1 + constraint['x']))
                ]

    # ################ ADD CONSTRAINTS TO MODEL ################
    m.addConstrs(c for c in constraint_inherent)
    m.addConstrs(c for c in constraint_scheduling)

    time_build = time() - time_build_start

    # ################ SOLVE ################
    time_solve_start = time()
    m.optimize()
    time_solve = time() - time_solve_start

    # ################ OUTPUT ################
    output = dict()
    output['Total Time'] = time_build + time_solve
    output['Build Time'] = time_build
    output['Solve Time'] = time_solve

    if m.Status == 9:  # TIME LIMIT reached
        output['Satisfied'] = 'Timed_Out'

    elif m.Status == 2:
        output['Satisfied'] = True
        output['Assignments'] = list()
        for i_shift in range(len(shift_set)):
            try:
                output['Assignments'].append(next(i_person for i_person in range(len(staff_set))
                                                  if assignments[i_person, i_shift].x == 1))
            except:
                output['Assignments'].append(-1)
    elif m.Status == 3:
        output['Satisfied'] = False

    return output