"""
Arena calibration for the SLEAP downstream analysis pipeline (per-rig method).

Each recording rig (box + camera, e.g. NL1, NL2) is measured ONCE: the four
floor corners are marked on a clean reference frame and stored in a rigs CSV.
Every video is then checked against its rig's reference instead of being
re-measured from scratch, so changing bedding, nesting material, food bowls or
resting mice can no longer corrupt the calibration.

Per video:
  1. Median-composite ~80 evenly spaced frames (removes the moving mice).
  2. Register the composite to the rig reference using only the static box
     structure (walls and floor outline; the floor interior is masked out).
     A shift <= --max-shift px is applied to the reference corners; a larger
     shift means the camera moved, and the video is marked CAMERA_MOVED with no
     calibration, so it fails loudly downstream instead of using a wrong scale.
  3. A perspective transform (homography) maps the four floor corners onto the
     true 27.94 x 27.94 cm floor. Distances are computed after mapping points to
     cm, which removes the near/far-wall perspective error of a single scale.
     ``cm_per_pixel`` (the local scale at the floor centre) is still written for
     backwards compatibility.

Usage
-----
    # 1) once per rig: build the reference (composite + corner overlay)
    python calibrate_arena.py reference --rig NL1 --video "/path/NL1_clean.mp4" \
        --rigs rigs.csv --out-dir calibration_rigs \
        --corners "171,49 435,49 445,368 160,368"      # TL TR BR BL (x,y px)

    # 2) every batch: check videos against their rig and write the calibration CSV
    python calibrate_arena.py apply --video-root "/path/videos" --rigs rigs.csv \
        --output arena_calibration.csv --montage calibration_montage.png

The rig is taken from the video name (``_NL1_``-style token) or from
``--rig-map`` (CSV with columns video,rig) for names that do not contain it.
"""
import os
os.environ.setdefault("OPENCV_FFMPEG_THREADS", "1")
import argparse
import csv
import datetime
import glob
import re

import cv2
cv2.setNumThreads(1)
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ARENA_INCHES = 11.0          # box floor is 11" x 11"
INCH_TO_CM = 2.54
ARENA_CM = ARENA_INCHES * INCH_TO_CM
RIG_PATTERN = re.compile(r"(?:^|_)(NL\d+)(?:_|$)")
CORNER_NAMES = ["tl", "tr", "br", "bl"]
RIG_FIELDS = ["rig", "reference_video", "reference_image", "measured_on"] + \
    [f"{c}_{a}" for c in CORNER_NAMES for a in ("x", "y")]
CALIB_FIELDS = ["video", "rig", "shift_x_px", "shift_y_px", "floor_width_px",
                "cm_per_pixel", "homography", "source"]


# ---- Image helpers -----------------------------------------------------------
def median_composite(video_path, n_frames=80, cache_dir=None):
    """Return a BGR median composite over n_frames evenly spaced frames.

    With ``cache_dir`` the composite is stored as <video>.png and reused.
    """
    cache = None
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
        cache = os.path.join(cache_dir, basename_of(video_path) + ".png")
        if os.path.exists(cache):
            return cv2.imread(cache)
    cap = cv2.VideoCapture(video_path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if n <= 0:
        cap.release()
        raise RuntimeError(f"could not read frames from {video_path}")
    frames = []
    for i in np.linspace(0, n - 1, min(n_frames, n)).astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ok, fr = cap.read()
        if ok:
            frames.append(fr)
    cap.release()
    if not frames:
        raise RuntimeError(f"no frames decoded from {video_path}")
    comp = np.median(np.stack(frames), axis=0).astype(np.uint8)
    if cache:
        cv2.imwrite(cache, comp)
    return comp


def structure_image(bgr, corners):
    """Edge-magnitude image of the static box structure, floor interior masked out.

    The floor interior (bedding, nest, bowl, mice) changes between recordings,
    so only the walls and the floor outline are used for registration.
    """
    gray = cv2.GaussianBlur(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32), (5, 5), 0)
    mag = cv2.magnitude(cv2.Sobel(gray, cv2.CV_32F, 1, 0), cv2.Sobel(gray, cv2.CV_32F, 0, 1))
    # Shrink the floor polygon toward its centre by 12% and zero its interior.
    c = np.asarray(corners, np.float32)
    inner = (c - c.mean(0)) * 0.88 + c.mean(0)
    mask = np.ones(gray.shape, np.uint8)
    cv2.fillPoly(mask, [inner.astype(np.int32)], 0)
    mag *= mask
    # Remove the burned-in timestamp (top-left text changes every video).
    mag[:20, :160] = 0
    return mag


def register_shift(ref_bgr, bgr, corners):
    """(dx, dy) translation of ``bgr`` relative to the rig reference, in pixels."""
    a = structure_image(ref_bgr, corners)
    b = structure_image(bgr, corners)
    win = cv2.createHanningWindow(a.shape[::-1], cv2.CV_32F)
    (dx, dy), _ = cv2.phaseCorrelate(a, b, win)
    return float(dx), float(dy)


