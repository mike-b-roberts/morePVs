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
project = 'EN2_x'
study_root = 'x_'


sites = ['F','G','H','I','J']

# Establish paths etc
# -------------------
new_project = project+'_hpc'
base_path = 'C:\\Users\\z5044992\\Documents\\MainDATA\\DATA_EN_4\\studies'



# Paths for hpc outputs
np_path = os.path.join(base_path, new_project)
if not os.path.exists(np_path):
    os.makedirs(np_path)
i_path = os.path.join(np_path, 'inputs')
hpc_path = os.path.join(np_path, 'outputs')

#loop over sites
for site in sites:
    study = study_root + site

    # Path for combined output:
    o_path = os.path.join(base_path, project, 'outputs', study)
    if not os.path.exists(o_path):
        os.makedirs(o_path)
    so_path = os.path.join(o_path, 'scenarios')
    if not os.path.exists(so_path):
        os.makedirs(so_path)
    po_path = os.path.join(o_path, 'pv')
    if not os.path.exists(po_path):
        os.makedirs(po_path)
    to_path = os.path.join(o_path, 'saved_tariffs')
    if not os.path.exists(to_path):
        os.makedirs(to_path)
    tso_path = os.path.join(o_path, 'timeseries')
    if not os.path.exists(tso_path):
        os.makedirs(tso_path)


    # ---------------------
    # combine results files
    # ---------------------
    # Combine results, customer_results and results_std
    types = ['customer_results.csv', 'results.csv', 'results_std_dev.csv']

    folder_list = [f for f in os.listdir(hpc_path) if 'hpc' in f and study in f and not '.csv' in f]
    df = dict(zip(types, [pd.DataFrame(), pd.DataFrame(), pd.DataFrame()]))

    #Combine results files:
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
            if len(slist) > 0:
                for s in slist:
                    sf = os.path.join(spath, s)
                    newname = s.split('_')[0]+'_'+ s.split('_')[1] + '_' + s.split('_')[len(s.split('_'))-1]
                    nf = os.path.join(so_path, newname)
                    shutil.move(sf, nf)
            os.rmdir(spath)
        pvpath = os.path.join(hpc_path, ff, 'pv')
        # # -------------
        # # copy PV files
        # # -------------
        # if os.path.exists(pvpath):
        #     slist = os.listdir(pvpath)
        #     for s in slist:
        #         sf = os.path.join(pvpath, s)
        #         nf = os.path.join(po_path, s)
        #         shutil.move(sf, nf)
        if os.path.exists(pvpath):
            os.rmdir(pvpath)
        # -------------
        # copy tariff files
        # -------------
        tariffpath = os.path.join(hpc_path, ff, 'saved_tariffs')
        if os.path.exists(tariffpath):
            slist = os.listdir(tariffpath)
            if len(slist) > 0:
                for s in slist:
                    sf = os.path.join(tariffpath, s)
                    newname = s[7:-4] + '_' + ff[-6:] + '.csv'
                    nf = os.path.join(to_path,newname)
                    shutil.move(sf, nf)
            os.rmdir(tariffpath)

        # -------------
        # copy timeseries files
        # -------------
        for tstype in [ 'timeseries', 'timeseries_b', 'timeseries_d']:
            tspath = os.path.join(hpc_path, ff, tstype)
            if os.path.exists(tspath):
                slist = os.listdir(tspath)
                if len(slist) > 0:
                    for s in slist:
                        sf = os.path.join(tspath, s)
                        newname = s[len(study) + 1:]
                        nf = os.path.join(tso_path, newname)
                        shutil.move(sf, nf)
                os.rmdir(tspath)

        fff = os.path.join(hpc_path, ff)
        os.rmdir(fff)
