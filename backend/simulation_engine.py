import numpy as np

def get_neighbors(r, c, rows, cols):
    """
    Returns valid 4-connectivity neighbors (up, down, left, right).
    """
    neighbors = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            neighbors.append((nr, nc))
    return neighbors

def simulate_water(grid, elevation, steps=10):
    """
    Simulates flood water flow on a 2D grid.
    
    Args:
        grid (np.ndarray): 2D array of initial water levels.
        elevation (np.ndarray): 2D array of surface elevation.
        steps (int): Number of simulation steps to run.
        
    Returns:
        np.ndarray: Updated water grid after simulation.
    """
    water_grid = grid.astype(float).copy()
    elevation_grid = elevation.astype(float)
    rows, cols = water_grid.shape
    
    for _ in range(steps):
        new_water_grid = water_grid.copy()
        
        for r in range(rows):
            for c in range(cols):
                current_water = water_grid[r, c]
                if current_water <= 0:
                    continue
                
                current_total = elevation_grid[r, c] + current_water
                neighbors = get_neighbors(r, c, rows, cols)
                
                # Identify lower neighbors (based on total height: elevation + water)
                lower_neighbors = []
                for nr, nc in neighbors:
                    neighbor_total = elevation_grid[nr, nc] + water_grid[nr, nc]
                    if neighbor_total < current_total:
                        lower_neighbors.append((nr, nc))
                
                if lower_neighbors:
                    # Distribute 25% of current water among lower neighbors
                    dist_amount = current_water * 0.25
                    amount_per_neighbor = dist_amount / len(lower_neighbors)
                    
                    new_water_grid[r, c] -= dist_amount
                    for nr, nc in lower_neighbors:
                        new_water_grid[nr, nc] += amount_per_neighbor
        
        water_grid = new_water_grid
        
    return water_grid

if __name__ == "__main__":
    # Example usage:
    size = 5
    elev = np.zeros((size, size))
    # Create a simple slope
    for i in range(size):
        elev[i, :] = size - i 
        
    water = np.zeros((size, size))
    water[0, 2] = 10.0 # Add water at the top
    
    print("Initial Water Grid:")
    print(water)
    
    final_water = simulate_water(water, elev, steps=5)
    
    print("\nWater Grid after 5 steps:")
    print(np.round(final_water, 2))
