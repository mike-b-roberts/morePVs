



# Systematic testing of `morePVs`

### Testing:

__Energy:__

* Import & Export
* Load Aggregation
* PV Sharing 
* PV aggregation
* Battery:load shifting
* Battery peak reduction
* Self Consumption
* Self Sufficiency

__Financial:__

* Tariffs

* Capex and Opex

* Inverter Replacement

* Battery SOH / Replacement

* Total Costs

* NPV

  

## Simple, reproducible scenarios:

***KISS: 2 days, 2 residents***

__Energy:__

* Simplify PV to step
* Simple distribution
* Load: 100%SC, 0%SC, 50%SC
* Compare arrangements
* Battery: 1kWh/1kW
  * Compare strategies and plot
  * Look at SC, SS, peak



__Finance:__

* BAU with simple tariffs: Flat, TOU, Demand. Do the sums
* EN with simple tariffs: Do the sums
* Capex and Opex: Effect on Total Costs
* Inverter replacement- after 12 hours
* battery replacement - after 1 hour / 0.2 cycles





###Input Files:

__reference__ data in `DATA_EN_3/reference - TEST`

**Loads** in  `load_profiles/test_2day' ` and  `load_profiles/test_2night' `

`test_load1` is night time only

`test_load2` is daytime only

**PV** is `pv_2days_test`



**Project:** `s_testing`

**Studies:**`test_energy1`

- No PV
- Different tariff types and arrangements.
- `btm` all should be == `bau`



### Tariffs:

I will call this:

##<u>Tariff Error #2</u>

*__DEMAND CHARGE__

​	Demand charge needs kW, Load is in kWh

​		kWh -> kW : *2

​		kW -> kWh : /2

Code has (`Customer.calcdemandCharge`):

```
max_demand = np.multiply(self.imports,self.tariff.demand_period_array).max()/2
```

__CHANGE TO:__

```python
max_demand = np.multiply(self.imports,self.tariff.demand_period_array).max() * 2
```

***Oh my days!***

**WHAT TO DO WITH THIS ERROR?**

* rerun `APRSC` and replot 

* All `EN1` and `EN2`  $ calcs, obvs.

* meanwhile, add in logging of demand charge for `en` scenario

* ***See `Tariff ERROR 3052018` for reruns and results***

  

## Next tests:

__With PV: PV allocation__

**Project:** `s_testing`

**Studies:**`test_energy2`

`en.allocatePV()` has an issue with `btm_s` arrangements where if there is zero load, get an error, allocation is zero, but should then be that all units (and cp in `_c` arrangements)  get equal share:

```python
self.pv = load_units_only.div(load_units_only.sum(axis=1), axis=0).multiply(
    self.pv.loc[:, 'total'], axis=0).fillna(0)
```

becomes

```
self.pv = load_units_only.div(load_units_only.sum(axis=1), axis=0)\
                .fillna(1/len(self.households))\
                .multiply(self.pv.loc[:, 'total'], axis=0)
```

`btm_i` is OK

`cp_only` and `en_pv` have same allocation

`btm_s` - look at when , eg load is all on one unit.. All good

__NEXT__

Looking at __import / export / SC / SS__ for all arrangements, with coincident and non-coincident generation:

(Still using `test_energy2`) and it all looks good.

__Energy with Batteries__

**Study:**`test_energy3`

* `central_battery_id` with no `central_battery_strategy` causes issue. It should assume no battery. ***sorted*** 
* checksum errors for all battery scenarios. Issue is `total_battery_capex_repayment`
  * Issue due to non-scalable scenario. test battery has 1 day life and `a_term` is 10 years so, uh.... revert to 5 year life. But still checksum error:
  * this is because arrangement is `bau` but there is a battery. hmmm. battery capex has not been allocated. Fix: make `bau` scenario have no battery, but #TODO: add `bau_bat` arrangement
  * Checksum error still appears for `cp_only`, `btm` scenarios. `resident[c].has_battery` is False for all residents (should be True for `cp`?) This is known issue: bat capex not resolved or individual batteries. Problem is central PV belongs to 'cp', central battery doesn't, 
  * Need to allocate central battery costs 
    * `en` : to `network`
    * `cp_only` : to 'cp'
    * `btm_s` : allocated to 'cp' by `cp_ratio` and shared equally
    * `btm_i` : allocated same as PV 
    * `btm_p` to solar retailer
  * OK, except for `btm_p` - solar retailer  - now sorted
