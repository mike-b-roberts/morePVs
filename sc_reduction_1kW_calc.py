import sys
sys.path.append('C:\\PYTHONprojects\\en')
sys.path.append('C:\\PYTHONprojects')
sys.path.append('C:\\PYTHONprojects\\utilities')

import os

import pandas as pd
from utilities import utility_module as um


def main(project, study_base):
    base_path='C:\\Users\\z5044992\\Documents\\MainDATA\\DATA_EN_4\\studies'
    sites = ['H','I','G','J','F']
    max_pdr=pd.DataFrame()

    for site in sites:
        study_name = study_base+site

        opath = os.path.join(base_path,project,'outputs',study_name)
        ppath = os.path.join(base_path,project,'outputs',study_name,'process')

        fname = os.path.join(opath, study_name+'_results_process.csv')
        pd10name = os.path.join(ppath, 'peak_demand_10_peak_period.csv')
        df = pd.read_csv(fname, index_col=[0])

        # Add kWh _unit and kWp_unit columns to df:
        # get pv sizes for maximum pv systems
        # -----------------------------------
        maximums = {}
        pv_ref_file = 'C:\\Users\\z5044992\\Documents\\MainDATA\\DATA_EN_3\\reference\\capex_pv_lookup.csv'
        pv_ref = pd.read_csv(pv_ref_file)
        pv_ref = pv_ref.set_index('pv_cap_id')
        df['pv_filename'].fillna('zero', inplace=True)
        for i in pv_ref.index:
            if 'max' in i and 'site' in i:
                site = um.find_between(i, '_', '_')
                maximums[site] = pv_ref.loc[i, 'kW']
        for s in df.index:
            site = df.loc[s, 'load_folder'][-1]
            df.loc[s, 'site'] = site
            arrangement = df.loc[s, 'arrangement']
            if df.loc[s, 'pv_filename'] == 'zero':
                df.loc[s, 'kWp_unit'] = 0
            elif 'max' in df.loc[s, 'pv_filename']:
                df.loc[s, 'kWp_unit'] = maximums[site] / df.loc[s, 'number_of_households']
            elif arrangement == 'bau_bat':
                df.loc[s, 'kWp_unit'] = 0
            else:
                df.loc[s, 'kWp_unit'] = float(df.loc[s, 'pv_filename'][-9]) + float(df.loc[s, 'pv_filename'][-7]) / 10

            if arrangement in ['en', 'en_pv']:
                df.loc[s, 'kWh_unit'] = df.fillna(0).loc[s, 'central_battery_capacity_kWh'] / df.loc[
                    s, 'number_of_households']
            elif ('btm_i' in arrangement) or \
                    (arrangement == 'bau_bat'):
                df.loc[s, 'kWh_unit'] = (df.fillna(0).loc[s, 'all_battery_capacity_kWh'] * df.loc[
                    s, 'number_of_households'] + \
                                         df.fillna(0).loc[s, 'cp_battery_capacity_kWh']) / df.loc[
                                            s, 'number_of_households']


        # for each battery strategy find increase in SC from 0kWh to 2 kWh
        strategies = []
        if 'central_battery_strategy' in df.columns:
            strategies += df.central_battery_strategy.drop_duplicates().dropna().tolist()
        if 'all_battery_strategy' in df.columns:
            strategies += df.all_battery_strategy.drop_duplicates().dropna().tolist()

        arrangements = {'en_': ['en_pv'],
                        'i_': ['btm_i_c']}

        # Slice df for kWp=1
        df = df.loc[df.kWp_unit == 1]
        delta_sc_en = pd.DataFrame(columns = sites, index = strategies)
        delta_sc_i = pd.DataFrame(columns = sites, index = strategies)

        for strategy in strategies:
            delta_sc_en.loc[strategy, site] = df.loc[(df.kWh_unit == 2.0) & \
                              (df.arrangement== 'en_pv') & \
                              (df.central_battery_strategy == strategy)] - \
                        df.loc[(df.kWh_unit == 0) & \
                                  (df.arrangement== 'en_pv')]

            delta_sc_i.loc[strategy, site] = df.loc[(df.kWh_unit == 2.0) & \
                              (df.arrangement =='btm_i_c') & \
                              (df.all_battery_strategy == strategy)] - \
                       df.loc[(df.kWh_unit == 0) & \
                              (df.arrangement.i=='btm_i_c')]

    outpath = os.path.join(base_path, project, 'outputs', study_base)
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    outfile1 = os.path.join(outpath, 'delta_sc_en_1kwp_2kwh.csv')
    delta_sc_en.to_csv(outfile1)
    outfile2 = os.path.join(outpath, 'delta_sc_i_1kwp_2kwh.csv')
    delta_sc_en.to_csv(outfile2)

if __name__ == "__main__":
    main(project = 'EN2_x',
         study_base = 'xenergy4pd_')