"""
Arena calibration for the SLEAP downstream analysis pipeline.

Measures the pixel width of the box floor (the 11" x 11" inner surface the mice
walk on) directly from the video, so distances can be converted to centimeters
with a fixed, reproducible factor instead of inferring scale from how far the
animals happened to move.

Method
------
1. Median-composite ~80 evenly spaced frames. The mice move, the box does not,
   so the median removes the animals and leaves a clean, static box image.
2. Segment the bedding by local texture (bedding is high-texture; the walls are
   smooth). The bedding spans the floor wall-to-wall horizontally, so its
   x-extent equals the 27.94 cm floor width -- the most reliable, least
   perspective-distorted reference edge.
3. cm_per_pixel = (arena_inches * 2.54) / floor_width_px.

Detection failures (e.g. bedding scattered up a wall) are flagged for review in
the montage; override any row by editing the CSV or passing --manual.

Usage
-----
    python calibrate_arena.py --video-root "/path/to/Videos for SLEAP" \
        --output arena_calibration.csv --montage calibration_montage.png

    # override one video's floor width by hand (in pixels):
    python calibrate_arena.py --video-root ... --manual AF30_PBS_ST1_F_Noiso_07-23-2026_11-20-26_1=341
"""
import os
os.environ.setdefault("OPENCV_FFMPEG_THREADS", "1")
import argparse
import csv
import glob
import cv2
cv2.setNumThreads(1)
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ARENA_INCHES = 11.0          # box floor is 11" x 11"
INCH_TO_CM = 2.54
TEXTURE_THRESH = 12.0        # grayscale local-std threshold separating bedding from walls
# central band of the bedding used for the width estimate (fractions of blob height);
# excludes the sparse far edge and the dark near-wall strip that can leak to the frame edge
BAND_LO, BAND_HI = 0.15, 0.70


def median_composite(video_path, n_frames=80):
    """Return a BGR median composite over n_frames evenly spaced frames."""
    cap = cv2.VideoCapture(video_path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if n <= 0:
        cap.release()
        raise RuntimeError(f"could not read frames from {video_path}")
    idxs = np.linspace(0, n - 1, min(n_frames, n)).astype(int)
    frames = []
    for i in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ok, fr = cap.read()
        if ok:
            frames.append(fr)
    cap.release()
    if not frames:
        raise RuntimeError(f"no frames decoded from {video_path}")
    return np.median(np.stack(frames), axis=0).astype(np.uint8)


def detect_floor_width(bgr):
    """Detect the box-floor pixel width from a median composite.

    Returns (left_px, right_px, row_range, mask). The bedding is segmented by
    local texture; the left/right walls are the median edges of the bedding blob
    over its central rows, with per-row outliers (wall leaks) rejected.
    """
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    mean = cv2.boxFilter(gray, -1, (9, 9))
    sq = cv2.boxFilter(gray * gray, -1, (9, 9))
    texture = np.sqrt(np.clip(sq - mean * mean, 0.0, None))
    mask = (texture > TEXTURE_THRESH).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))

    nlab, lab, stats, _ = cv2.connectedComponentsWithStats(mask)
    if nlab > 1:
        biggest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        mask = (lab == biggest).astype(np.uint8) * 255

    ys, xs = np.where(mask > 0)
    if ys.size == 0:
        raise RuntimeError("no bedding texture detected")
    r0, r1 = int(ys.min()), int(ys.max())
    lo = r0 + BAND_LO * (r1 - r0)
    hi = r0 + BAND_HI * (r1 - r0)

    lefts, rights = [], []
    for r in range(int(lo), int(hi) + 1):
        xr = xs[ys == r]
        if xr.size >= 20:                      # ignore rows with too little bedding
            lefts.append(xr.min())
            rights.append(xr.max())
    lefts, rights = np.array(lefts), np.array(rights)
    widths = rights - lefts
    med = np.median(widths)
    good = np.abs(widths - med) < 0.15 * med   # drop rows leaking up a wall
    left = float(np.median(lefts[good]))
    right = float(np.median(rights[good]))
    return left, right, (r0, r1), mask


