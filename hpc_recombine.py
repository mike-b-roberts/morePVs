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
project = 'EN1_rerun3'
study = 'value11b'


# Establish paths etc
# -------------------
new_project = project+'_hpc'
base_path = 'C:\\Users\\z5044992\\Documents\\MainDATA\\DATA_EN_4\\studies'



# Paths for hpc outputs
np_path = os.path.join(base_path,new_project)
if not os.path.exists (np_path):
    os.makedirs(np_path)
i_path =os.path.join(np_path,'inputs')
hpc_path =os.path.join(np_path,'outputs')


# Path for combined output:
o_path = os.path.join(base_path,project,'outputs')
if not os.path.exists(o_path):
    os.makedirs(o_path)
so_path = os.path.join(o_path,'scenarios')
if not os.path.exists(so_path):
    os.makedirs(so_path)
po_path = os.path.join(o_path,'pv')
if not os.path.exists(po_path):
    os.makedirs(po_path)
to_path = os.path.join(o_path,'saved_tariffs')
if not os.path.exists(to_path):
    os.makedirs(to_path)





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
            df[type] = df[type].append(df_s, sort=False)
            os.remove(small_file)

for type in types:
    df[type] = df[type].sort_index()
    o_name = study + '_' + type
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
            newname = s[0:8] + s[15:]
            nf = os.path.join(so_path, newname)
            shutil.move(sf, nf)
        # os.rmdir(spath)
    #pvpath = os.path.join(hpc_path, ff, 'pv')
    # # -------------
    # # copy PV files
    # # -------------
    # if os.path.exists(pvpath):
    #     slist = os.listdir(pvpath)
    #     for s in slist:
    #         sf = os.path.join(pvpath, s)
    #         nf = os.path.join(po_path, s)
    #         shutil.move(sf, nf)
    # -------------
    # copy tariff files
    # -------------
    # WRONG! - this just overwrites teh last tariff_file.
    # Need to combine them into a single file or change the names
    tariffpath = os.path.join(hpc_path, ff, 'saved_tariffs')
    if os.path.exists(tariffpath):
        slist = os.listdir(tariffpath)
        for s in slist:
            sf = os.path.join(tariffpath, s)
            nf = os.path.join(to_path, s)
            shutil.move(sf, nf)

        # os.rmdir(pvpath)
    fff = os.path.join(hpc_path, ff)
    # os.rmdir(fff)
