"""
Batch-run the SLEAP downstream analysis over every .h5 in a directory.

Each recording is written to its own subfolder under --output-root, with the
console log saved alongside its plots and CSVs. Recordings that fail (e.g. a
missing calibration entry or an untracked node) are reported and skipped so one
bad file doesn't halt the batch.

Usage:
    python run_downstream_batch.py \
        --h5-dir "/sc/arion/projects/naiklab/ikjot/Asma-SLEAP-Project-folder/h5_analysis" \
        --output-root "/sc/arion/projects/naiklab/ikjot/Asma-SLEAP-Project-folder/Downstream-Analysis" \
        --node bodycenter
"""
import argparse
import glob
import os
import sys
import contextlib

import sleap_plotting as sp


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--h5-dir", required=True)
    p.add_argument("--output-root", required=True)
    p.add_argument("--node", default="bodycenter")
    args = p.parse_args()

    h5_files = sorted(glob.glob(os.path.join(args.h5_dir, "*.h5")))
    if not h5_files:
        raise SystemExit(f"no .h5 files found in {args.h5_dir}")

    print(f"Found {len(h5_files)} recordings. Node = '{args.node}'.\n")
    ok, failed = [], []
    for h5 in h5_files:
        name = sp.calibration_key(h5)
        out_dir = os.path.join(args.output_root, name)
        os.makedirs(out_dir, exist_ok=True)
        log_path = os.path.join(out_dir, "analysis_log.txt")
        print(f"[{name}] -> {out_dir}")
        try:
            # Tee the pipeline's console output into the recording's log file.
            with open(log_path, "w") as log, contextlib.redirect_stdout(log):
                sp.plotting_SLEAP(h5, main_node=args.node, output_dir=out_dir)
            ok.append(name)
            print(f"    done ({log_path})")
        except Exception as e:  # noqa: BLE001 - keep the batch going
            failed.append((name, str(e)))
            print(f"    FAILED: {e}", file=sys.stderr)

    print(f"\n=== Batch complete: {len(ok)} succeeded, {len(failed)} failed ===")
    for name in ok:
        print(f"  ok    {name}")
    for name, err in failed:
        print(f"  FAIL  {name}: {err}")


if __name__ == "__main__":
    main()
