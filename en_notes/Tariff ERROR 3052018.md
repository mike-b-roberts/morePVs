Tariff Error 30/5/2018

*jesus fuck*

`tariff_lookup.csv` has error in theEASO_TOU` tariff and presumably all derivative tariffs (which are many).

peak, shoulder periods are correct, but Off peak period is set to `20:00-24:00` instead of `22:00 - 24:00`

Because off-peak is set *after* shoulder and peak (order of the tariffs in the spreadsheet), it takes precedent.

This could affect results for :

* ASPRC 2017
* EnergyCon 2018
* En1 (with supervisors)
* En2 (battery ) - underway

__Affected tariffs:__

| EASO_TOU            |
| ------------------- |
| EASO_TOU_5pc        |
| EASO_TOU_10pc       |
| EASO_TOU_15pc       |
| EASO_TOU_15pc_FIT12 |
| EASO_TOU_15pc_FIT8  |
| EASO_TOU_20pc       |
| EASO_TOU_25pc       |
| EASO_TOU_30pc       |
| EASO_TOU_35pc       |
| EASO_TOU_40pc       |
| EASO_TOU_GP         |
| STC_15              |
| STC_20              |



__Network Tariffs:__

All network tariffs and derived tariffs are OK



***Make a list of all studies to run and all charts to plot***



### Actions:

- [x] Backup `tariff_lookup.csv  ` and make corrections
- [x] __Energy Con__
   - Run studies (identifed from Notebook `ASPRC / ENERGYCON 2017` )
   - `envb` :
     *  `envb_6r`  - full roof PV,
     *  `envb_6s` - reduced PV (losing least optimal roof surfaces)
     * `envb_6u` big PV, with FIT = 12.5c
     * `envb_6v` - Small PV with FIT = 12.5c
     * In fact, `_6r` == `_6u` and `_6s` == `_6v` and both have fit = 9.5c and 11.5c          * scatter plots came from 6r.
     * (`envb_6r1`) was a duplicate of `_6r`
   - __SO:__ Use `_6r_REVISED` and `_6_REVISED` but there will be issues with changed script. `bash_energycon.bat`
     - (Issues: change `scenario` identifier, rename `pv_id` as `pv_cap_id`, and `capex_id` as `en_capex_id`, add `a_rate` = 0.06 and `a_term` = 8 and 12 Don't consider inverter replacement, so use  `G_maxflush_3` and `G_reduced_3` for `pv_capex_id` )
     - Still tariff issue:
       - `STC` tariffs have no value between 20:30 and 22:00 weekday only
       - All tariffs have no rate for 00:00
       - Issue remains with old `tariff_lookup`  and applies to network tariffs too, but was not there last week
       - Changed end time from `23:59:00` to `23:58:59` and resolved?
       - ***tick: sorted***
   - __Plot charts:__
     - scatters: `STS40` , `STC15` (scenarios: 5 and 6)
     - Use `morePVs_output` and adapt `scat_cust_sav_vs_sc_per_tariff`
     - __PROBLEM:__ *** VBs have changed.*** Look up for SCM: either use old version or new, but list of customers has changed (due to re-filling of sgsc data, and subsequent regeneration of virtual buildings). Options are:
     1. use the old (wrongly filled data and the old list (`vb_id_log.csv') and old `sgsc_self_consumption_metric.csv')
     	* ***Do this for `energycon2018`***
   Use `vb_id_log_original.csv` for vb look-up and `h_all_site_G_original` for load profiles results are unexpected (no relationship between savings and scm). Just to be sure, try this with the old 'tariff_lookup.csv`
   Re-try with old tariffs and get expected relationship.
     	*Goddamn.*
     	* ***tick: SORTED***

     results are processed (and barcharts) in
     `C:\Users\z5044992\Documents\MainDATA\DATA_EN\studies\envb6\outputs\SiteG - 6i&6j - summary.xlsx`
     Sheet: `6r&s - CORRECTED AGAIN`


     2. use the new data, new list (`vb_index.csv`) and
     	* Then need to re-create the sc metric
     	* *** Do this for  `EN1` `EN1a_bat` and `EN2` 


   - Compare
- [x] EN1: 
   * Run studies
     * ` EN1_value_of_pv2` : `value7` : Rename as `value8` and run as separate sites
   * Plot charts
   * Compare
- [ ] EN2 - Batteries
   * Run studies
    * *** Running bat3_3, 4, 5 and 6 overnight 30-3-18
     * (only `_3` and `_5` completed)
   * Plot charts
   * Compare
- [ ] APSRC - will tell from EN1 results
   * Rerun and plot if necessary
   * `envb_7a` and `envb_7b`



__12/6/18__

##Results of re-run with corrected tariffs

###EN1

`value_8`

- [x] Combine inputs and outputs

- [x] Plot charts & Compare:

  - [x]  Bar Charts  `EN1_barcharts_value8` 

    ​	 with `parent_retail` = `TOU12_FIT8`

    ​	 with BAU / BTM retail = `EASO_TOU_15pc_FIT8`

    __RESULT__ Increased costs, but no significant change to relative costs

    - [x] Replace charts in `EN1` paper

  - [x]  EN Costs vs `a_term`  plotted by `EN1_value8  LINEPLOTS - % bau`

    __RESULT:__ reduced `%BAU` 

    - [x] Replace charts in `EN1` paper

  - [x] `%EN` vs `kWp` plotted by `EN1_value8 en pv - LINEPLOTS - %en`

    __RESULT: NO CHANGE__

  - [x] BTM: `%BAU` vs `kWp`

    __RESULT:__ Significant change, particularly for PPA.

    - [x] Replace charts in `EN1` paper

### EN2

`EN1a_pv_bat3` `siteJ`  `bat3_3`, `3_4`, `3_5` and `3_6`

__SEE: `n2_storage_3.md__`



##<u>Tariff Error #2</u>

***22/6/18***

goddamnit demand charge error (see `Systematic testing.md`)

Rerun:

- [ ] `APSRC`
  - ??
- [ ] `EN1`
  - [ ] `value9` renamed as `value10`



## 

