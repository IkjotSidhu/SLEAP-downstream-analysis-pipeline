# 📏 Centimeter Distance Analysis Enhancement

## Overview

The SLEAP analysis pipeline has been enhanced to generate distance plots and CSV exports using **centimeters** in addition to pixels. This provides biologically meaningful distance measurements by converting pixel coordinates to real-world units based on your experimental arena dimensions.

## 🆕 New Features

### 1. **Calibrated Pixel-to-Centimeter Conversion**
- Conversion factor is measured **once per recording from the box floor**, not
  inferred from how far the animals moved.
- `calibrate_arena.py` composites the video (removing the mice), detects the
  11" floor width in pixels, and writes `arena_calibration.csv`.
- Conversion factor: `cm_per_pixel = (11 × 2.54) / floor_width_px`
- The pipeline looks up each recording's factor by file name, so the scale is
  fixed and reproducible across sessions.

> **Why not use the animals' movement range?** Earlier versions estimated the
> scale from the span of tracked positions (`max − min`). That is biased low
> when animals don't explore the full arena, corrupted by wall-climbing and
> tracking spikes, and — critically — gives a *different* factor for every
> recording, so cm values were not comparable across sessions. Measured floor
> widths across a 12-video rig were constant to within 0.4%, while the
> movement-based factor varied by ~22%.

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

### Step 1 — Calibrate the rig (once)
```bash
python calibrate_arena.py \
    --video-root "/path/to/Videos for SLEAP" \
    --output arena_calibration.csv \
    --montage calibration_montage.png
# Review calibration_montage.png; fix any bad detection with:
#   --manual VIDEO_BASENAME=<floor_width_px>
```

### Step 2 — Run the pipeline (factor resolved automatically)
```python
from sleap_plotting import plotting_SLEAP

results = plotting_SLEAP(
    file_path="your_data.predictions.analysis.h5",
    main_node="bodycenter",
    fps=30,
    output_dir="./results",
    # cm_per_pixel is looked up from arena_calibration.csv by file name.
)
```

### One-off override (no calibration entry)
```python
results = plotting_SLEAP(
    file_path="your_data.h5",
    main_node="bodycenter",
    fps=30,
    output_dir="./results",
    cm_per_pixel=0.0817,   # explicit factor for this recording
)
```

### Individual Analysis Functions
```python
# Inter-mouse distance — pass the fixed calibration factor directly
distances_px, distances_cm = analyze_inter_mouse_distance(
    locations, node_index, "bodycenter", cm_per_pixel=0.0817,
    fps=30, output_dir="./results"
)

# Cumulative distance
analyze_cumulative_distance(
    locations, node_index, "bodycenter", cm_per_pixel=0.0817,
    fps=30, output_dir="./results"
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
1. **Composite the video**: `calibrate_arena.py` takes the per-pixel median over
   ~80 evenly spaced frames. The mice move and the box does not, so the median
   leaves a clean, static image of the arena.
2. **Detect the floor width**: the bedding is segmented by local texture (bedding
   is high-texture; the walls are smooth). The bedding spans the floor
   wall-to-wall horizontally, so its pixel width equals the 27.94 cm floor width.
3. **Conversion factor**: `cm_per_pixel = (11 × 2.54) / floor_width_px`, written
   to `arena_calibration.csv` (one row per recording).
4. **Distance Conversion**: the pipeline looks up each recording's factor by file
   name and multiplies all pixel distances by it.

Detection failures (e.g. bedding scattered up a wall) are flagged in the review
montage; override any recording with `--manual VIDEO_BASENAME=<width_px>` or by
editing the CSV.

### Assumptions
- The 11" × 11" floor is the surface the mice walk on (the tracked plane).
- The bedding reaches the left and right walls, so its horizontal extent equals
  the floor width. (The angled camera view makes a single scalar factor a mild
  approximation across the floor's depth; floor width is the most stable edge.)

### Validation
For an 11" × 11" arena:
- Expected diagonal: ~39.5 cm — a valid inter-animal distance can never exceed this.
- Measured on this rig (640×480 video): floor ≈ 341 px → **~0.082 cm/pixel**.

## ⚠️ Important Notes

1. **Arena Size Accuracy**: Ensure you specify the correct arena dimensions
2. **Camera Setup**: Conversion assumes camera captures the full arena
3. **Animal Movement**: More accurate if animals explore the full space
4. **Square vs. Rectangle**: For non-square arenas, the larger dimension is used

## 🔄 Compatibility Notes

- All original pixel-based plots and CSVs are still generated.
- **Signature change:** the distance functions now take a `cm_per_pixel` factor
  instead of `box_size_inches`. `plotting_SLEAP` resolves it automatically from
  `arena_calibration.csv`; pass `cm_per_pixel=<float>` to override.
- Recordings with no calibration entry raise a clear error rather than silently
  reporting distances in the wrong units.

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