from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm, ListedColormap, LinearSegmentedColormap
import seaborn as sns
import pandas as pd
import numpy as np


def create_colormap(cmap_colors):
    # Generate colormap
    norm_factor = 255
    cmap_color_norm = [[c[0] / norm_factor, c[1] / norm_factor, c[2] / norm_factor] for c in cmap_colors]
    steps = 100
    myColors = [(cmap_color_norm[curr_color][0] * (1 - c / steps) + cmap_color_norm[curr_color + 1][0] * c / steps,
                 cmap_color_norm[curr_color][1] * (1 - c / steps) + cmap_color_norm[curr_color + 1][1] * c / steps,
                 cmap_color_norm[curr_color][2] * (1 - c / steps) + cmap_color_norm[curr_color + 1][2] * c / steps,
                 1)
                for curr_color in range(len(cmap_colors) - 1)
                for c in range(steps)]
    color_map = LinearSegmentedColormap.from_list('Custom', myColors, len(myColors))

    return color_map


def save_heatmap(name, x_data, y_data, z_data, x_label, y_label, absolute_ticks=False, satisfiability=None, mark_unsat=False, print_unsat=True):

    # Set ticks to be absolute
    if absolute_ticks:
        # Add None to x/y values with no z-value
        missing_data_positions = [(x, y)
                                  for x in range(min(x_data), max(x_data) + 1)
                                  for y in range(min(y_data), max(y_data) + 1)
                                  if not any(x_data[i] == x and y_data[i] == y for i in range(len(x_data)))]
        x_addon = [pos[0] for pos in missing_data_positions]
        y_addon = [pos[1] for pos in missing_data_positions]
        z_addon = [None for pos in missing_data_positions]
    else:
        x_addon = list()
        y_addon = list()
        z_addon = list()

    # Set all unsat cell values to none so that they don't print
    if not print_unsat and satisfiability is not None:
        for i_sat, sat in enumerate(satisfiability):
            if not sat:
                z_data[i_sat] = None

    # Create heatmap
    fig, ax = plt.subplots(figsize=(8, 5))
    data = pd.DataFrame(data={'x': x_data + x_addon,
                              'y': y_data + y_addon,
                              'z': z_data + z_addon})
    data = data.pivot(columns='x', index='y', values='z')
    sns.heatmap(data)  # , cmap=cm.get_cmap('viridis'))
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.gca().invert_yaxis()

    # Add marks on unsat cells if printing and marking unsat cells is true
    if satisfiability is not None and print_unsat and mark_unsat:
        for i_sat, sat in enumerate(satisfiability):
            if not sat:
                x_pos = data.columns.get_loc(x_data[i_sat])
                y_pos = data.index.get_loc(y_data[i_sat])
                ax.add_patch(plt.Rectangle((x_pos, y_pos), 1, 1, ec='mediumturquoise', fc='none', lw=1, hatch='//'))

    # Save figure
    plt.savefig(name, dpi=600)
    plt.close()


def comparison_heatmap(name, x_data, y_data, z_data, method1_status, method2_status, x_label, y_label, cb_label, vminmax=None):

    # Params
    color_map = 'viridis'
    cmap_colors = [[0, 0, 0],
                   [0, 91, 128],
                   [158, 0, 186],
                   [245, 102, 0],
                   [255, 255, 255]
                   ]
    #color_map = create_colormap(cmap_colors)
    color_map = plt.get_cmap(color_map)
    color_map = ListedColormap(color_map(np.linspace(0.1, 1, 100)))

    method1_only_color = 'black'
    method2_only_color = 'tomato'
    unsat_color = 'white'

    # Remove data if either SMT or MILP timed out
    edited_z_data = z_data.copy()
    for i_status, _ in enumerate(method1_status):
        if method1_status[i_status] == 'Timed_Out' or method2_status[i_status] == 'Timed_Out':
            edited_z_data[i_status] = None

    # Create heatmap
    fig, ax = plt.subplots(figsize=(5, 4))
    plt.rcParams.update({'mathtext.default': 'regular'})
    data = pd.DataFrame(data={'x': x_data,
                              'y': y_data,
                              'z': edited_z_data})
    data = data.pivot(columns='x', index='y', values='z')
    if vminmax is None:
        sns.heatmap(data, cmap=cm.get_cmap(color_map), cbar_kws={'label': cb_label})
    else:
        sns.heatmap(data, cmap=cm.get_cmap(color_map), cbar_kws={'label': cb_label},
                    vmin=vminmax[0], vmax=vminmax[1])
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.gca().invert_yaxis()

    # Add colors for only one timed out
    for i_status, _ in enumerate(method1_status):
        if not method1_status[i_status] == 'Timed_Out' and method2_status[i_status] == 'Timed_Out':
            x_pos = data.columns.get_loc(x_data[i_status])
            y_pos = data.index.get_loc(y_data[i_status])
            ax.add_patch(plt.Rectangle((x_pos, y_pos), 0.98, 1, fc=method1_only_color))
        if method1_status[i_status] == 'Timed_Out' and not method2_status[i_status] == 'Timed_Out':
            x_pos = data.columns.get_loc(x_data[i_status])
            y_pos = data.index.get_loc(y_data[i_status])
            ax.add_patch(plt.Rectangle((x_pos, y_pos), 0.98, 1, fc=method2_only_color))

    # Add marks on unsat cells if printing and marking unsat cells is true
    for i_status, _ in enumerate(method1_status):
        if method1_status[i_status] == False or method2_status[i_status] == False:
            x_pos = data.columns.get_loc(x_data[i_status]) - 0.02
            y_pos = data.index.get_loc(y_data[i_status])
            ax.add_patch(plt.Rectangle((x_pos, y_pos), 1, 1, ec=unsat_color, fc='none', lw=1, hatch='//'))

    # Save figure
    plt.savefig(name + '.png', dpi=600)
    plt.close()


