

#en2_storage_3.md



Continued from `en2_storage_design2.md` 

Re run `EN1a_pv_bat3` `siteJ`  `bat3_3`, `3_4`, `3_5` and `3_6` with

* corrected tariff calcs ( see `Tariff ERROR 3052018.md`)

* 10 years `a_term`


- `siteJ_bat3_3` : `evening_discharge` `TOU9`
- `siteJ_bat3_4` : `double_cycle` `TOU9`
- `siteJ_bat_3_5` : `evening_discharge` `TOU12`
- `siteJ_bat3_6` : `double_cycle` `TOU12`

## Energy SS and SC calcs



`EN1a_pv_bat3_SCM_SSM_ kWh vs kWp`

__(NB these have incorrect SC and SS algorithms)__

| battery_strategy    | discharge | discharge | charge | charge | discharge2 | discharge2 |
| ------------------- | --------- | --------- | ------ | ------ | ---------- | ---------- |
| evening_discharge_1 | 18:00     | 20:00     |        |        |            |            |
| double_cycle_1      | 18:00     | 20:00     | 22:00  | 7:00   | 7:00       | 14:00      |





###Self-Sufficiency

![ssm_kWp_site_J_evening_discharge_1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_3\plots\ssc_ssm\ssm_kWp_site_J_evening_discharge_1.jpg)

![ssm_kWh_site_J_evening_discharge_1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_3\plots\ssc_ssm\ssm_kWh_site_J_evening_discharge_1.jpg)

### Self-Consumption

![scm_kWp_site_J_evening_discharge_1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_3\plots\ssc_ssm\scm_kWp_site_J_evening_discharge_1.jpg)

![scm_kWh_site_J_evening_discharge_1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_3\plots\ssc_ssm\scm_kWh_site_J_evening_discharge_1.jpg)

* storage above 3.0 kWh / unit (or less? - 2.5?) does not increase SS or SC any further

  ### Double-Cycle - charging from grid

  ![ssm_kWp_site_J_double_cycle_1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_4\plots\ssc_ssm\ssm_kWp_site_J_double_cycle_1.jpg)

![scm_kWp_site_J_double_cycle_1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_4\plots\ssc_ssm\scm_kWp_site_J_double_cycle_1.jpg)

* `double_cycle` reduces SS and SC (due to grid import to charge battery and cycle losses)
* Purpose of `double_cycle` is $ arbitrage, not maximising SC or SS, so all good.
* (see below): decreases with kWh for `double_cycle` (due to increased losses)![ssm_kWh_site_J_double_cycle_1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_4\plots\ssc_ssm\ssm_kWh_site_J_double_cycle_1.jpg)



###Increase in SC compared to zero storage

![delta_sc_kWp_site_J_en_pv_evening_discharge_1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_3\plots\ssc_ssm\delta_sc_kWp_site_J_en_pv_evening_discharge_1.jpg)

### Which gives more information?

 * 2D plots of SC and SS vs kWh and kWp
 * 2D Plots of delta(SC) and delta(SS)
 * 3D plots of SC & SS
 * 3D plots of delta(SS)  and delta (SC)



###3D Plots

![scm_3D_site_J_evening_discharge_1_en_pv](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_3\plots\ssc_ssm\scm_3D_site_J_evening_discharge_1_en_pv.jpg)

![delta_sc_3D_site_J_evening_discharge_1_en_pv](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_3\plots\ssc_ssm\delta_sc_3D_site_J_evening_discharge_1_en_pv.jpg)



![delta_ss_3D_site_J_evening_discharge_1_en_pv](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_3\plots\ssc_ssm\delta_ss_3D_site_J_evening_discharge_1_en_pv.jpg)

# Financials:

### %BAU

__NB__ These are all for embedded network costs `en_capex_med`

`siteJ_bat3_3` : `evening_discharge` `TOU9`

![bau_3D_site_J_en_pv_evening_discharge_1_1000.0](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_3\plots\percentage_bau\bau_3D_site_J_en_pv_evening_discharge_1_1000.0.jpg)

