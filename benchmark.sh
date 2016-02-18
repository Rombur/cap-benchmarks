#!/bin/sh

/scratch/build_cap.sh
/scratch/run_benchmarks.py
rm -rf /scratch/source
rm -rf /scratch/build
