

# en2_storage_4.md

31/7/18 - concerning `EN2_bat2` outputs used for EN2 paper

- continued from en2_storage_3.md

## SSM / SSC Plots

RESULTS FROM : `energy1_J`

plotted in jupyter: EN2_bat2  SCM_SSM_ kWh vs kWp EN

`evening_discharge_1` look ok, similar to previously. 

`double_cycle_1` are odd: Sc and SS vary eratically with kWp and kWh

* 2 charge periods: 2200- 0700 and 1200- 1600

* 2 discharge periods: 0700 - 1000 and 1800-2000

  May well be un-useful for increasing SC and SS as this is  essentially an arbitrage strategy

  But this is odd: ![1532999604574](C:\Users\z5044992\AppData\Local\Temp\1532999604574.png)![](C:\Users\z5044992\AppData\Local\Temp\1532999604574.png)
![](C:\Users\z5044992\AppData\Local\Temp\1532999604574.png)

![1533001121644](C:\Users\z5044992\AppData\Local\Temp\1533001121644.png)

Maybe as kWp increases, more is sent to battery in the daytime, (so greater SC, SS). Need to look at it.

* ***TODO:  come back and look at timeseries for this***

__3D Plots__

orientation:

ssm works at 300 or 210, scm at 120 or 30.

Both increase with kWh but SC decreases with kWp. So maybe need same angle but plot one axis differently. `azim=210` degrees, but plot SC with kWp axis reversed using `ax.invert_yaxis()`

Averaging peaks removes anomalies:

__Single peak__

