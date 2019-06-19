#!/bin/bash
export OPENBLAS_NUM_THREADS=2
#SBATCH --mail-user=m.roberts@unsw.edu.au
#SBATCH --mail-type=FAIL
#SBATCH --job-name="testing"
#SBATCH --array=0-48
#SBATCH --time=96:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8192
#SBATCH --output "/home/z5044992/InputOutput/DATA_EN_4/slurm/slurm_study_%A_%a.out"
module load python/3.6
source /home/z5044992/python_venv/bin/activate
python /home/z5044992/InputOutput/en/morePVs/morePVs.py -b /home/z5044992/InputOutput/DATA_EN_4 -p EN2_bat2_hpc -s energy4pd_G_hpc$(printf "%03d" $SLURM_ARRAY_TASK_ID)
echo energy4pd_G_hpc$(printf "%03d" $SLURM_ARRAY_TASK_ID)
deactivate
module unload python/3.6
