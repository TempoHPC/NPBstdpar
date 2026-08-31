#!/bin/bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <class-letter> <num_runs>"
  exit 1
fi

class=$1
runs=$2
script_dir="$(cd "$(dirname "$0")" && pwd)"
outdir="$script_dir/results/sp${class}GPU"
tmpdir=$(mktemp -d)
binary="$script_dir/sp.${class}.x"

mkdir -p "$outdir"

for i in $(seq 1 "$runs"); do
  export NPB_TIMER_FLAG=1
  export ACC_NUM_CORES=1
  srun -p sequana_gpu_dev -N1 -n1 -c1 --gpus=1 "$binary" > "$tmpdir/run_${i}.log" 2>&1 || true
done

cat "$tmpdir"/run_*.log > "$outdir/all_runs.log"
(cd "$script_dir" && python3 parse_sp_simple.py "$outdir/all_runs.log")
mv "$script_dir/summary.txt" "$outdir/summary.txt"
rm -rf "$tmpdir"
