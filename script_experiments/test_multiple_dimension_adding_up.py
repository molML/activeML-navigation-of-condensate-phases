import itertools
import numpy as np
import pandas as pd

# Step 1: Define the ranges for the original variables
range_x = np.arange(0.1,8.1,0.1)
range_y = np.arange(0.1,8.1,0.1)

# Create all combinations of x, y, and z
combinations_xyz = list(itertools.product(range_x, range_y))

# Step 2: Define the step size and maximum sum for a, b, c
step = 100  # Define the step size
max_sum = 2000  # Maximum allowed sum for a, b, and c

# Generate the range for a, b, and c using frange function
def frange(start, stop, step):
    """Generates a range of floating-point numbers."""
    while start <= stop:
        yield round(start, 10)
        start += step

range_a = [i for i in frange(0, max_sum, step)]
range_b = range_a
range_c = range_a

# Step 3: Generate valid combinations for a, b, and c
combinations_abc = []
for a in range_a:
    for b in range_b:
        for c in range_c:
            if a + b + c <= max_sum:  # Check the sum condition
                combinations_abc.append((a, b, c))

# Step 4: Combine the two sets of combinations
combined_combinations = [
    (*xyz, *abc)
    for xyz in combinations_xyz
    for abc in combinations_abc
]

# Step 5: Create a DataFrame from the combined combinations
df = pd.DataFrame(combined_combinations, columns=['x', 'y', 'a', 'b', 'c'])

# Display the resulting DataFrame
print(df)