def ranking_heatmap(name, x_data, y_data, z_data, method1_status, method2_status, x_label, y_label, color_labels):

    # Params
    unsat_color = 'white'
    color_map = 'viridis'
    color_map = cm.get_cmap(color_map)
    cmap_colors = [[0, 107, 145],
                   [240, 240, 240],
                   [204, 227, 0]
                   ]
    color_map = create_colormap(cmap_colors)
    color_map = ListedColormap(color_map(np.linspace(0, 1, 3)))

    # Create heatmap
    fig, ax = plt.subplots(figsize=(5, 4))
    data = pd.DataFrame(data={'x': x_data,
                              'y': y_data,
                              'z': z_data})
    data = data.pivot(columns='x', index='y', values='z')

    hm = sns.heatmap(data, cmap=cm.get_cmap(color_map), cbar_kws={'ticks': [-1, 0, 1]}, vmin=-1, vmax=1)
    cbar = hm.collections[0].colorbar
    cbar.set_ticklabels(color_labels)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.gca().invert_yaxis()

    # Add marks on unsat cells if printing and marking unsat cells is true
    for i_status, _ in enumerate(method1_status):
        if method1_status[i_status] == False or method2_status[i_status] == False:
            x_pos = data.columns.get_loc(x_data[i_status]) - 0.02
            y_pos = data.index.get_loc(y_data[i_status])
            ax.add_patch(plt.Rectangle((x_pos, y_pos), 1, 1, ec=unsat_color, fc='none', lw=1, hatch='//'))

    # Save figure
    plt.savefig(name + '.png', dpi=600)
    plt.close()


def time_heatmap(name, x_data, y_data, z_data, status, x_label, y_label, vminmax=None):

    # Params
    color_map = 'GnBu_r'
    unsat_color = 'white'
    cmap_colors = [[41, 69, 69],
                   [78, 179, 179],
                   [151, 215, 215],
                   [224, 250, 250]
                   ]

    #color_map = create_colormap(cmap_colors)

    # Remove data if either SMT or MILP timed out
    edited_z_data = z_data.copy()
    for i_status, _ in enumerate(status):
        if status[i_status] == 'Timed_Out':
            edited_z_data[i_status] = None

    # Create heatmap
    fig, ax = plt.subplots(figsize=(5, 4))
    data = pd.DataFrame(data={'x': x_data,
                              'y': y_data,
                              'z': edited_z_data})
    data = data.pivot(columns='x', index='y', values='z')

    if vminmax is None:
        sns.heatmap(data, cmap=cm.get_cmap(color_map), cbar_kws={'label': 'Solver Time [s]'}, norm=LogNorm())
    else:
        sns.heatmap(data, cmap=cm.get_cmap(color_map), cbar_kws={'label': 'Solver Time [s]'}, norm=LogNorm(vmin=vminmax[0], vmax=vminmax[1]))

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.gca().invert_yaxis()

    # Add marks on unsat cells if printing and marking unsat cells is true
    for i_status, _ in enumerate(status):
        if status[i_status] == False:
            x_pos = data.columns.get_loc(x_data[i_status]) - 0.02
            y_pos = data.index.get_loc(y_data[i_status])
            ax.add_patch(plt.Rectangle((x_pos, y_pos), 1, 1, ec=unsat_color, fc='none', lw=1, hatch='//'))

    # Save figure
    plt.savefig(name + '.png', dpi=600)
    plt.close()