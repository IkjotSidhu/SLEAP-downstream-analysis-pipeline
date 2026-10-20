# Methodology Changes — SLEAP Downstream Analysis Pipeline

This document describes the **scientific/methodology changes** made on the `dev`
branch, so they can be reviewed and judged. It deliberately excludes pure code
cleanups (imports, de-duplication, figure handling); those don't change any
numbers. Every change below either changes a computed value or changes what is
reported about data quality.

Each section states: **what it did before**, **why that was a problem**, **what
it does now**, the **parameters you can tune**, and **what to judge**.

---

## 1. Pixel → centimeter calibration

### Before
`calculate_pixel_to_cm_conversion()` derived the scale from the **span of the
animals' tracked positions**:

```
cm_per_pixel = arena_cm / (max(tracked_coord) − min(tracked_coord))
```

### Why that was a problem
The denominator depends on animal behavior, not on the camera geometry:

- It assumes the animals visit the full arena. If they hug walls/corners (mice
  thigmotax), the span underestimates the arena and **every cm distance is
  inflated**.
- A single tracking spike (or a node extrapolated off-frame during a rear/climb)
  blows up `max − min` and shrinks all distances.
- It produces a **different factor for every recording**, so cm values are not
  comparable across sessions — which defeats the purpose of using real units.

Measured on your 4-video sample, the movement-based factor ranged **0.0615–0.0753
cm/px (a 22% spread)** across identical boxes; the y-range even hit **−6 px**
(nodes predicted above the frame while a mouse climbed the far wall).

### What it does now
The factor is measured **once per recording from a fixed physical landmark — the
box floor** — by `calibrate_arena.py`:

1. **Median-composite** ~80 evenly spaced video frames. The box is static and the
   mice move, so the per-pixel median removes the animals and leaves a clean box.
2. **Segment the bedding by local texture** (bedding is grainy/high-variance; the
   walls are smooth). The bedding spans the floor wall-to-wall horizontally, so
   its pixel width equals the known floor width.
3. `cm_per_pixel = (11 in × 2.54) / floor_width_px`, written to
   `arena_calibration.csv` (one row per recording), with a review montage.

At run time, `resolve_cm_per_pixel()` looks up each recording by file name. If a
file has no calibration entry it **raises an error** rather than guessing.

Measured across all **12 rig videos**: floor width **341 ± 4 px (CV 0.4 %) →
~0.0819 cm/px**. One video needed a manual override (bedding scattered up a wall
fooled the auto-detector); it was corrected to the rig median.

### Parameters
- Arena size: **11 in = 27.94 cm** (hard-coded in `calibrate_arena.py`).
- Calibration source: `arena_calibration.csv`, or an explicit `cm_per_pixel=`.

### What to judge
- **The 11″ refers to the inner floor** the mice walk on (you confirmed this).
- The camera is **angled, not perfectly top-down**, so the floor is a shallow
  trapezoid and a single `cm_per_pixel` is a **mild approximation** — scale drifts
  slightly front-to-back. We calibrate on floor **width** (the most stable,
  least-foreshortened edge). If you ever need sub-cm accuracy everywhere, the
  next step would be a full perspective (homography) correction; we deliberately
  did **not** do that.
- Net effect vs the old method: previously reported cm distances were
  **underestimated by ~10–25 %**, inconsistently between sessions.

---

## 2. Missing-data handling (tracking dropouts)

### Before
`fill_missing()` linearly interpolated **all** NaN gaps and filled leading/
trailing gaps with the nearest value. Downstream distance/velocity/path metrics
then ran on this fully-filled array **with no flag**.

### Why that was a problem
During a dropout the positions are **fabricated**. A 5-second gap became a
straight line of invented coordinates, and the resulting "distances" looked like
real data. Nothing marked which frames were real.

### What it does now
Gaps are handled by length:

- **Short gaps (≤ `max_interp_gap_seconds`)** are interpolated, as before, but the
  affected frames are **flagged** in a new `interpolated` column in every
  per-frame CSV.
- **Long gaps (> `max_interp_gap_seconds`)** are **not trusted**: the corresponding
  distance/velocity values are set to **NaN** (shown as blank in CSVs and as gaps
  in plots) instead of fabricated.
- **Time-binned statistics** (per-second/minute) are computed on **observed frames
  only** — interpolated frames are dropped before aggregation and NaNs are
  skipped, so means/std/counts reflect real data. The `count` column now tells
  you how many real frames each bin was based on.

The run summary reports `Interpolated (short gaps) %`, `Dropped (long gaps) %`,
and `Still missing %`.

> The full-resolution position arrays remain gap-filled internally (so plots stay
> continuous and velocity math stays numerically stable); only the **quantitative
> outputs** get NaN'd for long gaps.

