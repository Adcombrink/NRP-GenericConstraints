from itertools import chain, combinations, permutations


class Shift:
    def __init__(self, type, start_day, start_hour, duration, burden, qualification_requirements):
        self.type = type
        self.start_day = start_day
        self.start_hour = start_hour
        self.duration = duration
        self.burden = burden
        self.qualification_requirements = qualification_requirements

        self.start_tick = start_day*24 + start_hour
        self.end_tick = self.start_tick + self.duration
        self.workload = self.burden * self.duration
        self.qualified_staff = list()
        self.index = None

    def __str__(self):
        if self.index is None:
            return 'Day {} Hour {} {}'.format(self.start_day, self.start_hour, self.type)
        else:
            return '{}: Day {} Hour {} {}'.format(self.index, self.start_day, self.start_hour, self.type)

    def set_index(self, index):
        self.index = index

    def set_qualified_personnel(self, staff_set):
        for person in staff_set:
            if set(self.qualification_requirements).issubset(set(person.qualifications)):
                self.qualified_staff.append(person.index)


class ShiftSet:
    def __init__(self, shift_list=None):
        if shift_list is None:
            self.shifts = list()
        else:
            self.shifts = shift_list

    def __iter__(self):
        self.iter_num = 0
        return self

    def __next__(self):
        if self.iter_num >= len(self.shifts):
            raise StopIteration
        else:
            self.iter_num += 1
        return self.shifts[self.iter_num - 1]

    def __len__(self):
        return len(self.shifts)

    def add_shift(self, shift):
        shift.set_index(len(self.shifts))
        self.shifts.append(shift)

    def get_start_day_set(self):
        return set([shift.start_day for shift in self.shifts])

    def get_qualifications_set(self):
        return set([q for shift in self.shifts for q in shift.qualification_requirements])

    def get_overlapping_combinations(self):

        # Get all ticks (start and end tick) for each shift
        ticks = list()
        for iShift, shift in enumerate(self.shifts):
            ticks.append([iShift, shift.start_tick, 'Start'])
            ticks.append([iShift, shift.end_tick, 'End'])

        # Group ticks that are the same
        unique_ticks = sorted(set([tick[1] for tick in ticks]))
        tick_groups = [[t for t in ticks if t[1] == unique_tick] for unique_tick in unique_ticks]

        # Use the tick groups to define the sets of overlapping shifts
        overlapping_set = list()
        current_overlap = set()
        for iGroup, group in enumerate(tick_groups):
            for tick in group:
                if tick[2] == 'Start':
                    current_overlap.update(set([tick[0]]))
                elif tick[2] == 'End':
                    current_overlap = current_overlap.difference(set([tick[0]]))
            if sorted(current_overlap) not in overlapping_set:
                overlapping_set.append(sorted(current_overlap))

        # Get all overlapping shift permutations (Ex. 3 overlapping shifts have 4 combinations with >= 2 shifts)
        overlapping_combinations = list()
        for overlap in overlapping_set:
            if len(overlap) == 2:
                overlapping_combinations.append(overlap)
            elif len(overlap) > 2:
                overlap_powerset = chain.from_iterable(combinations(overlap, r)
                                                       for r in range(len(overlap) + 1))
                overlapping_combinations += [list(combo) for combo in overlap_powerset
                                             if len(combo) >= 2 and list(combo) not in overlapping_combinations]

        """
        output = list()
        for combo in overlapping_combinations:
            allowed_people = set()
            for allowed_overlap in shift_overlap:
                if len(combo) == len(allowed_overlap['Shift Indexes']):
                    perms = list(permutations(range(len(combo))))
                    for p in perms:
                        temp = [combo[p[i]] in allowed_overlap['Shift Indexes'][i] for i in range(len(p))]
                        if all(temp):
                            allowed_people.update(allowed_overlap['Staff Indexes'])
                            break

            output.append([combo, allowed_people])

        return output
        """

        return overlapping_combinations

    def set_shift_qualified_personnel(self, staff_set):
        for shift in self.shifts:
            shift.set_qualified_personnel(staff_set)

    def get_shifts(self, indexes=None):
        if indexes is None:
            return self.shifts
        elif type(indexes) is int:
            return self.shifts[indexes]

    def get_shift_indexes_on_day(self, days, relative_shift=None, intersection_set=None):

        # Determine if this is for all shifts or only for a certain set of shifts
        shift_pool = range(len(self.shifts)) if intersection_set is None else intersection_set

        if type(days) is int:
            days = [days]

        # Adjust days if relative to a shift
        days = days if relative_shift is None else [self.shifts[relative_shift].start_day + day for day in days]

        shift_indexes = list(set(i_shift for i_shift in shift_pool if self.shifts[i_shift].start_day in days))
        return shift_indexes

    def get_shift_indexes_of_type(self, shift_types, intersection_set=None):

        if intersection_set is None:
            intersection_set = [shift.index for shift in self.shifts]

        if type(shift_types) is not list:
            shift_types = [shift_types]

        types = set(shift_type.type if type(shift_type) is Shift else shift_type for shift_type in shift_types)

        return [i_shift for i_shift in intersection_set if self.shifts[i_shift].type in types]

    def get_all_shift_indexes(self):
        return list(range(len(self.shifts)))


