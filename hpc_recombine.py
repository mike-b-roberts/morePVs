import os
import en_utilities as um
import pandas as pd
import shutil
import numpy as np
import stat
import subprocess
import en_utilities as um

# Input parameters:
# -----------------
project='EN1a_pv_bat4'
study = 'siteJ_bat4_2'


# Establish paths etc
# -------------------
new_project = project+'_hpc'
base_path = '/home/z5044992/InputOutput/DATA_EN_3/studies'
bash_root = '/home/z5044992/InputOutput/en/morePVs/bash_files'


# Paths for hpc outputs
np_path =os.path.join(base_path,new_project)
if not os.path.exists (np_path):
    os.makedirs(np_path)
i_path =os.path.join(np_path,'inputs')
hpc_path =os.path.join(np_path,'outputs')

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
bash_path = os.path.join(bash_root,new_project)




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
        os.remove(spath)
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

        os.remove(pvpath)
    fff = os.path.join(hpc_path, ff)
    os.remove(fff)

# Delete hpc input files and bash files
# -------------------------------------
in_list = os.listdir(i_path)
for f in [f for f in i_path if 'hpc' in f and '.csv' in f]:
    fname = os.path.join(i_path, f)
    getridof(fname)

bash_list = os.listdir(bash_path)
for f in [f for f in bash_path]:
    fname = os.path.join(i_path, f)
    getridof(fname)
getridof(bash_path)