![]([1533020311717](![](https://i.imgur.com/EqA4Xdq.png)))



__Ten peaks:__

![1533020349512](C:\Users\z5044992\AppData\Local\Temp\1533020349512.png)



__50 peaks__

- not so much
- ![1533020763651](C:\Users\z5044992\AppData\Local\Temp\1533020763651.png)

1/8/18

## Battery Strategies

To examine possible strategies, - impact on energy firstly:

Create simplified study, with single VB:

* bau, en, en_pv

* central battery 0-4 kWh / unit

* PV 0,1,2,3,4

* Log timeseries INCLUDING PV, bat SOC, etc

  `study_bat_strat`

### Peak Demand reduction

Currently, evening discharge period is 18:00 - 20:00, but some peaks are earlier (17:00? eg)

Look at AusGrid Capacity charge calc (`ES7` document):

```
the maximum half hourly kW or kVA demand reading2 that occurred in the peak period (that is, between 2pm and 8pm on a working weekday) at a customer’s connection point over the billing periods that relate to the previous 12 months including the current billing period. The volume to which the capacity charge is applied is known as the “billable maximum capacity.

Refer to Appendix E – Calculation of Power from Interval Data (Ausgrid) for the calculation of kW and kVA.

```



* so even though 1400 - 1800 is shoulder period for volumetric tariff, worth reducing demand in this period, 

* so worth starting discharge earlier .

* Look at distn of peaks for each site.

  http://127.0.0.1:8888/notebooks/en_notebooks/EN2_bat2/Peak%20Demand%20frequency%20dist.ipynb

  

![1533186275259](C:\Users\z5044992\AppData\Local\Temp\1533186275259.png)


| ---- | ----- | ------ |
|      | mean  | median |
| ---- | ----- | ------ |
| A    | 19:00 | 19:00  |
| B    | 19:03 | 19:00  |
| C    | 19:18 | 19:00  |
| D    | 18:59 | 19:00  |
| E    | 18:53 | 18:30  |
| F    | 18:59 | 19:00  |
| G    | 19:03 | 19:00  |
| H    | 18:59 | 18:45  |
| I    | 19:27 | 19:00  |
| J    | 18:05 | 17:30  |
| ---- | ----- | ------ |


- very variable: in particular 
  - site J - start at 17:00
  - site G,I,H,F,C... start at 17:00

SEASONAL:

Generally, winter median peak is an hour (or 1/2 hour) LATER  than summer except site J where it is 1/2 hour EARLIER

### So.....

* Design battery strategies to discharge 1 hour EARLIER IN SUMMER??

First, try strategies with start at 17:00 , 17:30 and 18:00

~~`study_bat_strat_2`  - to look at single vb, but~~ 

better to run `bat_energy2` new study set up in `SETUP_EN2_bat2_2`

with 9 bat strategies: ed1-ed3 starting at 18:00, 17:00, 17:30

#### `energy2` results:

looking at slower charge / discharge (ed1, ed2, ed3) and earlier discharge:

Looking at site I and site J - cursory look at SSM ssc

Site I here: C:\Users\z5044992\Documents\MainDATA\DATA_EN_4\studies\EN2_bat2\outputs\bat_energy2_I\plots\ssc_ssm

- no signfiicant improvement on SSM / SSC

.....see below



## Financials: `finance1` plotting

in jupyter: EN2 FINANCIALS 

- issue with  duplication of `en` scenarios in set-up.
- Missing scenario: 'en' with no battery, no pv.  ***goddamit*** - this is rerun as `bat_finance1en_site`

meanwhile....

Site F: 

![1533531914144](C:\Users\z5044992\AppData\Local\Temp\1533531914144.png)

No positive npv for any en with pv and/or bat. This is consistent with EN1 paper, BUT, NPV calcs are much more negative than in EN1. Error in calc. - Now resolved.

- Site J has very odd results for `finance_J` . Seems to be incongruity between inputs and outputs.
- Specifically, e.g. `en_capex_repayment` calculated over wrong period. this is likely to be in recombination or transfer from hpc to PC. 
- DELETE AND RERUN `finance1_J`as `finance1a_J`

## energy2

looking at SSM SCM:

Comparing `ed1` (Discharge at max rate)  `ed2` 9 (C0.5) and `ed3` (C0.25)

`evening_discharge` stratagey, starting at 1800, 1730 or 1700,

Best results (higher SS & SC) shown below

| Site | discharge rate | start time |                                            |
| ---- | -------------- | ---------- | ------------------------------------------ |
| F    | max rate (ed1) | 17:00      |                                            |
| G    | max rate (ed1) | 17:00      |                                            |
| H    | max rate (ed1) | 17:00      |                                            |
| I    | max rate (ed1) | 17:00      | NB PV0, kWh1 missing for some arrangements |
| J    | max rate (ed1) | 17:00      |                                            |

Peak Demand results are *strange*:

* In general (many scenarios) , peak drops from no bat to 1kWh, then increases.

e.g. site F (these are average of top 10 peaks in 50VBs)

![peak_kWh_site_F_ed1](C:\Users\z5044992\Documents\MainDATA\DATA_EN_4\studies\EN2_bat2\outputs\bat_energy2_F\plots\peak_demand_10highest\peak_kWh_site_F_ed1.jpg)



![peak_kWh_site_G_ed3_1730](C:\Users\z5044992\Documents\MainDATA\DATA_EN_4\studies\EN2_bat2\outputs\bat_energy2_G\plots\peak_demand_10highest\peak_kWh_site_G_ed3_1730.jpg)



* NB decrease is small. e.g. above, savings from 28.6 to 27.9, delta is 0.7 x 39c x 365 = $99.64 for whole building  < AUD2 / unit. ***Not significant***
* e.g. 90% reduction in peak: 2.86 x 39 x 365 /442 = aud 407 = aud9.25 / unit
* e.g site G, demand charge is 20-30% of bill. reduce it by 10% saves 2-3% of bill
* 

Look at this e.g. in detail:

`C:\Users\z5044992\Documents\MainDATA\DATA_EN_4\analysis\Look at peak demand reduction - bat_energy2_G.xlsx`

```
site G
PV = 1.5kWp
strategy = ed_1730
```

| kWh  | scenario name            | Mean of 50 VBs | VB2      |
| ---- | ------------------------ | -------------- | -------- |
| 0    | bat_energy2_G_hpc020_040 | 28.6061351     | 32.0692  |
| 1    | bat_energy2_G_hpc078_157 | 28.05729       | 31.4351  |
| 2    | bat_energy2_G_hpc083_166 | 28.103148      | 31.82698 |

Choosing VB`02` to look at  because it does what the average does: peak increases 1kWh -> 2kWh

But only partial logging, so rerun these 3 scenarios:

`study_bat_energy2_G_testing.csv`

Peak can be reduced *less* with bigger battery if it has less stored energy when the peak arises. 

![1533626835380](C:\Users\z5044992\AppData\Local\Temp\1533626835380.png)

![1533626841951](C:\Users\z5044992\AppData\Local\Temp\1533626841951.png)



This can happen because the bigger battery discharges faster, so in some circumstances can end up with less stored energy than the smaller battery. e.g:



![1533626897985](C:\Users\z5044992\AppData\Local\Temp\1533626897985.png)

![1533626904145](C:\Users\z5044992\AppData\Local\Temp\1533626904145.png)

- larger battery starts with more energy but discharges quicker (to no useful affect in reducing peak demand) and ends up with less energy stored.
- so maybe need to compare larger battery with lower discharge rate??.
- ...or plot peak reduction vs kWh and discharge rate?

__Related Question:__ 

​	keep charge rate at max, or keep it equal to discharge rate?

​	(For double_cycle, definitely need to reduce charge rate to avoid import spikes)

### SSM / SCM results:

Comparing `energy2`  (fixed discharge time) and `energy3` (variable discharge time), - results LOOK the same: e.g site H:



![1533628418510](C:\Users\z5044992\AppData\Local\Temp\1533628418510.png)
![](https://i.imgur.com/3CVascp.png)

![](https://i.imgur.com/8zfNIix.png)


![1533628432877](C:\Users\z5044992\AppData\Local\Temp\1533628432877.png)

Both have ed2 (discharge at 0.5C) and winter period starts at 18:00. Summer period an hour earlier



e.g. `energy2_G: ed2 `     vs `energy3_G ed2_s_18` compared here:

`C:\Users\z5044992\Documents\MainDATA\DATA_EN_4\studies\EN2_bat2\outputs\bat_energy3_G\bat_energy3_G_results_process.xlsx`

- not the same:

  ​	`central_battery_cycles_mean` *very* close but less for seasonal strategy

  ​	similarly `ssm` and `scm` very close, but not equal.

- Look at peak demand:



## better strategy  design:

- so far PV meets daytime load first, then goes to battery.

__SiteF & siteG & siteI:__ low PV potential, so prioritise charging battery meeting daytime load, with single discharge period to match evening peak

`C:\Users\z5044992\Documents\MainDATA\DATA_EN_4\studies\tests\outputs\test_bat_strat\timeseries\plots`

***Do this later:***

* Additional strategies that only allows discharge when import meets (e.g) 90% of peak demand

## Look at energy again:

NOTE: I have been looking at *decrease in mean peak demand*, 
should i look at *mean decrease in peak demand*? (Mibee, but I think ok for now.)

Look at energy3 and energy2 to:

1. compare peak demand with peak 10 demand - decide which to use

   - peak10 is (obvs) lower, but delta much the same. And 50VB's accounts for outliers,
   - so use peak demand (for now)

2. identify best kWp / kWh to use to compare strategies

   - bigger differences are for higher kWp (2.5, 3, max)
   - biggest difference is for 1 kWh / unit

3. then compare seasonal strategy and fixed start-times

   __Peak Demand:__

   - J: `ed2_17` is better than `ed2_1730` or `18` 

     AND better than `e2_s_17` and `18`

     similarly with `ed1`

     (site J may be anomaly because of winter vs summer peaks different)

   - I: fixed `ed1` better than `ed1s` 1730 best. Same for `ed2`

   - H: `ed17` and`ed2_s_17`identical. also 18.  1730 gives best

     `ed1_18` (same as s) is best

     But `ed3` better: 1730 best, particularly for bigger PV

   - G:`ed1` and `ed2` both:   `s17` better than `17` but  `18` better than `s18`.  Fixed 1730 best

   - F: `ed1`  and `ed2` both: `s18` better than `18`, `s17` better than `17` . but `1730` is best.

     ***USE FIXED 1730***

   `ed3` better for higher PV: `F`, `G`, `H`, `I`( `J` is marginal)

   - NB: none of the differences are very large.

     

   - (really? 10 hour charge / discharge????. 

   or is there a factor of 2 there somewhere.....No, all good!

   __SSM / SCM__

   - J, I, H, G,F : Both metrics: `ed & 2`:  `s17` = `17` > `1730` >  `s18` >= `18`

     ed1>ed2>ed3 on both metrics

   ***`ed1` (max charge / discharge rate) gives higher SS and SC, but `ed3` (0.1C) gives greater peak reduction***

   ***`1700` (fixed or seasonal) gives higher SS and SC , but `1730`fixed gives greater peak reduction***

   __NB `energy2_I` has missing data__

4. pick 'best' strategy for increasing ss/sc and reducing pd

5. Use best strategy for energy4 study comparing btm_i with en_pv

   Primarily looking at SS and SC, so use:

   * `ed1` (max charge / discharge rate)

   * 1700 seasonal

     

***OK but*** some scenarios missing from `energy4`. rerun as `energy4a`

 