* div by zero error in `battery.charge` because `maxDOD` = `maxSOC` = 50%, so battery has no capacity ever,
  * Change to `maxSOC` = 0.6, `maxDOD` = 0.4 and still an issue  because still no capacity! They cannot add to 1. Doh.
* `central_bat_capex_repayment` needs to be set to zero if no central battery
* OK - no exceptions raised. Look at results.

***NB All this is in `git branch` `diagnostics` - need to `git merge ` back to `master`***

__Timeseries Plots:__

* `btm` does not show import or export - need to log total import and export to time series to analyse this. 
  * ***s'ok:*** confusion due to `en` in 'energy', now sorted
* Looking at scenario 103: 
  * `SOC` is unexpected.  
    * PV - Load = 1kWh, export = 0.95kWh, delta(battery charge) = +5kWh
    * WRONG. `test_bat1` Should be delta(battery charge) = 1  (efficiency = 100%) 
    * because efficiency given as 100, instead of 1.0! ***All good***
  * `en_pv` arrangement, `total_grid_import` and  `total_grid_export` is meaningless? certainly confusing. It is sum of imports / exports from the en, while `en_import` and `en_export` are import / export at the parent meter. need to make this clearer. 
    * ***CLARIFY  NAMES***: `total_grid_import` now called `sum_of_customer_imports` and same for exports
    * `en_import`  and `en_export` called `grid_import` and `grid_export`
* 104 also good.
* 105 no charging because PV < load
* 106 charges, doesn't discharge because evening only
* ***FIX LOGGING AND LOOK AT btm PLOTS*** THEN FINANCES

### `btm_s`:

![1529884988090](C:\Users\z5044992\AppData\Local\Temp\1529884988090.png)

* Is `pv_generation` == `total_grid_export` ? Makes no sense if battery is charging.
  * No. In `.csv` it looks OK, but `pv_generation` is not being plotted?
  * `en_export` is export to grid, `total_grid_export` is export from each customer, summed, bearing in mind that `cp` is exporting to the `eno`.
    *  ***CHANGE THESE NAMES????*** in `calcEnergyMetrics`  (DONE: SEE ABOVE)
    * hang on: This is `btm_s_c`  arrangement with a central battery. What is real world meaning? Battery must be connected to shared PV. This scenario is not included in the model at present. ***Scrap these scenarios***
*  SO, for all `btm` scenarios, only allow individual batteries.
  - [x] Modify `morePVs_setup_instructions`
  - [x] Add conditions into code

- [x] rerun `test_energy3` with scenarios removed
- [x] Set up revised `test_energy4` study: all `btm` arrangements with individual (unit and cp batteries) as appropriate
- `test_energy4_109` issue: `btm_i` with batteries for all units and cp. is this a real situation? Is this modeled?. ***all good.***
- NB batteries always initialized to zero `SOC` - would be better to initialize to 0.5 or to `maxDOD`?
  - ***Set `initial_SOC` to 0.5***
- compare 109 and 112: `btm_i` cf `btm_icp`  with same battery scenario (3 x 5kWh)
  - `batm_icp` SOC only goes to 6%. _OK._ less charging because no import.
- Look at 110 `btm_i`
- `SOC` goes to only 66.7% when  `maxSOC` is set to 1.0. Is fine, 2 batteries are full, (hence 67%) Doh

__Looking at SC and SS:__

`energy4_010`

