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
study_root = 'xenergy1_'

sites = ['F'] #, 'G'] # ,'H','I','J']

# Establish paths etc
# -------------------
new_project = project+'_hpc'
base_path = 'C:\\Users\\z5044992\\Documents\\MainDATA\\DATA_EN_4\\studies'



# Paths for hpc outputs
np_path = os.path.join(base_path, new_project)
if not os.path.exists(np_path):
    os.makedirs(np_path)
i_path = os.path.join(np_path, 'inputs')
hpc_path = os.path.join(np_path, 'transfer','xenergy1')

#loop over sites
for site in sites:
    study = study_root + site

    # Path for combined output:
    o_path = os.path.join(base_path, project, 'outputs', study)
    if not os.path.exists(o_path):
        os.makedirs(o_path)
    so_path = os.path.join(o_path, 'scenarios')




    folder_list = [f for f in os.listdir(hpc_path) if 'hpc' in f and study in f and not '.csv' in f]



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
                    newname = s.split('_')[0]+'_'+s.split('_')[len(s.split('_'))-1]
                    nf = os.path.join(so_path, newname)
                    shutil.move(sf, nf)




        fff = os.path.join(hpc_path, ff)