def calibrate_video(video_path):
    """Return dict with floor width and cm/pixel for one video."""
    bgr = median_composite(video_path)
    left, right, (r0, r1), _ = detect_floor_width(bgr)
    width = right - left
    cm_per_pixel = (ARENA_INCHES * INCH_TO_CM) / width
    return {
        "composite": bgr,
        "left": left, "right": right, "row_range": (r0, r1),
        "width_px": width, "cm_per_pixel": cm_per_pixel,
    }


def basename_of(video_path):
    return os.path.splitext(os.path.basename(video_path))[0]


def main():
    p = argparse.ArgumentParser(description="Measure per-video arena floor calibration.")
    p.add_argument("--video-root", required=True, help="directory searched recursively for .mp4 files")
    p.add_argument("--output", default="arena_calibration.csv", help="output calibration CSV path")
    p.add_argument("--montage", default="calibration_montage.png", help="review montage image path")
    p.add_argument("--manual", nargs="*", default=[],
                   help="override floor width in px, e.g. VIDEO_BASENAME=341")
    args = p.parse_args()

    overrides = {}
    for item in args.manual:
        key, _, val = item.partition("=")
        overrides[key] = float(val)

    videos = sorted(glob.glob(os.path.join(args.video_root, "**", "*.mp4"), recursive=True))
    if not videos:
        raise SystemExit(f"no .mp4 files found under {args.video_root}")

    rows, panels = [], []
    for vid in videos:
        base = basename_of(vid)
        try:
            r = calibrate_video(vid)
            source = "auto"
            if base in overrides:
                r["width_px"] = overrides[base]
                r["right"] = r["left"] + overrides[base]   # keep the row self-consistent
                r["cm_per_pixel"] = (ARENA_INCHES * INCH_TO_CM) / overrides[base]
                source = "manual"
            rows.append({
                "video": base,
                "floor_left_px": round(r["left"], 1),
                "floor_right_px": round(r["right"], 1),
                "floor_width_px": round(r["width_px"], 1),
                "cm_per_pixel": round(r["cm_per_pixel"], 5),
                "source": source,
            })
            panels.append((base, r, source))
            print(f"{base:55s} width={r['width_px']:5.1f}px  cm/px={r['cm_per_pixel']:.5f}  [{source}]")
        except Exception as e:  # noqa: BLE001 - report and continue over the batch
            print(f"{base:55s} FAILED: {e}")

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["video", "floor_left_px", "floor_right_px",
                                               "floor_width_px", "cm_per_pixel", "source"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {len(rows)} calibrations to {args.output}")

    # review montage
    ncol = 3
    nrow = int(np.ceil(len(panels) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(ncol * 6, nrow * 4.5), squeeze=False)
    for ax, (base, r, source) in zip(axes.ravel(), panels):
        ax.imshow(cv2.cvtColor(r["composite"], cv2.COLOR_BGR2RGB))
        for xv in (r["left"], r["right"]):
            ax.axvline(xv, color="lime", lw=1.8)
        r0, r1 = r["row_range"]
        ax.plot([r["left"], r["right"]], [(r0 + r1) / 2] * 2, "o-", color="yellow", lw=1.5, ms=5)
        ax.set_title(f"{base[:34]}\nw={r['width_px']:.0f}px  cm/px={r['cm_per_pixel']:.4f} [{source}]",
                     fontsize=8)
        ax.set_xticks([]); ax.set_yticks([])
    for ax in axes.ravel()[len(panels):]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(args.montage, dpi=95)
    print(f"Wrote review montage to {args.montage}")

    widths = np.array([row["floor_width_px"] for row in rows])
    print(f"floor width px: median={np.median(widths):.0f}  "
          f"range={widths.min():.0f}-{widths.max():.0f}  "
          f"CV={widths.std() / widths.mean() * 100:.1f}%")


if __name__ == "__main__":
    main()