009 (no bat) and 109 (bat_1) have same SC (91.7%) though old method gives 100% for bat
* expect SC to increase with bat, as small export without bat. Not necessarily:
  * This is `btm_i` With bat, the export is still exported from that resident and imported to another, then charges battery. So individual SC is not changes

* Also, same SS (I would expect ss lower with battery, due to losses 5%)
  * Sum of net imports is the same??
  * SS and SC use `sum_of_coincidences` rather than `total_aggregated_coincidence`
  * Actually, the battery doesn't affect SC because it is never discharged
  * and doesnt affect SS because no change to customer import
  * ***ALL GOOD***

__Look at 110 SC and SS:__compared to 010. SS and SC good. 

Currently, no examples have discharge except for nighttime load scenarios. Try with different battery strategy: `double_cycle_1`

`test_energy4` is btm with double_cycle

`test_energy_3_dc` is `en` with double_cycle

- charge pattersn look right.
- Compare `en` and `btm` scenarios for sc, ss:
- 5_120 and 3_dc_105: 

![529908385447](C:\Users\z5044992\AppData\Local\Temp\1529908385447.png)

* sum of imports and sum_of_exports are different because central bat vs indi bats. ie total bat capacity is 3 times for btm. better to compare with central en bat being 15kWh, ie 3_dc_3_305
* ![1529909069591](C:\Users\z5044992\AppData\Local\Temp\1529909069591.png)
* 

![1529909105121](C:\Users\z5044992\AppData\Local\Temp\1529909105121.png)



* grid import is the same for `btm_s` and for `en_pv` ,

