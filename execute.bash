#!/bin/bash
#SBATCH --job-name=gen_syn
#SBATCH --output=run_%j.out
#SBATCH --error=run_%j.err
#SBATCH -n 3
#SBATCH --partition=par-gpu

blender $1 -b -noaudio -t 512 -P genDescFromRRv3.py

