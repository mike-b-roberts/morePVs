import os
import en_utilities as um
import pandas as pd
import shutil
import numpy as np
import csv
import sys
import stat

# change
def main(project, study, base_path, maxjobs):


    # Variables
    # ---------
    num_threads = 2
    # See explanation: `https://stackoverflow.com/questions/51256738/multiple-instances-of-python-running-simultaneously-limited-to-35`


    # Establish paths etc
    # -------------------
    new_project = project+'_hpc'

    i_path = os.path.join(base_path,project,'inputs')
    i_name ='study_'+study+'.csv'
    i_file = os.path.join(i_path,i_name)

    np_path =os.path.join(base_path,new_project)
    if not os.path.exists (np_path):
        os.makedirs(np_path)
    new_i_path =os.path.join(np_path,'inputs')
    if not os.path.exists (new_i_path):
        os.makedirs(new_i_path)
    o_path = os.path.join(np_path, 'outputs')


    df = pd.read_csv(i_file)
    df = df.set_index('scenario')

    # Path for bash script files and for script
    # ----------------------------------------
    bash_path = '/home/z5044992/InputOutput/en/morePVs'

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
    for job in np.arange(num_jobs):
        dfn = pd.DataFrame(df1.iloc[0:joblength[job]],columns=df1.columns)
        df1 = df1.iloc[joblength[job]:]
        o_name = 'study_'+study+'_hpc'+ str(job).zfill(3) +'.csv'
        csv_list += [o_name]
        o_file = os.path.join(new_i_path ,o_name)
        dfn.to_csv(o_file)


    # # Create dict of execution lines:
    # # -------------------------------
    # execution_line ={}
    # for csv_name in csv_list:
    #     idx = csv_list.index(csv_name)
    #     study = um.find_between(csv_name,'study_','_')
    #     execution_line[idx] = \
    #         'python /home/z5044992/InputOutput/en/morePVs/morePVs.py -b /home/z5044992/InputOutput/DATA_EN_4 -p '\
    #         + new_project +' -s ' \
    #         + um.find_between(csv_name,'study_','.csv')
    # num_jobs = len(csv_list)





    # if not os.path.exists(bash_path):
    #     os.makedirs(bash_path)
    # for f in os.listdir(bash_path):
    #     xfile = os.path.join(bash_path, f)
    #     os.remove(xfile)
    # Create single batch bash file
    # -----------------------------
    bash_content = pd.Series([
        '#!/bin/bash',
        '#SBATCH --export OPENBLAS_NUM_THREADS='+str(num_threads),
        '#SBATCH --mail-user=m.roberts@unsw.edu.au',
        '#SBATCH --mail-type=FAIL',
        '#SBATCH --job-name='+study,
        '#SBATCH --array=0-'+str(num_jobs),
        '#SBATCH --nodes=2'
        '#SBATCH --time=96:00:00',
        '#SBATCH --ntasks=1',
        '#SBATCH --cpus-per-task=1',
        '#SBATCH --mem=8192',
        '#SBATCH --output "/home/z5044992/InputOutput/DATA_EN_4/slurm/slurm_%A_%a.out"',
        '#SBATCH --error "/home/z5044992/InputOutput/DATA_EN_4/slurm_err/err_%A_%a.err"',
        'module load python/3.6',
        'source /home/z5044992/python_venv/bin/activate',
        'python /home/z5044992/InputOutput/en/morePVs/morePVs.py -b /home/z5044992/InputOutput/DATA_EN_4 -p ' + new_project +' -s ' + study+'_hpc'+'$(printf "%03d" $SLURM_ARRAY_TASK_ID)',
        'deactivate',
        'module unload python/3.6',
        'cp -pr /home/z5044992/InputOutput/DATA_EN_4/studies/'+new_project+'/outputs/'+study+'_hpc'+'$(printf "%03d" $SLURM_ARRAY_TASK_ID) //share/scratch/z5044992/outputs',
        'rm -rf /home/z5044992/InputOutput/DATA_EN_4/studies/' + new_project + '/outputs/' + study + '_hpc' + '$(printf "%03d" $SLURM_ARRAY_TASK_ID)',
        'rm /home/z5044992/InputOutput/DATA_EN_4/studies/' + new_project + '/inputs/study_' + study+'_hpc'+'$(printf "%03d" $SLURM_ARRAY_TASK_ID)'+'.csv'
        ]).apply(lambda x: x.replace('\r\n', '\n'))
    # 'rm /home/z5044992/InputOutput/DATA_EN_4/studies/'+new_project+'/outputs/'+study+'_hpc'+'$(printf "%03d" $SLURM_ARRAY_TASK_ID)/*.*',
    # nb replace unix line ending
    bash_name = study+'.bat'
    bash_file = os.path.join(bash_path, bash_name)
    pd.DataFrame(bash_content).to_csv(bash_file,
                                      index=False,
                                      header=False,
                                      quoting=csv.QUOTE_NONE,
                                      line_terminator='\n')
    # Make script file executable:
    st = os.stat(bash_file)
    os.chmod(bash_file, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


if __name__ == "__main__":


    # Input parameters:
    # -----------------
    default_project = ''
    default_study = ''
    default_maxjobs = 60
    default_base_path = '/home/z5044992/InputOutput/DATA_EN_4/studies'

    # Import arguments - allows multi-processing from command line
    # ------------------------------------------------------------
    opts = {}  # Empty dictionary to store key-value pairs.
    while sys.argv:  # While there are arguments left to parse...
        if sys.argv[0][0] == '-':  # Found a "-name value" pair.
            opts[sys.argv[0]] = sys.argv[1]  # Add key and value to the dictionary.
        sys.argv = sys.argv[1:]
        # Reduce the argument list by copying it starting from index 1.
    if '-p' in opts:
        project = opts['-p']
    else:
        project = default_project
    if '-s' in opts:
        study = opts['-s']
    else:
        study = default_study
    if '-m' in opts:
        maxjobs = int(opts['-m'])
    else:
        maxjobs = default_maxjobs
    if '-b' in opts:
        base_path = opts['-b']
    else:
        base_path = default_base_path

main(project=project,
     study=study,
     base_path=base_path,
     maxjobs=maxjobs)