* These and others (comparing `btm_icp` and `btm_s_c` look correct in terms of charging schedule, etc.## 

  __Note re batteries__ 

  much of the charging is instantaneous -charge rate too high (C1, should be C2 min) - now changed to C2:

  ![1529910036015](C:\Users\z5044992\AppData\Local\Temp\1529910036015.png)

  

  

## Finances:

KISS: Start with no battery, Take 3 scenarios: ***`test_finance1`***

* en_pv , btm_icp, btm_s_c and compare :
  * customer bills
  * total costs
  * NPV

NPV calcs:

* `net.sum_of_npvs` = `net.npv_whole_building` for all arrangements *except* `en` and `en_pv`

`en_pv` has same npv as `en`, and same  `sum_of_npvs` - bc pv_capex attached to en scenario 

	* ***Add a check: if `en` (rather than `en_pv`), don't add pv capex. DONE***

Resolve which npv calc is correct for `en` and `en_pv`  `sum_of_npvs` is incorrect, it adds in individual customer npvs twice. Need:

sum of npvs for all customers - npv(en)

***npv sorted***

`en_pv` - scenario 3, 10

### Timestamp:

* Battery is not discharging at 18:00 as expected, bc `battery.discharge_period` is:

  ```
  DatetimeIndex(['2013-01-01 18:30:00', '2013-01-01 19:00:00',
                 '2013-01-01 19:30:00', '2013-01-01 20:00:00',
                 '2013-01-02 18:30:00', '2013-01-02 19:00:00',
                 '2013-01-02 19:30:00', '2013-01-02 20:00:00'],
                dtype='datetime64[ns]', name='timestamp', freq=None)
  ```

  i.e. starts at 18:30 	

   * 8 x 30 minute periods which is correct
  * timestamp refers to ***end*** of period

* For load:  __ASSUMED__ timestamp refers to end of period

  * __SGSC: __`READING_DATETIME`  is `The actual date and time of the reading.`

  

  * __Wattwatchers API:__ 
  * __Huxham: __Supplied data starting `00:00` and ending `23:30` 
  * __AEMO Interval Data:__`ts` is end of period; First reading of day is `00:30` , last is `00:00`

* For PV:

  - [x] SAM: 13:00 value is for the hour 13:00-14:00, ie ts is *start* of period

  - [x] BOM dataset

    * insolation: readings are x minutes after the hour quoted (~45mins):

      `C:\Users\z5044992\Dropbox\UNSW\METHODOLOGY\Weather Data\Timestamp Conventions.docx` - correction has been made for this.

    So PV is start of time period

    ```
    metafile ='C:\\Users\\z5044992\\Documents\\MainDATA\\DATA_EN_3\\pv_profiles\\pv metadata\\en3_pv_metadata.csv'
    # .... for Weather Data
    weather_path = "C:\\Users\\z5044992\\Documents\\MainDATA\\DATA - Weather\\WeatherFiles\\en_WFs\\halfhourly"
    # .....for PV output
    ```



## Weather Files

- see `Weather Files Process and Testing.md`



* So, are there 2 probs here: 
  * timestamp at start / end of timeperiod
  * weather files out of whack
* 

### Dynamic vs static:

*  Run multiple scenarios with no bat and bat cap = 0

  * Same results. Dynamic = Static. check

  `C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\s_testing\outputs\static_vs_dynamic\static_vs_dynamic_results.xlsx`

### `cp` energy bills in `en` arrangement - restructure

`study_test_cp_en.csv`

* Different results for  `cp_tariff` = `TIDNULL` or not

* `cust_bill_cp` is zero for `TIDNULL`, not otherwise, but if not `TIDNULL` is there a real meaning to this?

* it is what strata would pay ENO if ENO is independent (eg external retailer) and strata is effectively customer `cp`. 

  (BUT: (good) `npv` is not affected, so not a problem for `strata en`arrangement)

Why then was there so much variation on this figure when i shifted timestamps by 30min?

2 ISSUES: 

* Timestamp Issue (see below)
* Structural issue:
  * For `en` (non-strata-owned), `cp` 'owns' PV but it should be owned by EN
  * To fix this, central PV needs to be moved to `en`
  * This has implications for:
    - [x] `en.allocatePV`
    - [x] `en.allocateAllCapex`
    - [x] `customer.initialiseCustomerPV`
    - [x] `en.calcBuilding StaticEnergFlows`
    - [x] `en.calcBuildingDynamicEnergyFlows`
    - [x] `customer.calcSatticEnergy`
    - [x] `customer.calcDynamicEnergy`
    - [ ] ?`customer.calcCashflow`
    - [x] ? `en.calcEnergymetrics`
    - [x] ?` scenario.calcFinancials`
    - [x] `scenario.collateNetworkResults`

__Restructure results:__  comparing `value10a` and `value10_restructured` : outputs are identical - including `cp_bills`__ WWWW, because `en` scenarios have `cp_tariff` set to `TIDNULL`.

* Run `study_test_cp_en_2.csv` and compare with previous version: `cp_bill` should be different, `npv` same. 

  * In fact, `npv` is different for `en` scenarios, bc capex settings have changed. 
  * Revert capex and it is as expected

  

## Impact of Timestamp Issue

- Is this a fundamental problem?

  - run a single site: site J, BAU

    -  with existing profile

    - with profile shifted so 1st timestep load data is shifted to the end of the year, ie ts now refers to the hour following

      - Difference in mean of financial outputs is 0.41%.  but this was bau so had no pv.

      - site J has a high (67.5%) PV ratio, but it will be more significant for:

        - TOU tariffs & FiTs, so rerun: `EASO_TOU_15pc_FIT12`
        - `btm_i` scenario and `en_pv`  as it will affect individual exports, etc.

        `C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\s_testing\outputs\test_timestamps\test_timestamps_results.xlsx`

|       | average_hh_bill \| average_hh_total | cust_bill_cp_mean | cust_total_cp_mean \| eno_demand_charge_mean | eno_energy_bill_mean \| eno_npv_building_mean | export_kWh_mean | import_kWh_mean | retailer_receipt$_mean | self-consumption_mean | self-consumption_OLD_mean | self-sufficiency_mean | self-sufficiency_OLD_mean | total$_building_costs_mean |
| ----- | ---------------- | ----------------- | ----------------- | ------------------- | ----------------------- | --------------------- | ---------------------- |
| en_pv | 0.7%             | 0.7%              | -18.3%            | -18.3%              | -1.0%                   | -0.2%                 | -0.1%                  |
| btm_i | 1.2%             | 0.7%              | -0.2%             | -0.2%               |                         |                       | 0.3%                   |
| bau   | 0.7%             | 0.7%              | -0.2%             | -0.2%               |                         |                       | 0.4%                   |

All variation approx <0.5% EXCEPT `cp_energy_cost` for `en_pv` scenario  which is __18%__ despite negligible difference to import or export. 

- With zero FiT on EN internal tariffs , difference is 1%. so Why such a massive difference in export (flat_rate FiT) with the same amount of export. oh dear. But cp_tariff should be `TIDNULL` for `en` arrangement, so this isn't going to affect any results.

See here `C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\s_testing\outputs\test_timestamps\compare old and new timestamps.xls.xlsx` for manual calculation of the cp bill in these scenarios. (ie `en_pv` but with a cp tariff): There is a delta of AUD97 import and AUD20 export due to the shift in timing.

- Why doesn't this occur for the other arrangements - eg `btm_s`?
  - Difference is the same (AUD 76) BUT total cp bill is AUD 7000, so % is insignificant. Not sure why: `cp` export is bigger for `en` because PV allocated 100% cf btm_s where it is by PV ratio.
    - This scenario is critical only because of small CP bill

For btm_i, average h/h bill changes by 1.2%.

- How should tariff period be applied? to match load so:
  - currently: ts is end of period so, e.g ts between 14:30 and 18:00 are in period 2pm-6pm
  - IF `ts` changed to start of period, this shifts to 14:00-17:30



__Overnight run 26/6/18__

`siteJ_value10a`  and `siteJshift_value10a` 

Results:

`C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1_value_of_pv2\outputs\siteJshift_value10a\cmpare npv with timeshift.xlsx`

* NPV:

![1530056752561](C:\Users\z5044992\AppData\Local\Temp\1530056752561.png)

Similarly, 

![1530057380265](C:\Users\z5044992\AppData\Local\Temp\1530057380265.png)

* % Change in NPV due to timeshift

  ![1530056829245](C:\Users\z5044992\AppData\Local\Temp\1530056829245.png)

so, all < 1%.

* __BUT:__ NPV relative to BAU is smaller so impact of ts is larger, particularly in a minority of `en` scenarios:

  ![1530056894798](C:\Users\z5044992\AppData\Local\Temp\1530056894798.png)





#Back to Finances:

Still no battery. Look at `test_finance_1_results` and `comparing_npvs`

### Capex:

`pv_capex` = AUD 37.5. 10 yrs becomes 4.9959, with inverter 7.49 ***tick***

`en_capex` = `capex_short` = 14aud for 2 units. Should it be 3 (inc cp?) ***tick***

`battery_capex_repayment` is wrong (number of replacements incorrect)

* ***fixed*** Any implications?



__Battery Cycle Lifetime:__

`study_test_lifecycles.csv`

* Little difference between `double_cycle_1` and `_2`. look @ timeseries
* bc discharge period starts as PV kicks in (7am)
* Also, NB: charging period creating demand spike (C2). Try C4

(***BATTERY STRATEGY NOTE:*** `double_cycle` with overnight charging tends not to discharge in the morning if PV is sizable because shoulder period coincides with PV production (*BUT* maybe not with shifted loads))

__ALSO:__ Add afternoon charging from grid (if no PV) to options (`double_cycle` ??) 

Look at battery life:

`test_lifecycles` - with battery lifetime = 200 cycles: all batteery capex repayments should be the same but are not.

* residual error in battery capex calcs:
  * inverter lifetime years calc'd wrong - ***fixed*** (has not been used for any studies to date)

__BATTERY CAPEX__ - sorted for `en`. 

Now 

1. central battery with shared capex:

   btm_i & btm_s do not allow for central battery at present

2. individual batteries: `test_lifecycles2`

   - `btm_icp: all good
   - `btm_s_c` all good



## SGSC Zero Filling Issue

See summarised process and notes: `SGSC data preparation.md`

(SGSC Filling alalysis: `filling analysis and DRAW CONCLUSIONS - revisit 3/7/18`)

- 2 versions of SGSC data:

   1. approx 6000 households

      < 90% of readings are `zero` or `nan`

      filled for`zero` or `nan`

  	2.	approx 9000 households

      < 90% readings are `nan`

      filled for `nan`

BUT: there are no `nan`'s in the original datafile, only zeros. The `nan`'s must have been added at a later stage (converted from zeros), to files that have passed the 90% criteria. 

So, 

EITHER: 

- Assume `zero == nan`  (revert to original dataset)

OR:

- Assume `zero === nan` if at start (or end?) of customer data, or if big block of zeros (how many?), `zero == zero reading` otherwise. (Reprocess with arbitrary criteria.)  



## Script Snags



| Issue                                      | Impact                                                       | Solution                                                     | Done      | Implications                                         |
| ------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | --------- | ---------------------------------------------------- |
| **Filling zeros in SGSC data**             | +0.5% of total (average?) general load<br />+0.7% of average customer's load<br />But, max load added to single customer is +23% (largely unchanged)<br />BUT: variability  metrics are likely different  (Also total number of units) | 1. Re-preprocess data <br />2. recalc metrics<br />3. Recalc clusters and categories | Partially | Cluster Paper (EN Papers use  correctly filled data) |
| Typo in tariff period                      | Increased costs, no significant change to relative costs     | Correct `.csv` and reprocess                                 | Y         | ASPRC / EnergyCon, All EN papers                     |
| losses in SC and SS calculations           | Only affects battery scenarios                               | Revised algorithm                                            | Y         | None (EN2 on)                                        |
| Demand Charge algorithm                    | demand charges x 4                                           | Amend Algorithm                                              | Y         | All EN papers, ASPRC / EnergyCon                     |
| **Timestamp at start / end of period**     | to 0.5% energy & to 1% financial. 0.5% in NPV, but significant for delta(NPV) (5%+) in some scenarios | Move ts to start of period?                                  |           | All EN & conf & Cluster Paper - SC?                  |
| **PV weather file time alignment**         |                                                              | ?                                                            |           | All EN & conf & Cluster Paper - SC?                  |
| **Tariff periods  adjust for DST**         | Affects all TOU tariffs                                      | Change tariff algorithm?                                     |           | All  inc*Cluster Paper - SC?                         |
|                                            | -                                                            | Add NPV calc                                                 | Y         | All EN papers                                        |
| `cp` energy cost in `en` scenario          | Affects non-strata owned `en`                                | restructure: allocate PV to `en`                             | Y         | Future Only                                          |
| No spread data                             | -                                                            | Add box-tail plots                                           |           | All EN papers                                        |
| `battery_capex` <br />replacement bat calc | None - no battery replacements modeled to date               | Fix algorithm                                                | Y         | Future Only                                          |



## Timestamp Issue Summary:

__Load Profiles__: 

start `1/1/2013 00:00 `  Energy data - i.e. kWh supplied in *preceding* 30min period. 
So timestamp is at *end of period*.  *__ASSUMPTION__*

__PV Profiles:__

SAM: First timestep is from midnight to 1am (or to 12:30) whether it is labeled `0` or `1`. Here it is labeled `1/1/2013 00:00 `  so the timestamp relates to the *start of the period*.

__Weather Files:__

WFs created from BOM gridded satellite data 

- *Hourly* gridded data: timestamp marks start of period. Data reading is 49.3 minutes (0.82 hours) into hourly period. This `satellite_time` is fed to `SAM` to calculate `DHI` from `GHI` for weather file
- SAM takes solar position on the half-hour for hourly data.
- weather file created with Time Zone =10, first time = 00:00

__BUT__ my WFs do not align with `.TMY` files downloaded from NREL SAM (`IWEC`) or from EnergyPlus (`RMY`).

NB `RMY` and `IWEC` files start with 1/1/1991 01:00 but this is the treated by SAM as the *SAME* hour ie midnight -> 1am



__Timezones & DST:__

All weather files are local time - AST (i.e. no daylight savings).

*RMY:* `HOLIDAYS/DAYLIGHT SAVINGS,No,0,0,0`

*BOM:* gridded insolation is UTC, converted to AST (+10), 
	Temp & Windspeed are given as local time, and as local standard time.
		 local standard time (AST) used to generate weather file.

*SGSC:* in the original dataset, timestamps `6/10/2013 1:00` and `6/10/2013 1:30`    appear twice, while `6/10/2013 2:00` and `6/10/2013 2:30`are missing. This is rectified when extracting the yearly datasets.

*Huxham CP Data*: All supplied as standard local time

*WWAPI Data:* Supplied as UT, convert to standard local time

*TARIFFS:* TOU tariffs take DST into account. In 'morePVs', tariffs are applied assuming timestamps refer to start of period.

### So three issues:

1. Need to align load data with PV generation: timestamps should refer to *start* or *end* of period?
2. Why does WF not align with 'TMY' ?
3. Adjust tariff periods to standard local time:
   - so period is for times >= start and \< end  (previously it was times \> start and <= end)
   - Use this opportunity to resolve tariffs that cross over midnight: look at what i did for battery 

## Resolving DST Problem and Timestamp alignment:

6/7/18

* In `Timeseries.__init__` create winter and summer periods according to datetimes in `dst_lookup.csv`

  __NEW timestamps refer to the *start* of the period__

  __NEW TARIFF PERIOD: start <= timeperiod < end__
  $$
  start <= timeperiod < end
  $$
  (Previously it was *start < timeperiod <= end* )

  

* In `TariffData.generateStaticTariffs`:

  * belated fix to allow tariff periods to cross midnight

  * ***NB  need to change tariff periods in `tariff_lookup.csv` in light of this.***

    ​	- __DONE__ (also found a residual tariff period error on SIT_ppa tariffs)

    * `.join('inner')`: combine seasons and tariff period
    * for summer_period, shift the hours
    * recombine winter and summer

* - [x] Repeat this for demand tariff period and for solar tariff period
  - [x] Tested. ***Solar block and inst tariffs need further testing***

  

  ***STILL NEED TO SHIFT TIMESTAMPS ON LOAD PROFILES***

  ***THIS IS DONE IN `vb_create_v6.py`***



# More testing

__9/7/18__

## Compare no battery with null battery

`C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\s_testing\inputs\study_zero_battery.csv`

* Scenarios 13 - 16 create checksum error. `en` with battery creates an issue.

  * Appears that `en_capex_repayments` are not allocated to the eno in `en` scenario, but they are in `en_pv` scenario.
  * Because `arrangement` is `en_ ` (space) instead of `en`  

* Which is another reason to change `btm_` and `btm_icp` to `btm_i_u` and `btm_i_c` throughout

  All GOOD

* Also, rerun with battery capex and test again:

  * battery capex = 1000, but average customer in en is paying 4744 pa 

    because CAPACITY IS ZERO SO THOUSANDS OF BATTERIES ARE NEEDED.

    (SEE also central battery has 2337660 cycles!)

    This was a zero capacity anomaly

    `btm_i_c` and `btm_i_i` resident has NO pv capex

     `btm_i_u` cp has pv capex costs and en capex costs

    



### Testing NPV Calcs

SEE: [here](C:\Users\z5044992\Documents\MainDATA\DATA_EN_4\analysis\npv_capex_check_value11.xlsx)

![1531969162593](C:\Users\z5044992\AppData\Local\Temp\1531969162593.png)













