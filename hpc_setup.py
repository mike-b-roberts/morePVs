import os
import en_utilities as um
import pandas as pd
import shutil
import numpy as np
import csv

project='EN1a_pv_bat4'
study = 'example2'
base_path='/home/DATA_EN_3/studies'
i_path =os.path.join(base_path,project,'inputs')
i_name='study_'+study+'.csv'
i_file = os.path.join(i_path,i_name)
o_path = os.path.join(i_path,'for_hpc_'+study)
if not os.path.exists (o_path):
    os.makedirs(o_path)
df= pd.read_csv(i_file)
df = df.set_index('scenario')

# Split csvs
maxjobs = 100
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
    o_name = 'study_'+study+'_hpc'+ str(job)+'.csv'
    csv_list += [o_name]
    o_file = os.path.join(o_path,o_name)
    dfn.to_csv(o_file)

# Create bash files
bash_path = os.path.join(i_path,'bash_'+study)
if not os.path.exists (bash_path):
    os.makedirs(bash_path)
for csv_name in csv_list:
    #
    bash_content = pd.Series([
    '#!/bin/bash',
    '#SBATCH --mail-user=m.roberts@unsw.edu.au',
    '#SBATCH --mail-type=ALL',
    '#SBATCH --time=12:00:00',
    '#SBATCH --ntasks=1',
    '#SBATCH --cpus-per-task=4',
    '#SBATCH --mem=8192',
    '#SBATCH --output "/home/z5044992/InputOutput/DATA_EN_3/slurm/slurm-%j.out"',
    'module load python/3.6',
    'source /home/z5044992/python_venv/bin/activate',
    'python morePVs.py -b /home/z5044992/InputOutput/DATA_EN_3 -p '+ 'for_hpc_'+study+' -s '+ csv_name + ' -t False',
    'deactivate',
    'module unload python/3.6'
    ]).apply(lambda x: x.replace('\r\n', '\n'))
    # nb replace unix line ending
    bash_name = 'f'+ um.find_between(csv_name,'hpc','.csv') + '.bat'
    bash_file = os.path.join(bash_path, bash_name)
    pd.DataFrame(bash_content).to_csv(bash_file, index=False,header=False,
                                      quoting=csv.QUOTE_NONE, line_terminator='\n')
