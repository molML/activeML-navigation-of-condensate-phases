# -------------------------------------------------- #
# Functions for plotting results
#
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import plotly.graph_objects as go
from typing import Tuple, List, Union

# -------------------------------------------------- #
# --- FIG & AXES

# -- Set Fig and Axes
def get_axes(plots: int, 
             max_col: int =2, 
             fig_frame: tuple =(3.3,3.), 
             res: int =200) -> Tuple[Figure, Axes]:
    """Define Fig and Axes objects.

    :param plots: number of plots frames in a fig.
    :type plots: int
    :param max_col: number of columns to arrange the frames, defaults to 2
    :type max_col: int, optional
    :param fig_frame: frame size, defaults to (3.3,3.)
    :type fig_frame: tuple, optional
    :param res: resolution, defaults to 200
    :type res: int, optional
    :return: fig and axes object from matplotlib.
    :rtype: _type_
    """
    # cols and rows definitions
    cols = plots if plots <= max_col else max_col
    rows = int(plots / max_col) + int(plots % max_col != 0)

    fig, axes = plt.subplots(rows,
                             cols,
                             figsize=(cols * fig_frame[0], rows * fig_frame[1]),
                             dpi=res)
    # beauty
    if plots > 1:
        axes = axes.flatten()
        for i in range(plots, max_col*rows):
            remove_frame(axes[i])
    elif plots == 1:
        pass
    
    return fig, axes


# -- Remove frame
def remove_frame(axes):
    for side in ['bottom', 'right', 'top', 'left']:
        axes.spines[side].set_visible(False)
    axes.set_yticks([])
    axes.set_xticks([])
    axes.xaxis.set_ticks_position('none')
    axes.yaxis.set_ticks_position('none')
    pass


# -------------------------------------------------- #
# --- PDF & Entropy plots

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import scipy
from scipy.interpolate import griddata

CMAPS = ['Reds', 'Blues', 'Greens', 'Purples', 'Oranges']
COLOURS = ['red', 'blue', 'green', 'purple', 'orange']


def ensure_min_max(array, desired_min, desired_max):
    """
    Ensures that the array has the desired minimum and maximum values,
    ignoring NaN values. If they are not present, it corrects them by 
    replacing the first occurrence of the current min/max.

    Parameters:
    - array (np.ndarray): The 2D array to check and correct.
    - desired_min (int/float): The desired minimum value.
    - desired_max (int/float): The desired maximum value.

    Returns:
    - np.ndarray: The corrected array.
    """
    
    # Find the current min and max values in the array, ignoring NaN values
    current_min = np.nanmin(array)
    current_max = np.nanmax(array)
    
    # Find the locations of the current minimum and maximum values, ignoring NaN values
    min_positions = np.argwhere(array == current_min)
    max_positions = np.argwhere(array == current_max)
    
    # Correct if the minimum value is not the desired one
    if current_min != desired_min:
        # Replace the first min position with the desired min value
        min_position_to_replace = min_positions[0]  # Pick the first occurrence
        array[min_position_to_replace[0], min_position_to_replace[1]] = desired_min
        print(f"Min value corrected at position {min_position_to_replace}")
    
    # Correct if the maximum value is not the desired one
    if current_max != desired_max:
        # Replace the first max position with the desired max value
        max_position_to_replace = max_positions[0]  # Pick the first occurrence
        array[max_position_to_replace[0], max_position_to_replace[1]] = desired_max
        print(f"Max value corrected at position {max_position_to_replace}")
    
    return array


def get_alphas(pdf: np.ndarray, 
               scale: bool=False, 
               treshold: float=.50001) -> np.ndarray:
    alphas = (pdf.ravel() - pdf.ravel().min()) / (pdf.ravel().max() - pdf.ravel().min())
    if scale:
        for i,av in enumerate(alphas):
            if av <= treshold:
                alphas[i] = 0.
            else:
                pass
    return alphas


def plot2D_pdfsurfaceplot(df: pd.DataFrame,
                       pdf: np.ndarray,
                       var1: str,
                       var2: str,
                       screened_points_ndx: List[int],
                       new_points_ndx: List[int],
                       show_points: bool,
                       axis: Axes) -> None:
    
    X = df[var1]
    Y = df[var2]
    labels = df['Phase'].to_numpy()

    masked_2d_plane_index = df.index.to_numpy()

    # show the points
    if show_points:
        surface_edges = .3
        # compute the intersection between the screened and the plane indexes
        intersection_screened = list(set(masked_2d_plane_index) & set(screened_points_ndx))
        if len(intersection_screened) > 0:
            screened_labels = labels[np.array(intersection_screened).astype(int)]
            axis.scatter(X[intersection_screened], Y[intersection_screened], 
                         s=50,
                         c=np.array(COLOURS)[screened_labels], marker='o', edgecolors='0.', zorder=5)
            
        intersection_newpoints = list(set(masked_2d_plane_index) & set(new_points_ndx))
        if len(intersection_newpoints) > 0:
            axis.scatter(X[intersection_newpoints], Y[intersection_newpoints], 
                         s=50,
                         c='1.', marker='o', edgecolors='0.', zorder=6)
    else:
        surface_edges = .0

    for phase in range(pdf.shape[1]):

        # Determine the range for X and Y
        x_min, x_max = X.min()-surface_edges, X.max()+surface_edges
        y_min, y_max = Y.min()-surface_edges, Y.max()+surface_edges

        Z = pdf[masked_2d_plane_index, phase]

        # Generate a grid and interpolate the diffusion coefficients
        bins=100j
        grid_x, grid_y = np.mgrid[x_min:x_max:bins, y_min:y_max:bins]
        grid_z = griddata((X, Y), Z, (grid_x, grid_y), method='linear')

        grid_z = np.round(grid_z, decimals=4)

        contours = axis.contour(grid_x, grid_y, grid_z, 
                                levels=[.53, .7, .8, .9, .97, 1.], colors='.0', 
                                vmin=0., vmax=1.)
        axis.clabel(contours, inline=True, fontsize=5, fmt='%1.2f')

        contourfs = axis.contourf(grid_x, grid_y, grid_z, 
                                levels=[.53, .7, .8, .9, .97, 1.], cmap=CMAPS[phase], 
                                vmin=0., vmax=1.,)
        
        if phase == 0:
            boundary = axis.contour(grid_x, grid_y, grid_z, 
                                    levels=[.50], linestyles='-.')

        axis.set_xlabel(var1)
        axis.set_ylabel(var2)


