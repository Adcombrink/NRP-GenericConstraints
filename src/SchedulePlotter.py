import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import random


def plot_schedule(problem, solution):

    plt.figure(figsize=(12, 6))

    # Get colors for each shift type
    type_color = dict()
    for shift_type in set([shift.type for shift in problem['Shift Set']]):
        if shift_type not in type_color.keys():
            type_color[shift_type] = [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 0.5]

    # Plot shift rectangles
    for i_shift, shift in enumerate(problem['Shift Set']):

        x = shift.start_tick / 24
        width = (shift.end_tick - shift.start_tick) / 24
        height = 0.5
        # y = solution['Assignments'][i_shift] - height/2
        y = solution['Assignments'][i_shift] - random.uniform(0, 1) * height/2
        rectangle = plt.Rectangle((x,y), width, height, fc=type_color[shift.type], ec='black')
        plt.annotate(shift.type, (x + width/2, y + height/2), color='black', fontsize=6, ha='center', va='center')
        plt.gca().add_patch(rectangle)

    # Plot legend
    legend_handles = list()
    for shift_type in type_color.keys():
        legend_handles.append(mpatches.Patch(color=type_color[shift_type], label=shift_type))
    plt.legend(handles=legend_handles)

    # Misc plotting things
    plt.xticks(list(range(max([int(s.end_tick/24)+2 for s in problem['Shift Set']]))))
    plt.yticks(list(range(len(problem['Staff Set']))), [person.name for person in problem['Staff Set']])
    plt.ylim(-0.5, len(problem['Staff Set'])-0.5)

    #plt.axis('scaled')
    plt.grid(True, axis='x')
    plt.show()