import os
import en_utilities as um
import pandas as pd
import shutil
import numpy as np
import stat
import subprocess
import en_utilities as um
import sys

def main(project, study, base_path, delete_input, delete_output):

    # Establish paths etc
    # -------------------
    new_project = project+'_hpc'
    bash_root = '/home/z5044992/InputOutput/en/morePVs/bash_files'

    # Paths for hpc outputs
    np_path =os.path.join(base_path, new_project)
    if not os.path.exists(np_path):
        os.makedirs(np_path)
    i_path = os.path.join(np_path, 'inputs')
    hpc_path = os.path.join(np_path, 'outputs')

    # Path for combined output:
    o_path = hpc_path
    if not os.path.exists(o_path):
        os.makedirs(o_path)
    so_path = os.path.join(o_path,'scenarios')
    if not os.path.exists(so_path):
        os.makedirs(so_path)
    po_path = os.path.join(o_path,'pv')
    if not os.path.exists(po_path):
        os.makedirs(po_path)

    # Bash file path
    bash_path = os.path.join(bash_root, new_project, study)

    # ---------------------
    # combine results files
    # ---------------------
    # Combine results, customer_results and results_std
    types = ['customer_results.csv', 'results.csv', 'results_std_dev.csv']

    folder_list = [f for f in os.listdir(hpc_path) if 'hpc' in f and not '.csv' in f]
    df = dict(zip(types, [pd.DataFrame(), pd.DataFrame(), pd.DataFrame()]))

    for ff in folder_list:
        folder_path = os.path.join(hpc_path, ff)

        for type in types:  # NB customer_results must come first
            file_list = [f for f in os.listdir(folder_path) if 'hpc' in f and '.csv' in f and type in f]
            for f in file_list:
                small_file = os.path.join(folder_path, f)
                df_s = pd.read_csv(small_file)
                df_s = df_s.set_index('scenario')
                df[type] = df[type].append(df_s)
                if delete_output:
                    os.remove(small_file)

    for type in types:
        df[type] = df[type].sort_index()
        o_name = 'hpc_' + study + '_' + type
        o_file = os.path.join(o_path, o_name)
        df[type].to_csv(o_file)

    # -------------------
    # copy scenario files
    # -------------------
    for ff in folder_list:
        spath = os.path.join(hpc_path, ff, 'scenarios')
        if os.path.exists(spath):
            slist = os.listdir(spath)
            for s in slist:
                sf = os.path.join(spath, s)
                nf = os.path.join(so_path, s)
                shutil.move(sf, nf)
        pvpath = os.path.join(hpc_path, ff, 'pv')
        # -------------
        # copy PV files
        # -------------
        if os.path.exists(pvpath):
            slist = os.listdir(pvpath)
            for s in slist:
                sf = os.path.join(pvpath, s)
                nf = os.path.join(po_path, s)
                shutil.move(sf, nf)
            os.rmdir(pvpath)
        fff = os.path.join(hpc_path, ff)
        if delete_output:
            os.rmdir(fff)

    # Delete hpc input files and bash files
    # -------------------------------------
    if delete_input:
        in_list = os.listdir(i_path)
        for f in [f for f in in_list if 'hpc' in f and '.csv' in f]:
            fname = os.path.join(i_path, f)
            os.remove(fname)

        bash_list = os.listdir(bash_path)
        for f in [f for f in bash_list]:
            fname = os.path.join(bash_path, f)
            os.remove(fname)
        os.rmdir(bash_path)

if __name__ == "__main__":

    # Input parameters:
    # -----------------
    default_project = ''
    default_study = ''
    default_delete_input = False
    default_delete_output = False
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
    if '-i' in opts:
        delete_input = opts['-i']
    else:
        delete_input = default_delete_input
    if '-o' in opts:
        delete_output = opts['-o']
    else:
        delete_output = default_delete_output
    if '-b' in opts:
        base_path = opts['-b']
    else:
        base_path = default_base_path

    main(project=project,
         study=study,
         base_path=base_path,
         delete_input=delete_input,
         delete_output=delete_output
         )
