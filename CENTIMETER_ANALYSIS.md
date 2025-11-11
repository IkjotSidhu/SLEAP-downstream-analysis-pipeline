# 📏 Centimeter Distance Analysis Enhancement

## Overview

The SLEAP analysis pipeline has been enhanced to generate distance plots and CSV exports using **centimeters** in addition to pixels. This provides biologically meaningful distance measurements by converting pixel coordinates to real-world units based on your experimental arena dimensions.

## 🆕 New Features

### 1. **Automatic Pixel-to-Centimeter Conversion**
- Calculates conversion factor based on arena dimensions (default: 11" × 11")
- Uses the full range of animal movement to estimate pixel density
- Conversion factor: `cm_per_pixel = arena_size_cm / pixel_range`

### 2. **Enhanced CSV Outputs**
All distance-related CSV files now include both pixel and centimeter measurements:

#### Frame-by-Frame Data
- `inter_mouse_distance_pixels` ← Original pixel distances
- `inter_mouse_distance_cm` ← **NEW: Centimeter distances**
- `mouse1_frame_distance_pixels` ← Original pixel distances  
- `mouse1_frame_distance_cm` ← **NEW: Centimeter distances**
- `mouse1_cumulative_distance_pixels` ← Original cumulative pixels
- `mouse1_cumulative_distance_cm` ← **NEW: Cumulative centimeters**

#### Time-Aggregated Data
Both per-second and per-minute CSV files now include statistics for centimeter measurements:
- `inter_mouse_distance_cm_mean/std/min/max/count`
- `mouse1_frame_distance_cm_sum/mean/count`
- `mouse1_cumulative_distance_cm_last`

### 3. **Additional Visualizations**
New PDF plots generated in centimeters:
- `{node}_Inter-Mouse-Distance-by-Frame-CM.pdf`
- `{node}_Inter-Mouse-Distance-by-second-CM.pdf` 
- `Cumulative-distance-over-time-{node}-CM.pdf`

## 🎯 Usage

### Basic Usage with Default Arena Size (11" × 11")
```python
from sleap_plotting import plotting_SLEAP

results = plotting_SLEAP(
    file_path="your_data.h5",
    main_node="bodycenter", 
    fps=30,
    output_dir="./results"
    # box_size_inches=(11, 11) is the default
)
```

### Custom Arena Size
```python
results = plotting_SLEAP(
    file_path="your_data.h5",
    main_node="bodycenter",
    fps=30, 
    output_dir="./results",
    box_size_inches=(8, 12)  # Custom arena: 8" × 12"
)
```

### Individual Analysis Functions
```python
# Inter-mouse distance with centimeter conversion
distances_px, distances_cm = analyze_inter_mouse_distance(
    locations, node_index, "bodycenter", fps=30, 
    output_dir="./results", box_size_inches=(11, 11)
)

# Cumulative distance with centimeter conversion  
analyze_cumulative_distance(
    locations, node_index, "bodycenter", fps=30,
    output_dir="./results", box_size_inches=(11, 11)
)
```

## 📊 Example Output

### Console Output
```
Pixel-to-CM Conversion:
- Arena size: 11" × 11" (27.9 × 27.9 cm)
- Pixel range: 610.7 pixels
- Conversion factor: 0.0457 cm/pixel
```

### Sample CSV Data
```csv
frame,time_seconds,inter_mouse_distance_pixels,inter_mouse_distance_cm,mouse1_x,mouse1_y,mouse2_x,mouse2_y
0,0.000,156.8,7.17,245.2,298.5,102.4,302.1
1,0.033,142.3,6.51,247.8,301.2,105.5,299.8
2,0.067,168.9,7.72,250.1,303.9,108.2,297.4
```

## 🧮 Conversion Details

### How It Works
1. **Arena Specification**: You provide arena dimensions in inches
2. **Pixel Range Calculation**: Algorithm finds the full range of animal movement in pixels
3. **Conversion Factor**: `cm_per_pixel = (arena_size_inches × 2.54) / pixel_range`
4. **Distance Conversion**: All pixel distances are multiplied by this factor

### Assumptions
- Animals utilize the full arena space during tracking
- Arena is approximately square (uses larger dimension for conversion)
- Tracking coordinates represent the full camera field of view

### Validation
For an 11" × 11" arena:
- Expected diagonal: ~39.5 cm
- Typical conversion: ~0.045 cm/pixel (varies by camera resolution and setup)

## ⚠️ Important Notes

1. **Arena Size Accuracy**: Ensure you specify the correct arena dimensions
2. **Camera Setup**: Conversion assumes camera captures the full arena
3. **Animal Movement**: More accurate if animals explore the full space
4. **Square vs. Rectangle**: For non-square arenas, the larger dimension is used

## 🔄 Backwards Compatibility

- All original pixel-based functionality is preserved
- Existing function signatures work without modification
- New centimeter features are additive - original plots and CSVs still generated
- Default arena size (11" × 11") used if not specified

## 📈 Benefits

1. **Biological Relevance**: Distances in meaningful real-world units
2. **Cross-Study Comparison**: Standardized measurements across different setups
3. **Publication Ready**: Professional units for manuscripts and presentations
4. **Behavioral Analysis**: Easier to interpret social distances and movement patterns

## 🚀 Example Applications

```python
import pandas as pd

# Load centimeter-based distance data
df = pd.read_csv("results/bodycenter_inter_mouse_distances.csv")

# Analyze social interaction distances
close_interaction_threshold = 5.0  # cm
close_interactions = df['inter_mouse_distance_cm'] < close_interaction_threshold
print(f"Time spent in close interaction: {close_interactions.mean()*100:.1f}%")

# Load per-second aggregated data for smoother analysis
df_seconds = pd.read_csv("results/bodycenter_inter_mouse_distances_by_seconds.csv") 
avg_distance_per_second = df_seconds['inter_mouse_distance_cm_mean']
print(f"Average inter-mouse distance: {avg_distance_per_second.mean():.2f} ± {avg_distance_per_second.std():.2f} cm")
```

This enhancement makes the SLEAP analysis pipeline more suitable for behavioral research by providing biologically meaningful distance measurements while maintaining all existing functionality.