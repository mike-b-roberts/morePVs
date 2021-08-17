0,#!/bin/bash
1,#SBATCH --mail-user=m.roberts@unsw.edu.au
2,#SBATCH --mail-type=ALL
3,#SBATCH --time=12:00:00
4,#SBATCH --ntasks=1
5,#SBATCH --cpus-per-task=4
6,#SBATCH --mem=8192
7,"#SBATCH --output ""/home/z5044992/InputOutput/DATA_EN_3/slurm/slurm-%j.out"""
8,module load python/3.6
9,source /home/z5044992/python_venv/bin/activate
10,python morePVs.py -b /home/z5044992/InputOutput/DATA_EN_3 -p for_hpc_example2 -s study_example2_hpc0.csv -t False
11,deactivate
12,module unload python/3.6