# ---- Geometry ----------------------------------------------------------------
def floor_homography(corners):
    """3x3 homography mapping image px (TL, TR, BR, BL floor corners) to floor cm."""
    dst = np.float32([[0, 0], [ARENA_CM, 0], [ARENA_CM, ARENA_CM], [0, ARENA_CM]])
    return cv2.getPerspectiveTransform(np.float32(corners), dst)


def centre_cm_per_pixel(H, corners):
    """Local (area-equivalent) cm/pixel scale of homography H at the floor centre."""
    cx, cy = np.asarray(corners, np.float64).mean(0)
    pts = np.float32([[[cx, cy]], [[cx + 1, cy]], [[cx, cy + 1]]])
    p0, px, py = cv2.perspectiveTransform(pts, H)[:, 0]
    (ax, ay), (bx, by) = px - p0, py - p0
    return float(np.sqrt(abs(ax * by - ay * bx)))   # sqrt of the 1-px-square area in cm^2


def floor_width_px(corners):
    """Mean of the top and bottom floor-edge lengths in pixels (for reference)."""
    c = np.asarray(corners, np.float64)
    return float((np.linalg.norm(c[1] - c[0]) + np.linalg.norm(c[2] - c[3])) / 2)


# ---- Rigs table --------------------------------------------------------------
def basename_of(video_path):
    return os.path.splitext(os.path.basename(video_path))[0]


def load_rigs(path):
    """{rig: {'corners': [[x,y]x4], 'reference_image': path, ...}} from the rigs CSV."""
    rigs = {}
    if not os.path.exists(path):
        return rigs
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            row["corners"] = [[float(row[f"{c}_x"]), float(row[f"{c}_y"])] for c in CORNER_NAMES]
            rigs[row["rig"]] = row
    return rigs


def save_rigs(path, rigs):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=RIG_FIELDS, extrasaction="ignore")
        w.writeheader()
        for rig in sorted(rigs):
            w.writerow(rigs[rig])


def rig_of(base, rig_map):
    """Rig for a video: explicit --rig-map entry first, else the _NLx_ token in its name."""
    if base in rig_map:
        return rig_map[base]
    m = RIG_PATTERN.search(base)
    return m.group(1) if m else None


