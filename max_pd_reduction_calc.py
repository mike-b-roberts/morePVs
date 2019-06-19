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

        dfpd = pd.read_csv(pd10name, index_col=[0])
        delta_pdname = os.path.join(ppath, 'delta_pd10.csv')

        df_delta10 = pd.DataFrame()
        bau = dfpd.index[0]

        for s in dfpd.index:
            for vb in dfpd.columns:
                df_delta10.loc[s, vb] = -(dfpd.loc[s, vb] - dfpd.loc[bau,vb])/dfpd.loc[bau,vb] *100
            maxpd = df_delta10.loc[s].max()
            minpd = df_delta10.loc[s].min()
            meanpd = df_delta10.loc[s].mean()
            # df_delta10.loc[s, 'max'] = maxpd
            # df_delta10.loc[s, 'min'] = minpd
            df_delta10.loc[s, 'mean'] = meanpd
        df_delta10.to_csv(delta_pdname)

        # for each battery strategy find maximum Peak Demand reduction
        strategies = []

        if 'central_battery_strategy' in df.columns:
            strategies += df.central_battery_strategy.drop_duplicates().dropna().tolist()
        if 'all_battery_strategy' in df.columns:
            strategies += df.all_battery_strategy.drop_duplicates().dropna().tolist()

        arrangements = {'en_': ['en', 'en_pv'],
                        'i_': ['btm_i_c', 'bau_bat']}

        for strategy in strategies:
            for arrangement in list(arrangements.keys()):
                arrs = arrangements[arrangement]
                scenarios = []
                if 'central_battery_strategy' in df.columns:
                    scenarios += df.loc[(df.central_battery_strategy == strategy) &
                                        (df.arrangement.isin(arrs))]['scenario_label'].tolist()
                if 'all_battery_strategy' in df.columns:
                    scenarios += df.loc[(df.all_battery_strategy == strategy) &
                                        (df.arrangement.isin(arrs))]['scenario_label'].tolist()
                print(strategy, arrangement, len(scenarios))
                if len(scenarios) != 0:
                    pdr_metrics = []
                    for scenario in scenarios:
                        short_label = scenario.split('_')[2] + '_' + scenario.split('_')[3]
                        pdr_metrics += [df_delta10.loc[short_label,'mean']]
                        print(short_label)

                    max_scenario = df_delta10.loc[df_delta10['mean']==max(pdr_metrics)].index[0]
                    max_pdr.loc[(arrangement + '_' + strategy),site] = max(pdr_metrics)
                    max_pdr.loc[(arrangement + '_' + strategy),site+'_kWh'] = df.loc[df['scenario_label'] == study_name+'_'+max_scenario,'kWh_unit'].values[0]
                    max_pdr.loc[(arrangement + '_' + strategy),site+'_kWp'] = df.loc[df['scenario_label'] == study_name+'_'+max_scenario,'kWp_unit'].values[0]

    outpath = os.path.join(base_path, project, 'outputs', study_base)
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    outfile = os.path.join(outpath, 'max_pd_reduction.csv')
    max_pdr.to_csv(outfile)

if __name__ == "__main__":
    main(project = 'EN2_x',
         study_base = 'xenergy6pd_')