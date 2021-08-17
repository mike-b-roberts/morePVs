## Storage: Questions / Outputs

1. How does storage affect SC and SS of PV?

   * Self consumption and self sufficiency as function of kWp and kWh. 
   * 3D Plot?
   * file:/C:/PYTHONprojects/notes%20and%20notebooks/en_notes/en1_storage_design.md

2. How does aggregation affect *energy value* of kWh?

- needs careful framing: comparing 
  -  `btm_s_c` plus `bat_icp` 
  -  `btm_icp` plus `bat_icp` (storage shared in same proportions as PV)
  -  `en_pc_bat`
- metrics?
  - % increase SC relative to same arrangement with zero storage,
    -  plotted vs kWh for kWp scenarios (e.g 1, 1.5, 2 kWp / unit)

3. How does storage affect $ outcomes for building?

   * Answer: it increases costs., so....

   3a. What is max $ / kWh for batteries to reduce total site costs

   * en_pv?
   * for cp_only?

   3b. Given 2 or 3 $/kWh scenarios, what is optimum kWh capacity?

   4 For en_pv with shared bess, different strategies for increasing value:

   ​	* seasonal

   ​	* prioritise battery

   * grid charge/ cycling
   * target demand peaks

* Start with single site and reduced set of parameters, including multiple PVs:

    

    __Working Parameter List for `EN1a_pv_bat2` project `study_siteJ_bat2_1.csv` study:__

    ​	*  `bau` and `btm` tariffs: `EASO_TOU_15pc_FIT8`

    * Site J  `a26_f4_cp44`

    * parent:
        * `TOU9` no fit
        * `TOU9_FIT8`
    * Ea310
    * capex_med
    * `a_term` 20 years

* *0,1,2,3,4 Powerwall2* ???????????

* 0 - 3 kWp / unit

* Battery Control:
  * PV only, evening discharge
  * NB peak period 1400- 2000, *but* more useful to discharge closer to building peak?? or only for peak demand shaving strategy?
  * 2 cycles / day: off-peak import
  * 2 cycles decreases SC, but increases $?
  * Peak demand management??

N.B. (all `_id`s require `_strategy` too.)

| Arrangement                                | Battery Set-up                      |
| ------------------------------------------ | ----------------------------------- |
| `en` or `en_pv`  - with central battery    | `central_battery_id`                |
| `cp_only` - central bat only               | `central_battery_id`                |
| `btm_icp`  or `btm_i`only ind batteries    | `all_battery_id` ( `cp_battery_id`) |
| `btm_s_c`  or `btm_s_u` only ind batteries | `all_battery_id` (`cp_battery_id` ) |
|                                            |                                     |



__TEST SCENARIO:__ `study_siteJ_bat2_test1.csv`

-------------------------------------------------------



Site J (26 apartments). 

2 days only

PV: 1kWp / unit. 26kWp

