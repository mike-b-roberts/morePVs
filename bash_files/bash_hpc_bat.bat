<<<<<<< HEAD
=======
cd /home/z5044992/en/morePVs
>>>>>>> ff9208756e907620096fd784b4e60d2039b899ac
#!/bin/bash
#SBATCH --mail-user=m.roberts@unsw.edu.au
#SBATCH --mail-type=FAIL
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
module load python/3.6
source /home/z5044992/python_venv/bin/activate
python morePVs.py -b home/z5044992/InputOutput/DATA_EN_3 -p EN1a_pv_bat4 -s siteJ_bat4_1 -t False

