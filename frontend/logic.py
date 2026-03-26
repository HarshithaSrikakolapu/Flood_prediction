import numpy as np
from typing import List

def calculate_refined_risk(rainfall: float, river_level: float, soil_moisture: float, elevation: float) -> dict:
    # 1/elevation safeguard (minimum 0.1 to avoid extreme values)
    inv_elevation = 1.0 / max(0.1, elevation)
    
    # Weighted formula: 0.4*R + 0.3*L + 0.2*S + 0.1*(1/E)
    # Note: This assumes inputs are already in a reasonable scale or 0-1 range.
    # We will compute and then normalize/cap the output between 0 and 1.
    score = (0.4 * rainfall) + (0.3 * river_level) + (0.2 * soil_moisture) + (0.1 * inv_elevation)
    
    # Normalize/Cap between 0 and 1
    # Assuming the formula is meant to be self-scaling if inputs are 0-1.
    # We'll just cap it for safety.
    risk_score = float(max(0.0, min(1.0, score)))
    
    # Risk Classification: LOW (<0.3), MEDIUM (0.3-0.7), HIGH (>0.7)
    if risk_score > 0.7:
        level = "HIGH"
    elif risk_score >= 0.3:
        level = "MEDIUM"
    else:
        level = "LOW"
        
    return {
        "risk_score": risk_score,
        "risk_level": level
    }

def simulate_water_flow(elevation_grid: List[List[float]], initial_water_level: float, rainfall: float, steps: int = 10) -> List[List[List[float]]]:
    elev = np.array(elevation_grid)
    rows, cols = elev.shape
    water = np.zeros_like(elev) + initial_water_level + (rainfall / 10.0) # simplify rainfall to water height
    
    history = [water.copy().tolist()]
    
    for _ in range(steps):
        new_water = water.copy()
        # Simple flow: water moves from higher total (elev + water) to lower total
        for r in range(rows):
            for c in range(cols):
                if water[r, c] <= 0: continue
                
                # Check neighbors
                best_neighbor = None
                min_total = elev[r, c] + water[r, c]
                
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        neighbor_total = elev[nr, nc] + water[nr, nc]
                        if neighbor_total < min_total:
                            min_total = neighbor_total
                            best_neighbor = (nr, nc)
                
                if best_neighbor:
                    flow_amount = min(water[r, c], (elev[r, c] + water[r, c] - min_total) / 2.0)
                    new_water[r, c] -= flow_amount
                    new_water[best_neighbor[0], best_neighbor[1]] += flow_amount
        
        water = new_water
        history.append(water.copy().tolist())
        
    return history
