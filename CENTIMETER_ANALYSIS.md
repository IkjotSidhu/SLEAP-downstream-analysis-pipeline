# 📏 Centimeter Distance Analysis Enhancement

## Overview

The SLEAP analysis pipeline has been enhanced to generate distance plots and CSV exports using **centimeters** in addition to pixels. This provides biologically meaningful distance measurements by converting pixel coordinates to real-world units based on your experimental arena dimensions.

## 🆕 New Features

### 1. **Calibrated Pixel-to-Centimeter Conversion (per rig)**
- Each rig (box + camera, e.g. `NL1`, `NL2`) is measured **once**: the four
  floor corners are marked on a clean reference frame and stored in `rigs.csv`.
- `calibrate_arena.py apply` checks every video against its rig reference
  (registration on the static walls only) and writes `arena_calibration.csv`
  with a floor **homography** per recording. A camera shift larger than
  `--max-shift` (3 px) marks the video `CAMERA_MOVED` instead of guessing.
- Positions are mapped onto the 27.94 × 27.94 cm floor plane before distances
  are computed, which removes the near/far perspective error of a single factor.
  `cm_per_pixel` (local scale at the floor centre) is still written for reference.
- The pipeline looks up each recording by file name, so the scale is fixed and
  reproducible across sessions.

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

### Step 1 — Measure each rig (once, and again only if its camera moves)
```bash
python calibrate_arena.py reference --rig NL1 \
    --video "/path/to/a_clean_NL1_video.mp4" \
    --rigs rigs.csv --out-dir calibration_rigs \
    --corners "165.6,22.9 499.2,29.8 500.7,351.5 175.6,350.0"   # TL TR BR BL floor corners (px)
# Check calibration_rigs/NL1_corners_overlay.png: the outline must sit on the
# wall/floor junction on all four sides.
```

### Step 1b — Calibrate a batch against its rigs
```bash
python calibrate_arena.py apply \
    --video-root "/path/to/Videos for SLEAP" --rigs rigs.csv \
    --output arena_calibration.csv --montage calibration_montage.png
# Rig = the _NLx_ token in the video name, or --rig-map video,rig CSV.
# CAMERA_MOVED / NO_RIG videos get no calibration and fail loudly downstream:
# re-run 'reference' for a new rig entry and map those videos to it.
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
1. **Composite the video**: the per-pixel median over ~80 evenly spaced frames
   removes the mice and leaves a clean, static image of the box.
2. **Register to the rig**: the composite's edge image (walls and floor outline
   only; the floor interior and timestamp are masked out because bedding, nests,
   bowls and resting mice change between recordings) is phase-correlated with
   the rig reference to measure any camera shift.
3. **Floor homography**: the rig's four floor corners (plus the measured shift)
   are mapped onto a 27.94 cm square, giving a 3 × 3 transform from image px to
   floor cm, written to `arena_calibration.csv`.
4. **Distance conversion**: tracked positions are mapped to floor cm and
   inter-mouse / path distances are measured there.

### Why the earlier bedding-texture method was replaced
Bedding and nesting material pile up against the walls, so the textured area
extends past the floor edge (typically 8–10 px per side on 640×480 video), and
white nesting or a resting mouse can split it. On the November 2026 batch it
failed on 6 of 10 videos (143–475 px), and even its "good" values (344–348 px)
were ~5% wider than the true floor (~328 px), so cm distances came out ~5% low.

### Assumptions
- The 11" × 11" floor is the inner floor surface; corners are placed on the
  wall/floor junction.
- Mice are tracked close to the floor plane. Their body centre sits ~1–2 cm
  above it, which on these rigs shifts scale by well under the bedding error the
  old method had; tracked body centres span ~0–28 cm, matching the floor.

### Validation (November 2026, NL1 / NL2, 640×480)
- Floor ≈ 328 px wide → **~0.0855 cm/pixel at the floor centre** on both rigs.
- 9/10 videos registered within 1 px of their rig; one (NL1, 09-23 afternoon)
  had moved ~14 px and was given its own reference.
- 98–99.5% of tracked body-centre positions fall inside the calibrated floor.

## ⚠️ Important Notes

1. **Arena Size Accuracy**: Ensure you specify the correct arena dimensions
2. **Camera Setup**: Conversion assumes camera captures the full arena
3. **Animal Movement**: More accurate if animals explore the full space
4. **Square vs. Rectangle**: For non-square arenas, the larger dimension is used

## 🔄 Compatibility Notes

- All original pixel-based plots and CSVs are still generated.
- **Signature change:** the distance functions take `cm_per_pixel` and an
  optional `homography`. `plotting_SLEAP` resolves both from
  `arena_calibration.csv`; pass `cm_per_pixel=<float>` to override (no
  perspective correction).
- Older scalar-only calibration CSVs still load (no homography column).
- Recordings with no calibration entry, or marked `CAMERA_MOVED` / `NO_RIG`,
  raise a clear error rather than silently reporting distances in wrong units.

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