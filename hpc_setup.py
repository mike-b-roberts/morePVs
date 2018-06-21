import os
import en_utilities as um
import pandas as pd
import shutil
import numpy as np
import csv

# Input parameters:
# -----------------
project='EN1a_pv_bat4'
study = 'siteJ_bat4_2'
maxjobs = 120


# Establish paths etc
# -------------------
new_project = project+'_hpc'
base_path='/home/z5044992/InputOutput/DATA_EN_3/studies'

i_path = os.path.join(base_path,project,'inputs')
i_name ='study_'+study+'.csv'
i_file = os.path.join(i_path,i_name)

np_path =os.path.join(base_path,new_project)
if not os.path.exists (np_path):
    os.makedirs(np_path)
o_path =os.path.join(np_path,'inputs')
if not os.path.exists (o_path):
    os.makedirs(o_path)

df = pd.read_csv(i_file)
df = df.set_index('scenario')

#PAth for bash script files
# -------------------------
bash_path='/home/z5044992/InputOutput/en/morePVs/bash_files/'+new_project+'/'+study

# Split input (s'study_....csv') files 
# ------------------------------------

length = len(df)
num_jobs = min(length, maxjobs)
joblength = {}
for job in np.arange (num_jobs):
    if job <= round((length/num_jobs - int(length/num_jobs))*num_jobs)-1:
        joblength[job] = round(length/num_jobs +0.5)
    else:
        joblength[job] = int(length/num_jobs)
df1 = df.copy()
csv_list=[]
for job in np.arange (num_jobs):
    dfn = pd.DataFrame(df1.iloc[0:joblength[job]],columns=df1.columns)
    df1 = df1.iloc[joblength[job]:]
    o_name = 'study_'+study+'_hpc'+ str(job).zfill(3) +'.csv'
    csv_list += [o_name]
    o_file = os.path.join(o_path ,o_name)
    dfn.to_csv(o_file)

# Initiate PuTTY Script
# ---------------------
putty_script = []

# Create bash files
# -----------------

if not os.path.exists (bash_path):
    os.makedirs(bash_path)
for f in os.listdir(bash_path):
    xfile = os.path.join(bash_path,f)
    os.remove(xfile)
for csv_name in csv_list:
    #
    bash_content = pd.Series([
    '#!/bin/bash',
    '#SBATCH --mail-user=m.roberts@unsw.edu.au',
    '#SBATCH --mail-type=FAIL',
    '#SBATCH --time=12:00:00',
    '#SBATCH --ntasks=1',
    '#SBATCH --cpus-per-task=4',
    '#SBATCH --mem=8192',
    '#SBATCH --output "/home/z5044992/InputOutput/DATA_EN_3/slurm/slurm-%j.out"',
    'module load python/3.6',
    'source /home/z5044992/python_venv/bin/activate',
    'python /home/z5044992/InputOutput/en/morePVs/morePVs.py -b /home/z5044992/InputOutput/DATA_EN_3 -p '+ new_project +' -s '+ um.find_between(csv_name,'study_','.csv') + ' -t False',
    'deactivate',
    'module unload python/3.6'
    ]).apply(lambda x: x.replace('\r\n', '\n'))
    # nb replace unix line ending
    bash_name = 'f'+ um.find_between(csv_name,'hpc','.csv') + '.bat'
    bash_file = os.path.join(bash_path, bash_name)
    pd.DataFrame(bash_content).to_csv(bash_file, index=False,header=False,
                                      quoting=csv.QUOTE_NONE, line_terminator='\n')


    putty_script +=['sbatch '+ bash_file]

# Create PuTTY Script:
# --------------------    

putty_file = os.path.join(bash_path, 'putty.txt')
putty_out = pd.DataFrame (putty_script)
putty_out.to_csv(putty_file, index=False,header=False,
                                      quoting=csv.QUOTE_NONE, line_terminator='\n')


	

