import sys
sys.path.append('C:\\PYTHONprojects\\en')
sys.path.append('C:\\PYTHONprojects')
sys.path.append('C:\\PYTHONprojects\\utilities')
import morePVs_output as opm
import morePVs as mpv
import os
import en_utilities as um
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.lines as mlines
import shutil
import seaborn as sns



arrangement = 'en_pv'
fontsize=12
alpha=0.6

# Create REVISED peak_charging_period
timeseries = 'C:\\Users\\z5044992\\Documents\\MainDATA\\DATA_EN_4\\studies\\EN2_bat2\\outputs\\energy5_G\\timeseries\\hpc000_000_bau_vb_site_sh_t_all_site_G_01.csv'
df = pd.read_csv(timeseries, parse_dates=['timestamp'], dayfirst=True)
df = df.set_index('timestamp')
ts = df.index
days = ts[ts.weekday.isin([0, 1, 2, 3, 4])]
dst_start = pd.Timestamp('2013-10-06 02:00:00')
dst_end = pd.Timestamp('2013-04-07 02:00:00')
tsy = days
seasonal_time = {}
seasonal_time['summer'] = tsy[(tsy >= pd.Timestamp('1/01/2013 00:00:00'))
                              & (tsy < dst_end)].join(tsy[(tsy >= dst_start)], how='outer')
seasonal_time['winter'] = tsy[(tsy >= dst_end) & (tsy < dst_start)]

winter_days_affected = seasonal_time['winter']
summer_days_affected = seasonal_time['summer']

winter_period = \
    winter_days_affected[
        (winter_days_affected.time >= pd.Timestamp('14:00:00').time()) \
        & (winter_days_affected.time < pd.Timestamp('20:00:00').time())]

summer_period = \
    summer_days_affected[
        (summer_days_affected.time >= pd.Timestamp('13:00:00').time()) \
        & (summer_days_affected.time < pd.Timestamp('19:00:00').time())]
demand_period = winter_period.join(summer_period, 'outer').sort_values()

# Run this cell only once to collate peak demand data from timeseries files
# for evening discharge and charge-priority strategies

def main(project, study_name):
    base_path='C:\\Users\\z5044992\\Documents\\MainDATA\\DATA_EN_4\\studies'
    opath = os.path.join(base_path,project,'outputs',study_name)
    ipath = os.path.join(base_path,project,'inputs')

    fname = os.path.join(opath,study_name+'_results.csv')
    iname = os.path.join(ipath,'study_'+study_name+'.csv')
    df = pd.read_csv(fname, index_col = [0])
    df_in = pd.read_csv(iname, index_col = [0])
    df = df.merge(df_in,left_index = True, right_index=True)
    for c in df.columns:
        if '_x' in c:
            nc = c[:-2]
            df.rename(columns={c:nc}, inplace=True)
        if '_y' in c:
            df= df.drop([c],axis=1)

    # ---------------
    # Organise labels
    # ---------------
    df.loc[:,'site'] = df.loc[:,'load_folder'].apply(lambda x : x[-1])

    # get pv sizes for maximum pv systems
    # -----------------------------------
    maximums={}
    pv_ref_file='C:\\Users\\z5044992\\Documents\\MainDATA\\DATA_EN_3\\reference\\capex_pv_lookup.csv'
    pv_ref=pd.read_csv(pv_ref_file)
    pv_ref = pv_ref.set_index('pv_cap_id')
    for i in pv_ref.index:
        if 'max' in i and 'site' in i:
            site = um.find_between(i,'_','_')
            maximums[site] = pv_ref.loc[i,'kW']
    df['pv_filename'].fillna('zero',inplace=True)

    for s in df.index:
        site = df.loc[s,'load_folder'][-1]
        df.loc[s,'site']=site
        df.loc[s,'short_label']= df.loc[s,'scenario_label'].split('_')[
                    len(df.loc[s,'scenario_label'].split('_'))-2] + \
                    '_'+ \
                    df.loc[s,'scenario_label'].split('_')[
                    len(df.loc[s,'scenario_label'].split('_'))-1]


    # get timeseries data and create dfs with peak demand
    # -----------------------------------------
    ts_path = os.path.join(base_path,project,'outputs',study_name,'timeseries')
    tslist = [f for f in os.listdir(ts_path) if 'hpc094_403' in f]

    process_path = os.path.join(base_path,project,'outputs',study_name,'process')
    if not os.path.exists(process_path):
        os.makedirs(process_path)

    # paths for peak demand files
    pf = 'Xpeak_demand_peak_period.csv'
    peakFile = os.path.join(process_path, pf)
    pf10 = 'Xpeak_demand_10_peak_period.csv'
    peakFile10 = os.path.join(process_path, pf10)

    # Calc single highest demand:
    dfpeak = pd.DataFrame(index = df['short_label'], columns =[str(r).zfill(2) for r in range(1,51)])
    for tsf in tslist:
        short_label = tsf[0:10]
        vb = tsf[-6:-4]
        tsFile = os.path.join(ts_path, tsf)
        dfts = pd.read_csv(tsFile, parse_dates=['timestamp'],dayfirst=True)
        dfts=dfts.set_index('timestamp')
        dfts = dfts.loc[demand_period]
        dfpeak.loc[short_label,vb] = dfts['grid_import'].max()
    um.df_to_csv(dfpeak,peakFile)
    print('saved: ', peakFile)


    # Calc mean of 10 higest demands:
    dfpeak10 = pd.DataFrame(index = df['short_label'], columns =[str(r).zfill(2) for r in range(1,51)])
    for tsf in tslist:
        short_label = tsf[0:10]
        vb = tsf[-6:-4]
        tsFile = os.path.join(ts_path, tsf)
        dfts = pd.read_csv(tsFile, parse_dates=['timestamp'],dayfirst=True)
        dfts=dfts.set_index('timestamp')
        dfts = dfts.loc[demand_period]
        dfpeak10.loc[short_label,vb] = dfts['grid_import'].nlargest(10).mean()
    um.df_to_csv(dfpeak10,peakFile10)
    print('saved: ', peakFile)

if __name__ == "__main__":

    default_project = 'EN2_x'
    default_study='xenergy2_G'
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

    # for base_study in base_studies:
    #     for site in sitelist:
    #         # -------------------------------
    #         # combine  input and result files
    #         # -------------------------------
    #
    #         sitelist = ['H', 'G', 'J', 'F']
    #         base_studies = ['xenergy2_']
    #         study_name = base_study + site

    main(project=project,
         study_name=study)