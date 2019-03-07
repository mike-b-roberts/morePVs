#!/bin/bash
#SBATCH --mail-user=m.roberts@unsw.edu.au
#SBATCH --mail-type=FAIL
#SBATCH --time=96:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8192
#SBATCH --output "/home/z5044992/InputOutput/DATA_EN_4/slurm/slurm_study_%j.out"
module load python/3.6
source /home/z5044992/python_venv/bin/activate
python /home/z5044992/InputOutput/en/morePVs/morePVs.py -b /home/z5044992/InputOutput/DATA_EN_4 -p optimiser060_hpc -s pv_optimiser_060_hpc002
deactivate
module unload python/3.6