### Parameters
- `max_interp_gap_seconds = 0.5` (→ 15 frames at 30 fps). Gaps longer than this
  are dropped rather than filled.

### What to judge
- **Is 0.5 s the right cutoff?** It's the single most important knob here. Larger
  → more interpolation trusted; smaller → more frames dropped as untrustworthy.
- On the AF36 test recording this exposed that **mouse 2's bodycenter is tracked
  only ~27 % of the time** (long 5-second gaps). That's a real data-quality
  finding the old pipeline hid.
- **Over-filtering note:** for per-mouse metrics (velocity, cumulative distance)
  a frame is dropped from the binned stats if *either* mouse was interpolated in
  that row. This is conservative (a well-tracked mouse can lose a frame because
  its partner was missing). Flag if you'd prefer per-mouse independent filtering.

---

## 3. Cumulative distance (path length)

### Before
Path length was `cumsum(‖diff(raw_positions)‖)` — the running sum of raw
frame-to-frame displacement.

### Why that was a problem
Per-frame tracking jitter never averages out under a sum; it **accumulates**. A
stationary animal with ±1 px keypoint noise still racks up "distance" every
frame, so total path length is **systematically overestimated**.

### What it does now
Before summing, per mouse:

1. **Smooth** the position with a short moving average (`path_smoothing_window`).
2. Compute frame-to-frame displacement.
3. **Zero out sub-noise steps** (below `path_noise_threshold_px`) so stationary
   jitter contributes nothing.
4. **Exclude long-gap steps** (from §2) via `nancumsum`, so a dropout contributes
   0 rather than a fabricated jump.

### Parameters
- `path_smoothing_window = 5` frames (≤ 1 disables smoothing).
- `path_noise_threshold_px = 1.0` px (steps below this count as 0).

### What to judge
- Both parameters trade **sensitivity vs. jitter rejection**. A larger window or
  threshold gives lower, more conservative path lengths; too large and you
  suppress real slow movement. `1.0 px` (≈ 0.08 cm) and a 5-frame window are
  gentle defaults — worth sanity-checking against a known trajectory if path
  length is a primary endpoint for you.

---

## 4. Track-identity swap diagnostic

### Before
Per-mouse metrics assumed instance 0 and instance 1 are always the same animal.

### Why that was a problem
SLEAP track identities can **swap** mid-recording (two animals cross, occlude,
etc.). When that happens, per-mouse velocity and per-mouse cumulative distance
silently mix the two animals. (Inter-mouse *distance* is symmetric, so it is
unaffected by swaps.)

### What it does now
`detect_track_swaps()` scans every frame and compares **keeping** vs **swapping**
the two identities relative to the previous frame (nearest-neighbour). Frames
where swapping would have produced a much smaller total movement are flagged as
**likely identity swaps**, and a warning is printed with the count and example
frames. **The data is not modified** — this is a diagnostic only (your chosen
option: detect + warn, not auto-correct).

### Parameters
- `swap_detection_margin_px = 15.0` — how much smaller the swapped move must be
  than the kept move to flag a frame.

### What to judge
- This is a **heuristic flag**, not a correction. It tells you which recordings to
  inspect; it does not fix identities. If a recording flags many swaps, its
  per-mouse metrics should be treated with caution (inter-mouse distance is still
  fine).
- The margin (15 px) sets sensitivity: lower → more frames flagged (more false
  positives); higher → only blatant swaps.

---

## Summary of tunable parameters (all in `AnalysisConfig`)

| Parameter | Default | Controls |
|---|---|---|
| `max_interp_gap_seconds` | 0.5 s | longest gap that is interpolated vs. dropped (§2) |
| `path_smoothing_window` | 5 frames | position smoothing before path length (§3) |
| `path_noise_threshold_px` | 1.0 px | sub-noise step suppression (§3) |
| `swap_detection_margin_px` | 15.0 px | track-swap flag sensitivity (§4) |
| `velocity_window` / `velocity_poly_order` | 25 / 3 | Savitzky–Golay velocity smoothing |

Calibration (`cm_per_pixel`) is **not** in the config — it is a measured physical
property per recording, stored in `arena_calibration.csv`.

---

## What did *not* change (and why)

- **Inter-mouse distance definition** (Euclidean distance between the chosen node
  of the two instances) is unchanged — only its units (now calibrated cm) and its
  gap handling.
- **No perspective/homography correction** — a single `cm_per_pixel` is kept for
  simplicity; the angled view makes it a mild approximation (§1).
- **No automatic track-swap correction** — flagged only, to avoid introducing
  wrong "corrections" (§4).
- **2-animal assumption** is retained (this is a social-interaction pipeline).
