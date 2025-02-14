# -------------------------------------------------- #
# Func to simulate a human-based decision pattern
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

import random
import numpy as np

from itertools import product, combinations
from activeclf.acquisition import sampling_fps
from scipy.spatial import distance_matrix


def random_sampler(indices_pool, n_points):
    """
    Sample n new points in a random fashion from the grid space.
    
    Parameters:
    - indices_pool: Indices of the grid space points.
    - n_points: Number of new points to sample
    
    Returns:
    - new_indices: Indices of the new points on the grid
    """

    return random.sample(indices_pool, n_points)


def coarse_grid_sampler(coordinates, n_points):
    """
    Sample n points from a regular grid such that they form a coarser grid.
    
    Parameters:
    - coordinates: Array of shape (Npoints, Dim) representing the regular grid
    - n: Number of points to sample
    
    Returns:
    - sampled_indices: Indices of the sampled points in the coordinates array
    - sampled_points: Array of the sampled points' coordinates
    """
    
    # 1. Get grid dimensions and unique values per dimension
    dims = coordinates.shape[1]
    unique_vals = [np.unique(coordinates[:, d]) for d in range(dims)]
    
    # 2. Calculate how many points per dimension
    points_per_dim = int(np.round(n_points ** (1/dims)))
    
    # 3. Calculate step size for each dimension
    indices = [np.linspace(0, len(uv)-1, points_per_dim, dtype=int) for uv in unique_vals]
    
    # 4. Create a coarse grid by selecting combinations of these indices
    coarse_indices = list(product(*indices))
    sampled_points = np.array([ [unique_vals[dim][idx] for dim, idx in enumerate(idx_tuple)] 
                               for idx_tuple in coarse_indices ])
    
    # 5. Find indices of the sampled points in the original grid
    sampled_indices = []
    for point in sampled_points:
        idx = np.where((coordinates == point).all(axis=1))[0]
        if len(idx) > 0:
            sampled_indices.append(idx[0])
    
    # 6. Limit to exactly n points (in case of rounding issues)
    sampled_indices = sampled_indices[:n_points]
    sampled_points = coordinates[sampled_indices]
    
    return sampled_indices, sampled_points


def midpoint_sampler(coordinates, starting_indices, starting_labels, n_points, min_dist):
    """
    Sample n new points in the 'middle' of the shortest distances between different classes.
    
    Parameters:
    - coordinates: Array of shape (M, D) representing grid coordinates
    - starting_indices: Array of indices of sampled points
    - starting_labels: Array of labels corresponding to the sampled points
    - n_points: Number of new points to sample
    - min_dist: ...
    
    Returns:
    - new_indices: Indices of the new points on the grid
    """

    # 1. Extract coordinates of the sampled points and N classes
    sampled_coords = coordinates[starting_indices]
    unique_classes = np.unique(starting_labels)

    # 2. Separate points by class
    class_points = {cls: sampled_coords[starting_labels == cls] for cls in unique_classes}

    # 3. Compute pairwise distances between all class pairs
    all_midpoints = []
    all_distances = []
    for (class_a, class_b) in combinations(unique_classes, 2):
        points_a = class_points[class_a]
        points_b = class_points[class_b]
        
        # Distance matrix between points in Class A and Class B
        dist_matrix = distance_matrix(points_a, points_b)
        
        # Find the shortest pairs
        min_indices = np.unravel_index(np.argsort(dist_matrix, axis=None), dist_matrix.shape)
        closest_pairs = list(zip(min_indices[0], min_indices[1]))
        
        # Calculate midpoints
        midpoints = [(points_a[i] + points_b[j]) / 2 for i, j in closest_pairs]
        distances = [dist_matrix[i,j] for i, j in closest_pairs]
        all_midpoints.extend(midpoints)
        all_distances.extend(distances)

    # 4. Select the N shortest midpoints (across all class pairs)
    all_midpoints = np.array(all_midpoints)
    all_distances = np.array(all_distances)

    # 5. First filtration on distances based on min dist parameter
    min_dist_filterd_indexes = np.where(all_distances >= min_dist)[0]
    all_midpoints_filtered = all_midpoints[min_dist_filterd_indexes]

    # 6. Second dist matrix to check distances from the sampled points
    dist_matrix_2 = distance_matrix(sampled_coords, all_midpoints_filtered)

    # 7. Second filtration based on radius of exclusion around midpoints from sampled coords
    valid_mid_points = []
    for i, dists in enumerate(dist_matrix_2.T):  # Transpose to loop over candidates
        if np.all(dists >= min_dist):
            valid_mid_points.append(i)

    all_midpoints_filtered_2 = all_midpoints_filtered[valid_mid_points]

    # 8. Sample from valid candidates
    if len(valid_mid_points) > n_points:
        fps_indx_from_valid_points = sampling_fps(X=all_midpoints_filtered_2, 
                                                  n=n_points)
        all_midpoints_filtered_3 = all_midpoints_filtered_2[fps_indx_from_valid_points]

    elif len(valid_mid_points) == n_points:
        all_midpoints_filtered_3 = all_midpoints_filtered_2

    elif len(valid_mid_points) < n_points:
        print(f'Warning, found only {len(valid_mid_points)}/{n_points} valid points for d={min_dist}')
        all_midpoints_filtered_3 = all_midpoints_filtered_2

    # 9. Assign closet grid point to sampled midpoints
    midpoint_distances = distance_matrix(coordinates, all_midpoints_filtered_3)
    closest_indices = np.argmin(midpoint_distances, axis=0)
    unique_indices = np.unique(closest_indices)
    
    return unique_indices