def draw_floor(ax, img_bgr, corners, title, color="lime"):
    """Show a composite with the floor polygon and corner labels."""
    ax.imshow(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    c = np.vstack([corners, corners[:1]])
    ax.plot(c[:, 0], c[:, 1], "-", color=color, lw=1.4)
    for (x, y), name in zip(corners, CORNER_NAMES):
        ax.plot(x, y, "o", ms=4, color="yellow")
        ax.annotate(name.upper(), (x, y), color="yellow", fontsize=7,
                    xytext=(4, -4), textcoords="offset points")
    ax.set_title(title, fontsize=8)
    ax.set_xticks([]); ax.set_yticks([])


# ---- Subcommands -------------------------------------------------------------
def cmd_reference(args):
    """Build (or update) one rig's reference composite and corners."""
    os.makedirs(args.out_dir, exist_ok=True)
    comp = median_composite(args.video, cache_dir=os.path.join(args.out_dir, "composites"))
    ref_img = os.path.join(args.out_dir, f"{args.rig}_reference.png")
    cv2.imwrite(ref_img, comp)
    print(f"Reference composite -> {ref_img}")
    if not args.corners:
        print("No --corners given: open the composite, read the four floor corners "
              "(TL TR BR BL), and re-run with --corners.")
        return
    corners = [[float(v) for v in pt.split(",")] for pt in args.corners.split()]
    if len(corners) != 4:
        raise SystemExit("--corners needs exactly four 'x,y' points: TL TR BR BL")
    rigs = load_rigs(args.rigs)
    row = {"rig": args.rig, "reference_video": basename_of(args.video),
           "reference_image": os.path.abspath(ref_img),
           "measured_on": datetime.date.today().isoformat()}
    for (x, y), name in zip(corners, CORNER_NAMES):
        row[f"{name}_x"], row[f"{name}_y"] = round(x, 1), round(y, 1)
    rigs[args.rig] = row
    save_rigs(args.rigs, rigs)
    H = floor_homography(corners)
    overlay = os.path.join(args.out_dir, f"{args.rig}_corners_overlay.png")
    fig, ax = plt.subplots(figsize=(9, 7))
    draw_floor(ax, comp, corners,
               f"{args.rig}: floor {ARENA_CM:.2f} cm square | width ~{floor_width_px(corners):.0f} px | "
               f"centre {centre_cm_per_pixel(H, corners):.5f} cm/px")
    fig.tight_layout(); fig.savefig(overlay, dpi=110); plt.close(fig)
    print(f"Saved rig {args.rig} to {args.rigs}; check the overlay: {overlay}")


def cmd_apply(args):
    """Calibrate every video under --video-root against its rig reference."""
    rigs = load_rigs(args.rigs)
    if not rigs:
        raise SystemExit(f"no rigs defined in {args.rigs}; run the 'reference' step first")
    refs = {r: cv2.imread(v["reference_image"]) for r, v in rigs.items()}
    rig_map = {}
    if args.rig_map:
        with open(args.rig_map, newline="") as f:
            rig_map = {row["video"]: row["rig"] for row in csv.DictReader(f)}

    videos = sorted(glob.glob(os.path.join(args.video_root, "**", "*.mp4"), recursive=True))
    if not videos:
        raise SystemExit(f"no .mp4 files found under {args.video_root}")
    cache = os.path.join(os.path.dirname(os.path.abspath(args.output)), "composites")

    rows, panels = [], []
    for vid in videos:
        base = basename_of(vid)
        rig = rig_of(base, rig_map)
        row = {"video": base, "rig": rig or ""}
        if rig not in rigs:
            row["source"] = "NO_RIG"
            print(f"{base:55s} NO_RIG (rig={rig!r}; add it to --rig-map or the rigs CSV)")
            rows.append(row)
            continue
        comp = median_composite(vid, cache_dir=cache)
        ref_corners = np.asarray(rigs[rig]["corners"], np.float64)
        dx, dy = register_shift(refs[rig], comp, ref_corners)
        row.update(shift_x_px=round(dx, 2), shift_y_px=round(dy, 2))
        corners = ref_corners + [dx, dy]
        if np.hypot(dx, dy) > args.max_shift:
            row["source"] = "CAMERA_MOVED"
            print(f"{base:55s} CAMERA_MOVED shift=({dx:+.1f},{dy:+.1f}) px > {args.max_shift} px; "
                  f"re-measure rig {rig} with the 'reference' step")
        else:
            H = floor_homography(corners)
            row.update(floor_width_px=round(floor_width_px(corners), 1),
                       cm_per_pixel=round(centre_cm_per_pixel(H, corners), 5),
                       homography=" ".join(f"{v:.8g}" for v in H.ravel()),
                       source=f"rig:{rig}")
            print(f"{base:55s} rig={rig} shift=({dx:+.1f},{dy:+.1f}) px  "
                  f"centre cm/px={row['cm_per_pixel']:.5f}")
        rows.append(row)
        panels.append((base, comp, corners, row))

    with open(args.output, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CALIB_FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {len(rows)} calibrations to {args.output}")

    ncol = 3
    nrow = max(1, int(np.ceil(len(panels) / ncol)))
    fig, axes = plt.subplots(nrow, ncol, figsize=(ncol * 6, nrow * 4.7), squeeze=False)
    for ax, (base, comp, corners, row) in zip(axes.ravel(), panels):
        bad = row["source"] == "CAMERA_MOVED"
        draw_floor(ax, comp, corners,
                   f"{base[:40]}\n{row['source']}  shift=({row['shift_x_px']:+.1f},{row['shift_y_px']:+.1f}) px",
                   color="red" if bad else "lime")
    for ax in axes.ravel()[len(panels):]:
        ax.axis("off")
    fig.tight_layout(); fig.savefig(args.montage, dpi=95); plt.close(fig)
    print(f"Wrote review montage to {args.montage}")

    failed = [r["video"] for r in rows if not r["source"].startswith("rig:")]
    if failed:
        print(f"\n** {len(failed)} video(s) NOT calibrated: {failed}")


def main():
    p = argparse.ArgumentParser(description="Per-rig arena floor calibration.")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("reference", help="measure a rig once from a clean video")
    r.add_argument("--rig", required=True, help="rig name as it appears in video names, e.g. NL1")
    r.add_argument("--video", required=True, help="a video recorded on this rig")
    r.add_argument("--rigs", default="rigs.csv", help="rigs CSV to create/update")
    r.add_argument("--out-dir", default="calibration_rigs", help="where reference images go")
    r.add_argument("--corners", default="", help='floor corners "x,y x,y x,y x,y" in order TL TR BR BL')
    r.set_defaults(func=cmd_reference)

    a = sub.add_parser("apply", help="calibrate a batch of videos against their rigs")
    a.add_argument("--video-root", required=True, help="directory searched recursively for .mp4 files")
    a.add_argument("--rigs", default="rigs.csv")
    a.add_argument("--rig-map", default=None, help="CSV video,rig for names without an _NLx_ token")
    a.add_argument("--output", default="arena_calibration.csv")
    a.add_argument("--montage", default="calibration_montage.png")
    a.add_argument("--max-shift", type=float, default=3.0,
                   help="largest camera shift (px) still accepted without re-measuring")
    a.set_defaults(func=cmd_apply)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