![bau_3D_site_J_en_pv_evening_discharge_1_250.0](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_3\plots\percentage_bau\bau_3D_site_J_en_pv_evening_discharge_1_250.0.jpg)



## AS % EN:

![en_3D_site_J_en_pv_evening_discharge_1_500.0](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_3\plots\percentage_en\en_3D_site_J_en_pv_evening_discharge_1_500.0.jpg)

![en_3D_site_J_en_pv_evening_discharge_1_250.0](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_3\plots\percentage_en\en_3D_site_J_en_pv_evening_discharge_1_250.0.jpg)

* For zero storage, PV up to 1kWp/unit approx reduces costs

###Repeat with parent retail tariff = TOU12

`siteJ_bat_3_5` : `evening_discharge` `TOU12`

![en_3D_site_J_en_pv_evening_discharge_1_1000.0](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_5\plots\percentage_en\en_3D_site_J_en_pv_evening_discharge_1_1000.0.jpg)

Bigger range of PV having downward effect on costs

Storage still no  benefit at 1000$/kWh capex

## Focus on $250 / kWh



![en_3D_site_J_en_pv_evening_discharge_1_250.0](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_5\plots\percentage_en\en_3D_site_J_en_pv_evening_discharge_1_250.0.jpg)

For smaller PV sizes, storage increases costs

For large PV, BESS up to 2-3 kWh/unit reduces costs (but still more than EN with no PV)

![en_kWp_site_J_en_pv_evening_discharge_1_250.0](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_5\plots\percentage_en\en_kWp_site_J_en_pv_evening_discharge_1_250.0.jpg)

![en_kWh_site_J_en_pv_evening_discharge_1_250.0](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_5\plots\percentage_en\en_kWh_site_J_en_pv_evening_discharge_1_250.0.jpg)



__*THESE ARE ALL OVER 10 YEARS*__ for PV as well as battery, and ***all are better than BAU:***

###![bau_kWh_site_J_en_pv_evening_discharge_1_250.0](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_5\plots\percentage_bau\bau_kWh_site_J_en_pv_evening_discharge_1_250.0.jpg)

## Repeat for 20 years

__NB: Include battery / inverter replacement:__

- After 10 years or 7300 cycles, whichever is soonest.

- Calculating cycles as % of max DOD 

  Will reduce costs as PV capex is spread over 20 years



## Repeat for 4 more sites:

As well as `a26_f4_cp44`

`a52_f3_cp27` 
`a48_f4_cp09`
`a44_f4_cp17`
`a20_f5_cp37`

## Other scenarios to consider: (Do it now in `EN2_bat`???)

* Higher future parent tariffs? ***YES***

* Seasonal TOU residential tariffs (for BAU)? ***NO***

* Flat rate BAU? ***NO?***

* TOU FiTs? ***NO?***

* Finer resolution of kWh and kWp?? (500 W / Wh?)  ***NO***

* OTHER BATTERY STRATEGIES:

  * Different charge and discharge periods?
  * Constrained charge and discharge rates?
  * Peak shaving?

  

  # Anna / Iain suggestions

* __Debugging:__

   * simple examples

  * extreme testing

    "spend a day" *hahahahahahahahahahaha* (a month later....)

* __Plots:__

  * delta(SC), delta(SS) too confusing - lose it
  * 3D  but with 2D to illustrate
  * Add to legend: `capex_med`, `a_term`
  * ***?? Plot savings instead of total cost?? ***

* __Demand Charge:__

  (David Leitch podcast)

  __1) Look at it:__

  * Look at delta (demand charge) for all scenarios
  * Look at delta (Peak Demand) for all scenarios
  * Look at peaks: plot vs frequency

  __2) Ex post calc of impact:__

  * What if we *could* get rid of or reduce  PD within bounds of possibility with this battery
  * Is there available battery capacity at time of peak demand?
  * What additional saving  *could* be achieved?