battery:`bat_test1` 1kWh per unit  / `bat_test26 26kWh centralised

​	$1000/kWh, 0.5C charging

***NOTE - small issue:*** 

__PGV files labelled `1.0kW`, etc. have 1kW per unit but in  `icp`  or`c` scenarios, this is split  between units and cp, so <1kW per customer__

For test, use `btm_i` and `btm_s_u` instead?

1.  Could have 1.0kW / unit *plus* cp ratio?

2. Keep 1.0kW per unit applied to whole building?

   `cp_ratio` is determined per load, so cannot be assumed before designing PV, so stick to 2. __BUT MAKE IT CLEAR IN NOTES ETC.__

<u>__Script changes needed:__</u>

__24/5/18__

* rename `battery_` as `central_battery`. ***tick***

* Add processing for `all_battery_` ***tick*** in `network.initialiseAllBatteries`

  * Look at script sequence to ensure cp battery is processed appropriately in all scenarios.
  * ***OK, I think*** because all `Customer` initialisation of loads, etc *and* all `DynamicEnergy` calcs are applied to `residnet_list` i.e. `households` plus `cp`

* Currently no `capex` calcs for individual batteries Need to update `Network.allocateAllCapex`

  * **TODO:** Allow for individual PV (in `en`) in the same way as ind batts

* Add `self-sufficiency` calcs into `calcEnergyMetrics`

* test individual batteries

  ***SORTED***

OK I think, have debugged battery

***Still Needed:*** Peak demand management??

__Separate kWh and $ Calculations__

---------------------------------------------------

***Suggestion:***

1. Look at scenario parameters - are all energy parameters the same as previous
2. If so, copy energy flows
3. if not, calc energy flows
4. calc $
5. next

BUT: Need to look at possible exceptions:

* dynamic tariffs
* solar tariffs

***But:***

VB multiple loads, so.... would need to do all 50 VB's for the scenario

​	then calc $ for all 50

​	then look at next scenario

​	if same, calc $ for all 50

​	if not, calc energy for next 50

***FORGET IT FOR NOW!***



### **Set up Study**  `siteJ_bat2_1.csv` 

-------------------------------------------------

* Initially, looking at sc and ss so single settings for tariffs etc.
* don't use powerwall, but use generic bats with
  * 13.2kWh, 5kW
  * $1000 / $750 / $500 / $250 per kWh
  * `max DOD` = 1.0
  * `maxSOC` = 0.9
  * 

site J: `cp_ratio` = 44%. 26 units.

 *  e.g 5kWh / unit (= 130kWh), plus 100/56*130 = 230kWh total 
 *  3, 5, 10 kWh / unit

`en_pv`: 29 (mostly dynamic_ scenarios in 4532 seconds - 75 mins. 156s per scenario. Say 3 mins for dynamic? 6 threads

  `siteJ_bat2_1.csv` -> `en_pv`

`siteJ_bat2_2.csv` -> `cp_only`

__Processing Results__

2D plots:  Adapt from `EN1a_pv_bat2_SCM_SSM_ kWh vs kWp`

![1527237020427](C:\Users\z5044992\AppData\Local\Temp\1527237020427.png)

storage of 5 kWh/unit is not fully utilised. (This is 3kWh per unit plus cp)

So run again with kWh = 1,2,3,4,5 total storage per unit: 26, 52, 78, 104 total



| `siteJ_bat2_1a.csv` | `en_pv`     |
| ------------------- | ----------- |
| `siteJ_bat2_2.csv`  | `cp_only`   |
| `siteJ_bat2_3.csv`  | `btm_icp`\| |
| `siteJ_bat2_4.csv`  | `btm_s_c|`  |

* cp battery ~ 44% =11kWh (22,33,44)
* `all_residents_battery` = 15/26 = __0.58kWh/unit__
* All battery strategies are `evening_discharge_1 `

All 4 running o/night 25/5/18

`siteJ_bat2_2.csv` -> `cp_only` creates checksum error. `cp_only` not set up for bat capex.

Battery sizes incorrectly calculated, doddamnit. Should be:

| Total kWh | CP kWh | Unit kWh |
| --------- | ------ | -------- |
| 26        | 11     | 0.58     |
| 52        | 22     | 1.15     |
| 78        | 33     | 1.73     |
| 104       | 44     | 2.31     |





```
# Checksum disabled. - #TODO sort out battery capex for 'cp_only' AND BATTERY GENERALLY FOR THIS ARRANGEMENT
```

28/5/18

__Processing Results__

1. Look at `en_pv` first:

`siteJ_bat2_1a.csv`

- Using this script:  `EN1a_pv_bat2_SCM_SSM_ kWh vs kWp`

Effect of storage on SS and SC : 

![ssm_kWp_site_J_evening_discharge_1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat2\outputs\siteJ_bat2_1a\plots\ssc_ssm\ssm_kWp_site_J_evening_discharge_1.png)





![scm_kWp_site_J_evening_discharge_1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat2\outputs\siteJ_bat2_1a\plots\ssc_ssm\scm_kWp_site_J_evening_discharge_1.png)



***Up to 3 kWh/unit increases SS and SC; beyond that not much***

NB This is across whole building with cpr = 44% and 26 units, so 

- Max useful storage is  = 26 * 3 = 78 kWh, cp storage =  34.3 kWh. Per unit storage = 1.7 kWh.

2. Look at `cp_only`  (Study: `siteJ_bat2_2.csv`). Jupyter: `EN1a_pv_bat2_SCM_SSM_ kWh vs kWp CP Only`

__PROBLEM__ storage does not affect ss or sc in this arrangement. ***BUG***



![scm_kWh_site_J_evening_discharge_1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat2\outputs\siteJ_bat2_2\plots\ssc_ssm\scm_kWh_site_J_evening_discharge_1.png)

3. __`btm_icp`__ (Study `siteJ_bat2_3.csv`)  Jupyter: EN1a_pv_bat2_SCM_SSM_ kWh vs kWp BTM_ICP

   

Battery sizes calculated incorrectly. Need to rerun `siteJ_bat2_3.csv`and `siteJ_bat2_4.csv`

Meanwhile, change chart labels to include

* `site_tag`

* `arrangement`

  ***Done***

  __Sort out `cp_only`:__

  

  ss, sc, exports and imports are not affected by central battery under `cp_only` arrangement.

  Try running with `cp_battery` instead of `central_battery` ?

  (REMEMBER to change `morePVs_INSTRUCTIONS` )

  __Plotting Outputs__

* Change axes limits for comparisson between arrangements

| arrangement | ss      | sc        |
| ----------- | ------- | --------- |
| `en_pv`     | 0 -> 50 | 50 ->100  |
| `cp_only`   | 0 -> 20 | 25 -> 30  |
| `btm_icp`   | 0 -> 35 | 40 -> 100 |
| `btm_s_c`   | 0 -> 40 | 50 -> 100 |

* So try next ss: 0 -> 50 , sc: 25 -> 100 (maybe 40 -> 100 better and drop `cp_only`??)
* Then, try calculating `delta_sc` `delta_ss`  being increase  in ss, sc cf storage = 0. plot vs kWh for each scenario
*  try 3D plots:
* * NB rotation: SS 210, SC: 30

***GOOD***



![scm_3D_site_J_evening_discharge_1_en_pv](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat2\outputs\siteJ_bat2_1a\plots\ssc_ssm\scm_3D_site_J_evening_discharge_1_en_pv.png)



![ssm_3D_site_J_evening_discharge_1_en_pv](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat2\outputs\siteJ_bat2_1a\plots\ssc_ssm\ssm_3D_site_J_evening_discharge_1_en_pv.png)



### Changes to SC and SS

* basecase = row with same PV zero storage

* Calc: 

  * delta_SC = SC_kWh - SC_base

  * %SC_improvement  = delta_SC/SC_base x 100%

    

* `btm_icp` vs `btm_s_c`: sc and ss are higher for `btm_s` BUT, the increase in sc and ss due to storage is the same. ***Is this surprising??*  YES. Not correctly dealing with individual batteries because `study` file has `all_residnets_battery_id` etc instead of `all_battery_id` . Also, `battery_id` missing from `battery_lookup.csv` 

* ***Now sorted*** rerun `btm_icp` and `btm_s_c`  - i.e.  `J_bat2_3` and `J_bat2_4`



### Finances Total Site $  project: `EN1a_pv_bat3` 

Q: How does storage affect $ outcomes for building?

- Answer: it increases costs., so....

3a. What is max $ / kWh for batteries to reduce total site costs

- en_pv?
- for cp_only?

3b. Given 2 or 3 $/kWh scenarios, what is optimum kWh capacity?\



* Only`bau`,  `en`, `en_pv`  firstly (then `cp_only` but with smaller battery sizes)
* Range of storage costs: 250, 500, 750, 1000 $/kWh (add this as a parameter in `battery_lookup.csv` and copy to results file .
* Different `battery_stratagy` : 
  * `siteJ_bat3_1` has `evening_discharge_1`
  * `siteJ_bat3_2` has `double_cycle_1`

Running these two and re-running all energy ss and sc files overnight -> 29/5/18

__Whoops!__ - Have used 20 years; should be 10 or include battery refurb?

***SO: NB DON'T USE $ RESULTS FROM 20-YEAR STUDIES:***

### Energy SS and SC calcs revisited (with corrected battery calcs):

Impact of storage on SC for `en_pv`, ![delta_sc_kWp_site_J_en_pv_evening_discharge_1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat2\outputs\siteJ_bat2_1a\plots\ssc_ssm\delta_sc_kWp_site_J_en_pv_evening_discharge_1.jpg)

`btm_s`





![delta_sc_kWp_site_J_btm_s_c_evening_discharge_1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat2\outputs\siteJ_bat2_4\plots\ssc_ssm\delta_sc_kWp_site_J_btm_s_c_evening_discharge_1.jpg)



 and `btm_i`



![delta_sc_kWp_site_J_btm_icp_evening_discharge_1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat2\outputs\siteJ_bat2_3\plots\ssc_ssm\delta_sc_kWp_site_J_btm_icp_evening_discharge_1.jpg)





* Need to resolve captions and scales for all charts. DONE.

* Next - construct narrative (energy results)

  __meanwhile: Financials:__

* Start with `en_pv` :

  * For each $/kWh,
  * Plot %bau vs kWp and kWh (2D, and 3D)
  * Plot %en vs kWp and kWh (2D and 3D)





* **NEED TO PLOT ZERO STORAGE** (*tick*)

![1527571015634](C:\Users\z5044992\AppData\Local\Temp\1527571015634.png)



* increasing PV reduces costs up to optimum value which varies according to amount of storage
* Adding kWh increases costs for all dollar/kWh  except  250$/kWh![en_kWh_site_J_en_pv_evening_discharge_1_250.0](C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat3\outputs\siteJ_bat3_1\plots\percentage_en\en_kWh_site_J_en_pv_evening_discharge_1_250.0.jpg)
* Here, adding 1kWh reduces costs for PV = 2kWp or more
* __BUT__ *ALL* costs are > EN except for PV=1kW, with no storage

![1527571183280](C:\Users\z5044992\AppData\Local\Temp\1527571183280.png)

* All are cheaper than `BAU` however.

__DAMN: ALL ABOVE ARE 20 years with no battery replacement, so actual is worse.__

* 

* `siteJ_bat_3_1` : `everning_discharge` (parent 10c flat)

* `siteJ_bat3_2` : `double_cycle` (parent 10c flat)

  ***NB THESE HAVE NOT BEEN RUN CORRECTLY _ HAD 20 YEARS BUT WRONG BAT CAPEX***

  ***AND (ffs) SHOULD BE `EA305`, not `EA310`***

  

  Do these:

* `siteJ_bat3_3` : `everning_discharge` `TOU9`

* `siteJ_bat3_4` : `double_cycle` `TOU9`

* `siteJ_bat_3_5` : `everning_discharge` `TOU12`

* `siteJ_bat3_6` : `double_cycle` `TOU12`

1. Run all of the above, with 10 years (and corrected tariff calcs). 
   * No FIT for now as it will work against batteries... looking for "what would it take for batteries to work"
2. Look at impact of different strategies, parent tariff. Focusing on % of EN costs

With HPC: Could do 250W increments??

Looking at `3_3` and `3_5` with `èvening_discharge_1`  : Although PV ***does***reduce EN cost, battery ***Mostly*** reduces the benefit with this strategy, except at 

* $250 / kWh
* or for high PV > 1.5kWp/unit , when storage reduces the disadvantage of PV

This is for `TOU12`.

For `TOU9` The area of benefit is very small: No storage and PV <1.5kWp/unit



# Incorrect calculation of SC (and SS)

- With battery, SC and SS need to account for energy lost due to cycle inefficiencies.

- For `battery_strategies` that charge from PV *only*:

  - SS is unchanged
  - SC needs losses in calc

- For `battery_strategies` that charge from grid *and* PV:

  - SS and SC need charging losses, distinguished by source

- `morePVs.py` needs to log:

  - Losses (Total) 

    and, if possible

  - Losses (PV)  and Losses (Grid), *(but maybe SC and SS are less interesting if strategy includes grid charging, so leave it for now)*

  - Battery `SOH`  

  - TODO Add battery replacement by `battery_age` and/or `battery_cycle_life` to allow 20 year horizon

### `morePVs` Script: Battery charge and discharge 1)

__???__ Do losses happen on charge or discharge?

- Efficiency factored in `charge`

- `number_of_cycles` and `SOH` calculated on discharge

- `cumulative_losses` calculated on `charge` - change this to `discharge`

  This is problematic: SOC and charge level are only estimates however calculated,

  but it would make sense to have a reasonable estimate.

  For now, assume charge efficiency = discharge efficiency 

  

- `efficiency_charge` and `efficiency_discharge` set to sqrt (`efficiency_cycle`)
- Distinguish between `amount_to_charge` and `energy_accepted` and between`amount_to_discharge` and `energy_delivered` 
- `max_timestep_accepted` and `max_timestep_delivered` calculated from max charge / discharge power but are *before* losses for charging and *after* losses for discharge
- `net_discharge` per timestep is used for calculation of SC and SS (in Luthander eqn SC3 above) and
  is based on energy accepted / delivered (so  *before* losses for charging and *after* losses for discharge)
- In each timestep, co-incidence = min(load(t), Generation(t) + Net bat discharge (summed for all batteries))

***NO! SCRAP THIS!!***



### `morePVs` Script: Battery charge and discharge 2) 

__-try again:__

- Actually, rated capacity is "useful discharge capacity " 
- So, Do all the losses on charging, it will store more than 13.2 kWh and deliver 13.2kWh
- Leave script as above but set `efficiency_charge` = `efficiency_cycle` and `efficiency_discharge` = 0





__NB 1: SS has been calculated incorrectly until now.__ *(Doh!)*

__NB 2: Meaning of SC is slightly ambiguous when there is battery charging from the grid.__  Need to apportion battery cycling losses to grid or PV. Perhaps best to NOT consider SC when grid charging.

### SS CALC

WAS:  SS(old) = 1- (Total Import / Total Load)

CHANGE TO: SS(new) = 1 - (NET Import / Total Load)

​	SS1(new) = 1 - (Tot Import - Tot Export)/ Tot Load *COMPLETELY WRONG*

AND: SS2 (Luthander) = SUM(min(Load, Generation) + Net discharge) / Total Load

### SC CALC

WAS:  1- (Total Export / Total Generation) 

CHANGE TO: SC1 =  1 - (Total Export + Total Battery Losses) / Total Generation

AND: SC2 = (Total Load - Net Import) / Total Generation = (Total Load - Total Import + Total Export) / Total Generation *COMPLETELY WRONG*

AND: SC3 = SUM(min(Load, Generation) + Net discharge) / Total Generation

(Luthander)

__BUT__ 1) MAKE SURE THEY'RE THE SAME. (Spoiler: they're not)

__BUT__ 2) Do not use with grid-charging strategies

***e.g. scenario1: No battery, Load and PV dont overlap:***

*  SC= SS = 0
* `SC2` and `SS1` give wrong answer. Scrap them.
* `SC_old`, `SC1`, `SC3`, `SS_old`,`SS2` give correct answer

***e.g. scenario2: No battery, Load < PV and always overlaps:***

* SC = L/P; SS=100
* `SC2` and `SS1` give wrong answer. Scrap them.
* `SC_old`, `SC1`, `SC3`, `SS_old`,`SS2` give correct answer

***e.g. scenario3: No battery, Load > PV and always overlaps:***

* all ok

***e.g. scenario4: No battery, Load < PV and always overlaps:***

- `SC_old`, `SC2` , `SC3`,and `SS1` ,`SS2` give wrong answer. Scrap them.
- `SC1`,`SS_old` give correct answer



__WHOOPS!__

`sc3` and `ss2` copied incorrectly:

Should be:

`SS2` = SUM(min(Load, Generation + Net discharge)) / Total Load

`SC3` = SUM(min(Load, Generation + Net discharge)) / Total Generation

Correct this and ***should*** find:

* `SS2` and `SC3` are correct
* `SC3` = `SC1` . NO!
* `SS2` = ?

Using Luthander Formulas:

* For discharge, Net discharge = energy_delivered
* For charge, net_discharge = - energy_accepted
* There is an issue because the `total_coincidence` is somehow > than total generation. Odd with no grid charging.

A number of issues here:

* formula for central battery uses `cumulative_resident_export` and `cumulative_resident_import` for generation and load respectively
* This is ***Wrong*** because there has already been netting of cp load and cp pv (for `en` scenario) and presumably similar for individual PV systems
* ***Q: Does this mean the other calcs are wrong, or just this new SC3, SS2 formula???***

Fixed for this.

* For no -battery scenarios with shared pv : `sc1`= `sc3` but for individual, not so
* SC and SS figures generally within a few % of previous versions (as difference is just cycling losses)
* sc3 is higher than sc1 for `btm_icp` with no battery, but lower with battery

ANYWAY, scrap:

*  SC1 and SS_old
* SC2
* I like SS1. For 100% efficiency, SS1 is the same for all arrangements though, which is stupid but because the net import is the same for all scenarios (with PV) so it's not surprising. SS1 is about net energy consumption, not about self-sufficiency. ie not time-based. SS1 is ***stupid***. Scrap it.

***Leaving SS2 and SC3 *** refactored as SC and SS

__NB__ `en_pv` calcs use `aggregated_coincidence`  (Found using total network load and PV, with sum of all battery net discharges) , `btm` calcs use `sum_of_coincidences` (individual coincidences calculated for each PV&load&bat arrangement, then summed)

##  Testing new SC and SS Metrics

15/6/18

### Using `EN1` data as `study_combined_value9` :

Comparing old SC and SS for different arrangements (NB No battery in these scenarios)

`C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1_value_of_pv2\outputs\combined_value9\Compare SC and SS value 8 and 9.xlsx`

| Arrangement | SC (new)                      | SS (new)                      |
| ----------- | ----------------------------- | ----------------------------- |
| `cp_only`   | Higher (Same if SC=100)       | Higher (Same if SC=100)       |
| `en_pv`     | EQUAL                         | EQUAL                         |
| `btm_i`     | Significantly Higher          | Significantly Higher          |
| `btm_icp`   | Significantly Higher          | Marginally Higher             |
| `btm_s_u`   | Higher (same for `A` and `B`) | Higher (same for `A` and `B`) |
| `btm_s_c`   | EQUAL                         | EQUAL                         |
| `btm_p_u`   | Higher (same for `A` and `B`) | Higher (same for `A` and `B`) |
| `btm_p_c`   | EQUAL                         | EQUAL                         |

__TESTING:__

`study_scss_test.csv` in `p_testing`

***ASIDE:*** There is a duplication of script:

in `calcDynamicEnergy` and `calcStaticEnergy` calculating `cum_resident_export`

and then in `en.calcEnergyMetrics`, adding `resident.exports.sum()` together to get `total_building_export`

But not a problem so ***Leave it!***

SC and SS problem is with the new algorithm:

e.g. for `cp_only`, `coincidence` is calculated using total load, not cp load. 

* This is now corrected for static energy calcs: new SS and SC calcs give same results as the old ones for static, battery free scenarios. ***Hallelujah!***
* testing for battery scenarios using `study_siteJ_bat2_test2`:
* Unequal results (old and new metrics) for all scenarios with battery (as you would expect now losses are accounted for)
  * `en_pv` with central bat: SC is lower, *SS is same* 
    * which is OK, SS same because calculated using total import (unchanged)
    * SC different because calculated using export, not export+losses
  * `btm_icp` with ind bats: SC is lower, SS is lower 
  * `btm_s_c` with ind bats: SC is lower, SS is lower
    * WHY SS lower? 

Working thru 2 week scenario `btm_icp` in `C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1a_pv_bat2\analysis\bat2_test2_ss analysis.xlsx` suggests that NEW SS calculation is still wrong

Oh my word, that took a while: found bug (variable`battery.net_discharge_for_ts` being reset prematurely)

SS is the same, SC is reduced in some scenarios. Tick

Now, to test:

`siteJ_bat2_test2`

`EN1` Run `.value9` and do scatterplot: old vs new formula, should be the same

![1529276612612](C:\Users\z5044992\AppData\Local\Temp\1529276612612.png)

![1529276628735](C:\Users\z5044992\AppData\Local\Temp\1529276628735.png)

Rewrite  `siteJ_bat3_3` to `_6`  with 20 years battery capex
- [x] 1) 10 year replacement
- [x] 2) # cycles

Run `bat4` 1-4 is 10 years, 5-8 is 20 years

`bat4` results:

- [x] Numpy error raised:

  ***Fixed***

- [ ] Timing:

  - 1 scenario (battery, no PV) 8 minutes (ontop of other runs)

  - `bat4_1-6` 5 simultaneous processes  - no threads

    ​	each process: 3 - 8 scenarios / hour, so up to 20mins / scenario.

    But if 3 mins / scenario (running in series), 6 studies x 120 scenarios = 720 * 3 min /60 = 36 hours. If 20 mins, 240 hours. Far too long


## SC & SS Timing

* Change  `battery.net_discharge_this_timestep` to 17520 x 1 array

* Also `total_discharge` to be summed from all batteries as an array (perhaps in 'calcEnergyMetrics`)

  * Move sc and ss calcs out of `calcDynamicEnergy` and `calcStaticEnergy`

    and into `en.calcEnergyMetrics`