class Person:
    def __init__(self, name, desired_workload, qualifications):
        self.name = name
        self.desired_workload = desired_workload
        self.qualifications = qualifications
        self.index = None

    def __str__(self):
        if self.index is None:
            return '{}'.format(self.name)
        else:
            return '{}: {}'.format(self.index, self.name)

    def set_index(self, index):
        self.index = index


class StaffSet:
    def __init__(self, person_list=None):
        if person_list is None:
            self.staff = list()
        else:
            self.staff = person_list

    def __iter__(self):
        self.iter_num = 0
        return self

    def __next__(self):
        if self.iter_num >= len(self.staff):
            raise StopIteration
        else:
            self.iter_num += 1
        return self.staff[self.iter_num - 1]

    def __len__(self):
        return len(self.staff)

    def add_person(self, person):
        person.set_index(len(self.staff))
        self.staff.append(person)

    def get_person(self, indexes=None):
        if indexes is None:
            return self.staff
        elif type(indexes) is int:
            return self.staff[indexes]

    def get_person_index(self, some_names):

        if type(some_names) is str:
            names = [some_names]
        elif type(some_names) is list:
            names = some_names
        else:
            raise Exception('Wrong format as input argument. Only str or list.')

        person_indexes = list()
        for i_person, person in enumerate(self.staff):
            if person.name in names:
                person_indexes.append(i_person)

        return person_indexes

    def get_all_person_indexes(self):
        return [person.index for person in self.staff]

    def get_qualifications_set(self):
        return set([q for person in self.staff for q in person.qualifications])

    def get_staff_indexes_with_qualifications(self, qualifications):
        if type(qualifications) is str:
            qualifications = [qualifications]

        staff_indexes = [person.index
                         for person in self.staff
                         if all(quali in person.qualifications for quali in qualifications)]

        return staff_indexes


class OverlapCombination:
    def __init__(self, shift_indexes, staff_indexes=None):
        self.shift_indexes = shift_indexes
        if staff_indexes is None:
            self.staff_indexes = list()
        elif staff_indexes is list:
            self.staff_indexes = staff_indexes
        else:
            self.staff_indexes = [staff_indexes]

    def __str__(self):
        return 'Shifts {}     Staff {}'.format(self.shift_indexes, self.staff_indexes)

    def add_staff_indexes(self, staff_indexes):
        if type(staff_indexes) is int:
            self.staff_indexes.append(staff_indexes)
        elif type(staff_indexes) is list:
            self.staff_indexes += staff_indexes


class OverlapSet:
    def __init__(self, shift_set):
        self.overlap_combinations = list()
        for combo in shift_set.get_overlapping_combinations():
            #  if len(combo) == 2:
            self.overlap_combinations.append(OverlapCombination(combo))

    def __iter__(self):
        self.iter_num = 0
        return self

    def __next__(self):
        if self.iter_num >= len(self.overlap_combinations):
            raise StopIteration
        else:
            self.iter_num += 1
        return self.overlap_combinations[self.iter_num - 1]

    def __len__(self):
        return len(self.overlap_combinations)

    def add_allowed_personnel(self, shift_indexes, staff_indexes, include_permutations=False):
        for combo in self.overlap_combinations:
            if include_permutations:
                if set(combo.shift_indexes).issubset(set(shift_indexes)):
                    combo.add_staff_indexes(staff_indexes)
            else:
                if set(combo.shift_indexes) == set(shift_indexes):
                    combo.add_staff_indexes(staff_indexes)

    def get_overlap(self, indexes=None):
        if indexes is None:
            return self.overlap_combinations
        elif type(indexes) is int:
            return self.overlap_combinations[indexes]