MAX_ENTROPY = {
    2 : scipy.stats.entropy(pk=[.5,.5], axis=0),
    3 : scipy.stats.entropy(pk=[.3333,.3333,3333], axis=0),
    4 : scipy.stats.entropy(pk=[.25,.25,.25,.25], axis=0),
    5 : scipy.stats.entropy(pk=[.20,.20,.20,.20,.20], axis=0)
}


def plot2D_entropysurfaceplot(df: pd.DataFrame,
                       pdf: np.ndarray,
                       var1: str,
                       var2: str,
                       screened_points_ndx: List[int],
                       new_points_ndx: List[int],
                       show_points: bool,
                       axis: Axes) -> None:
    
    X = df[var1]
    Y = df[var2]
    labels = df['Phase'].to_numpy()

    masked_2d_plane_index = df.index.to_numpy()

    # show the points
    if show_points:
        surface_edges = .3
        # compute the intersection between the screened and the plane indexes
        intersection_screened = list(set(masked_2d_plane_index) & set(screened_points_ndx))
        if len(intersection_screened) > 0:
            screened_labels = labels[np.array(intersection_screened).astype(int)]
            axis.scatter(X[intersection_screened], Y[intersection_screened], 
                         s=50,
                         c=np.array(COLOURS)[screened_labels], marker='o', edgecolors='0.', zorder=5)
            
        intersection_newpoints = list(set(masked_2d_plane_index) & set(new_points_ndx))
        if len(intersection_newpoints) > 0:
            axis.scatter(X[intersection_newpoints], Y[intersection_newpoints], 
                         s=50,
                         c='1.', marker='o', edgecolors='0.', zorder=6)
    else:
        surface_edges = .0

    # Determine the range for X and Y
    x_min, x_max = X.min()-surface_edges, X.max()+surface_edges
    y_min, y_max = Y.min()-surface_edges, Y.max()+surface_edges

    Z = pdf[masked_2d_plane_index, :]
    H = np.around(scipy.stats.entropy(pk=Z, axis=1), 4)

    n_phases = Z.shape[1]

    # Generate a grid and interpolate the diffusion coefficients
    bins=100j
    grid_x, grid_y = np.mgrid[x_min:x_max:bins, y_min:y_max:bins]

    grid_z = griddata((X, Y), Z[:, 0], (grid_x, grid_y), method='linear')

    grid_h = griddata((X, Y), H, (grid_x, grid_y), method='linear')
    grid_h = np.round(grid_h, decimals=5)

    contours = axis.contour(grid_x, grid_y, grid_h, 
                            levels=np.linspace(0,MAX_ENTROPY[n_phases]+.1, 7), colors='.0', 
                            vmin=.0, vmax=MAX_ENTROPY[n_phases])
    axis.clabel(contours, inline=True, fontsize=5, fmt='%1.2f')

    contourfs = axis.contourf(grid_x, grid_y, grid_h, 
                            levels=np.linspace(0,MAX_ENTROPY[n_phases]+.1, 7), cmap='plasma', 
                            vmin=.0, vmax=MAX_ENTROPY[n_phases])
    
    boundary = axis.contour(grid_x, grid_y, grid_z, 
                            levels=[.50], linestyles='-.')

    axis.set_xlabel(var1)
    axis.set_ylabel(var2)
    

def plot3D_surface_volume_landscape(df, pdf, show_surfaces=False):

    fig = go.Figure()

    fig.add_trace(go.Volume(
        x=df.to_numpy()[:,0],
        y=df.to_numpy()[:,1],
        z=df.to_numpy()[:,2],
        value=pdf[:,1],
        isomin=0.0,
        isomax=1.0,
        opacity=1.0, # needs to be small to see through all surfaces
        opacityscale=[[0.0, 0.5], [0.40, 0.3], [0.45, 0.1], [0.50, 0.0], [0.55, 0.1], [0.6, 0.3], [1., 1.]],
        surface_count=11, # needs to be a large number for good volume rendering
        colorscale='RdBu',
        showscale=False,
        # caps= dict(x_show=True, y_show=True, z_show=True, x_fill=1),
        ))

    if show_surfaces:
        fig.add_trace(go.Isosurface(
            x=df.to_numpy()[:,0],
            y=df.to_numpy()[:,1],
            z=df.to_numpy()[:,2],
            value=pdf[:,1],
            isomin=0.0,
            isomax=1.0,
            colorscale='RdBu',
            surface_count=11, # number of isosurfaces, 2 by default: only min and max
            colorbar_nticks=8, # colorbar ticks correspond to isosurface values
            caps=dict(x_show=False, y_show=False),
            showscale=False,
            ))

    fig.update_layout(
        scene_camera_center=dict(x=0, y=0, z=0),  # Focus on the center
        margin=dict(t=0, l=0, b=0, r=0),  # Tight margins
        scene=dict(aspectmode='cube'),  # Equal aspect ratio for centering
        scene_camera_eye=dict(x=1.6, y=1.4, z=0.075)
    )

    return fig