`test_bat_numpy` was 459 seconds for 1 scenario. Now: 220s

- [ ] Run single scenario on hpc: `test_bat_numpy`



## BESS Strategies revised

1/7/18



| battery_strategy    | charge_start1 | charge_end1 | charge_day1 | discharge_start1 | discharge_end1 | discharge_day1 | charge_start2 | charge_end2 | charge_day2 | discharge_start2 | discharge_end2 | discharge_day2 | notes                                                |
| ------------------- | ------------- | ----------- | ----------- | ---------------- | -------------- | -------------- | ------------- | ----------- | ----------- | ---------------- | -------------- | -------------- | ---------------------------------------------------- |
| no_time_constraints |               |             |             |                  |                |                |               |             |             |                  |                |                |                                                      |
| evening_discharge_1 |               |             |             |                  |                |                |               |             |             | 18:00            | 20:00          | both           | PV charge for evening peak                           |
| single_cycle_1      |               |             |             |                  |                |                | 12:00         | 16:00       | both        | 18:00            | 20:00          | both           | Afternoon charge for evening peak                    |
| double_cycle_1      | 22:00         | 7:00        | both        | 7:00             | 10:00          | both           | 12:00         | 16:00       | both        | 18:00            | 20:00          | both           | ...plus overnight charge for morning shoulder period |
| double_cycle_2      | 22:00         | 6:00        | both        | 6:00             | 10:00          | both           | 12:00         | 16:00       | both        | 18:00            | 20:00          | both           | ...overnight charge for morning peak load?           |























- [ ] Run `pv_optimiser_2_10` for SS and SC plots in `EN1` paper:

  - [ ] compare with `2_9` (scatter plot)

    Taking 1 min per Static scenario - slooooow

  - [ ] 



__NEXT: Look at `cp_only` and `btm_s_c`  arrangements in more detail.__

__THEN: repeat for other sites__

Only: 
`a52_f3_cp27` 
`a48_f4_cp09`
`a44_f4_cp17`
`a26_f4_cp44`
`a20_f5_cp37`