* __Strategies:__

  * Try slower discharge (3C, 4C) or starting later and see effect on total $ and on demand charge / peak demand
  * Strategies may vary for different relative load/kWp/kWh
  * Double Cycle: add afternoon grid top-up (if no PV)

* __Variability / Distribution:__

  * Plot variability across VBs: Box plot?

* __Tariffs:__

  * Try higher parent tariff
  * try with FiT (Reduced value for battery)
  * No FiT: distinguish between 2 scenarios:
    * zero export (constrained)
    * export but no payment 
    * how does this affect SC and SS metrics?

* __Discussion:__ 

  * Use of H/W as more cost-effective storage 
  * Shortcomings of battery control strategy

# DATA_EN_4\studies\EN2_bat2\

jupyter notebok: __`SETUP_EN2_bat`__ creates study files

Energy Studies:

- * log timeseries of total en imports vs total load for peak demand analysis
  * ***PROBLEMATIC:*** because hpc storage quota (25GB) is consumed.
    * some timeseries  up to 18MB!!!
  * So, reduced level of logging: Only: total load, total import
    * 

## Energy

__Question:__

`bau` scenario with individual batteries: does it need a new arrangement name `bau_bat` ??

- Yes!

  ```
   'bau' arrangement has no batteries by definition
  ```

Therefore `bau_bat` - put it in the instructions and check the code`

`bat_energy1`

*  `en` and `en_pv` with central battery 

*  `btm_i_c` with individual bats.

  * Also `bau` with individual batteries `bau_bat`

__BATTERY SIZES:__

~~Individual: Units: [1,2,3,4]~~

~~​		 CP: cpr/(1-cpr).n.[1,2,3,4]~~

~~Combined CP + n.Units~~

~~	n(1+cpr/(1-cpr)).[1,2,3,4]~~

Therefore if 1kWh applied directly to each unit plus CP as above, 

~~then *total* storage is between 1.1 and 2.3 kWh per unit. (site J is 1.5)~~

~~QUESTION: Use 1,2,3,4 kWh per unit PLUS cp battery, or 1,2,3,4kWh per unit INCLUDING CP battery?~~

~~***HOW ABOUT:***~~

~~0.5,1,1.5,2,2.5, 3.0 PLUS CP~~

***Revisit this - look at consistency of sizing for PV and BESS***

So, revert to total battery / # units = [1,2,3,4]

```
bat(tot) = n x [1,2,3,4]
bat(cp) = n x cpr x [1,2,3,4]
bat(unit) = (1-cpr) x [1,2,3,4] 
```

| Site | Total Battery / unit<br /> kWh | Total battery<br />kWh | CP battery<br /> kWh | Unit Battery<br /> kWh |
| ---- | ------------------------------ | ---------------------- | -------------------- | ---------------------- |
| I    | 1                              | 48                     | 4.32                 | 0.91                   |
| G    | 1                              | 44                     | 7.48                 | 0.83                   |
| C    | 1                              | 34                     | 11.22                | 0.67                   |
| J    | 1                              | 26                     | 11.18                | 0.57                   |
| F    | 1                              | 20                     | 7.2                  | 0.64                   |

##SCALABLE BATTERY

- add scalable battery to `morePVs` 
- add `charge_c_rate` and `discharge_c_rate`
- test using 2 day cycle:

**all good**

## Run 'em!



`bat_energy1_F`, `_G`, `_H`, `_I`, `_J` prepared -sent to hpc to run 30/7/18

Between 50 and 100 scenarios per site, so with m=48, 1 or 2 scenarios per process. hpc running one or 2 sites at a time (to avoid storage issues)  takes approx 90 mins.

Now, __finance:__

e.g site J: 2761 scenarios. with just 2 battery strategies. No timeseries logging, which will save space.

So.... estimate:55* 50 mins... 60 hours? per site. But ... try more processes 96 (x num threads =8 +1) < 1024

##Results Plotting:

### SC and SS:  `EN2_bat2  SCM_SSM_ kWh vs kWp EN.ipynb`

### Peak Demand: `EN2_bat2  Peak Demand.ipynb`

