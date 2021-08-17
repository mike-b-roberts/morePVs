## Detailed design of en_1 and en_2 studies 
## Using *morePVs*
# Extensions from APSRC 2017 and EnergyCON

### Broad Outline:
1)	EN2: Distribution of Costs and benefits (As EnergyCON but extended)
-	50 VBs , but for all 10 sites 
		o/p: %Savings vs SC for different tariffs, Savings vs load?
		o/p: EN Income vs tariffs / PV
		o/p – Landlords vs tenants vs OO
		Tariffs: TOU25, STC20, Solar Inclining Block (SIB)? ,Cost plus % for EN) (C+15)
		PV x 2: a) max with FiT,  b) smaller PV for high SC (plot SC vs PV)
		11.5c & 9.5c?
		10/15/20 years??

	)	EN1: Value of PV & Storage (As APSRC but extended)
		50VBS for 10 sites
		Add cp only arrangement
		o/p is total building cost
		10/15/20 years capex payback
		Add costs for BTM-s
		Add storage – impact on total costs

	)	EN2: Distribution of Costs and benefits Using WWAPI Data:
		Look at range of scenarios from above and apply to each building
		O/p: total building costs
		o/p look at each resident / owner individually
		relate to h/h demographics

-------------------------------------------------------------------------------------------

Value of PV and Storage (EN1)
-----------------------------
A) __Find optimum PV__
Run multiple scenarios for each site: Keep all factors constant, change PV system.
PV systems could be:
1) Take max roof pv and scale down
2) Take optimum pv and scale
3) Rank panels (or kWp) from max system and exclude iteratively

* Start with approach 1) (for simplicity), 
 * then take optimum pv size and apply to method 3)
  * Plot SCM vs PV/unit and look for kink in the curve.\

 __PV vs SC and SS__

Generally: can get 100% SC with 20% self-sufficiency
Increase SS to 40%, SC drops to 40%

 1 kW / unit: Sc 80-100%, SS 20-30%
 2kW / unit: SC 55-80%, ss 28-36%

* But* These real(virtual) buildings have 0.2 - 3.0 kWp per unit
H and J > 2kW/unit: 
Where pv < 1kw/unit, use full roof only

	 site  |kWp    |kWp/unit	| households|  PV scenarios |
| ----- | ----- | --------- | ----------| ------------- |
	A	    |47.25	|0.227163	|208        |    Max        |
	B	    |18.75	|0.180288	|104        |    Max        |
	C	    |9.5	|0.279412	|34         |    Max        |
	D	    |42.25	|0.306159	|138        |    Max        |
	E	    |90.25	|0.560559	|161        |    Max        |
	F	    |31.5	|1.575	    |20         | Max, 0.5 1.0  |
	G	    |76.75	|1.744318	|44         |Max,0.5 1.0,1.5 |
	H	    |141.5	|2.721154	|52         |Max,1,1.5,2,2.5|
	I	    |52.5	|1.09375	|48         |Max, 0.5, 1    |
	J	    |78.5	|3.019231	|26         |Max,1,1.5,2,2.5|


For sites F -> J, calculate "best" 0.5kW per unit;
This is done in `C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\pv_profiles\pv metadata\en3_pv_metadata.csv`
NB pv is created by: `C:\PYTHONprojects\utilities\create_pv_profile_subarrays.py`
and stored in `C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\pv_profiles\vb_pv`

B)__As before__
* Load Data: 50 x VB's (new filling)
    1) for Site G only
    2) for all vb sites
* PV
    1) Max PV and other options (see above)
    2) Range of options 0.5-3.0 kWp/unit (see above)
    3) "Optimised"??
    
* All technical arrangements
* 3 en capex scenarios
* __PV capex__ from feb 2018: https://www.solarchoice.net.au/blog/solar-power-system-prices
NB APVI PV trends 2016: http://apvi.org.au/wp-content/uploads/2017/08/PV-In-Australia_AU.1.1.pdf
* Subsidy is 60-70c/kWp depending on insolation
* PV inverter capex 30c/W https://www.solarquotes.com.au/inverters/
* 5 / 10 / 15 / 20 / 25 years amortization
* 6% rate
* Parent Tariff: Network + 9.5c , 11.5c , ??
* Parent FiTs 0 / 8 / 12.5
* Also need to vary FiTs for BTM arrangements: 8 / 12.5

* Internal tariffs irrelevant

```
# NB This strips path and suffix from cell in excel:
=IF(ISBLANK(B3),"",LEFT(RIGHT(B3,LEN(B3)-FIND("\",B3)-1),FIND(".",RIGHT(B3,LEN(B3)-FIND("\",B3)-2))))
```

Site A has 141 scenarios. Some sites have 6 times that for ,multiple PV systems
Currently running at 8s/ scenario for 4xVB's
BUT this scales to 1 minute for 50VBs
For 50 VBs will be 1 *141 for site A = 141 minutes 
And for other sites, up to 6 * 141 = 846 mins = 14 hours.
So 28 pv scenarios is 2 weeks. Doh!


__GODDAMN THIS WILL TAKE TOO LONG_
Need to be cleverer about what i want to know.

With superfluous scenarios removed:
{'A': 125,
 'B': 125,
 'C': 125,
 'D': 125,
 'E': 125,
 'F': 500,
 'G': 500,
 'H': 750,
 'I': 375,
 'J': 826}
 TOTAL 3576 scenarios = 10 hours



__FiTS__ 
2017/18
https://www.ipart.nsw.gov.au/Home/Industries/Energy/Reviews/Electricity/Solar-feed-in-tariffs-201718
11.9-15
Cut to around 8c from July (iPART) https://www.ipart.nsw.gov.au/files/sharedassets/website/shared-files/pricing-reviews-energy-services-publications-solar-feed-in-tariffs-201819/solar-feed-in-tariffs-201819-issues-paper-march-2018.pdf

__study_EN1_value1__
* as above
* no storage
Desired Outputs:
1) Barchart of costs/unit for single site under various scenarios
2) Sites compared for similar scenarios
For 1) : Separate study for each site?
C) __Add Storage__
1) For fixed dispatch strategy, and other parameters
* iterate for PV size and bat_cap
* plot SC
* plot total_building_costs or total_building savings vs pv

__Battery Details__
* Storage Costs from C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\reference\PV_storage_costs_lookup.xlsx
- from Solar Choice battery Storage Prices Jan 2018.
* Model Scenarios: Low/ Mid / High $/kWh for Battery
* Find / Use 'typical' W/Wh (or C's) and lifecycles



__Question:__ Do i need to add the facility for individual batteries, in order to compare
individual battery & PV to shared battery and PV??

__Answer: YES__ (but maybe later):
* Gives facility to calculate the increased benefit of shared storage / PV
* Does not apply to apartment buildings

__How hard is it?__
* refactor `initailiseBuildingBattery` to `initailiseAllBatteries` and Initialise all batteries 
* Move `calcDynamicStorageEnergyFlows` from `Network` to `Battery` or to `Customer`?
* Call `calcDynamicStorageEnergyFlows` for all customers and `eno`
    - initialise `flows` using `generation` and `load` for `Customer`
   - *sorted*
__Meanwhile, add Threads:__
done


EN1 - Value (no storage): Processing Results
--------------------------------------------

Possible approaches:
1. Look at all scenarios for each site in isolation
2. Compare specific scenarios across all sites

These are the variables:

| Parameter | Values                   | Treatment                     |
|-----------|--------------------------|-------------------------------|
| `arrangement`| `en` |
|   | `btm`  |
| `pv kWp  / unit`| 0, 0.5, 1.0, 1.5, 2.0, 2.5 & max
| `en_capex`|  3 scenarios             |
| `a_years`| 5,10,15,20,25 |
| `parent` (en only) | 9.5,11.5|
| parent FiT | 0, 8, 12.5 |

__These are the questions:__

*Note that it's quite late in the day to be deciding what the question is!*

*NB Important to look at distribution of results, not just average across all vbs.*

1.  Compare `btm_i`, `btm_icp`, `btm_s` with `bau`.

    Plot scatter with colour for site OR plot barchart ?

    a) For all sites, range of `kWp / unit`

    b) For range of PV `a_years` (1 plot per)

    c) 3 FiT scenarios on same plot

2. Compare `en` , `en_pv`, for range of `kWp / unit`:
    * Scatter Plot Total $ vs vs kWp / unit,
    * colour per `site`
    * symbol per `a_years` amortization
    * plot per `en_capex`  / `parent` tariff

3. Compare `en_pv` to `btm_i` and `btm_s`
    * Scatter `en_pv` total $ vs `btm` total $
    * fixed kWp / unit for each chart
    * colour by `a_years` and `en_capex` ??

    Start with Number 2: `en_pv`


Notes on restructuring
----------------------
19/4/18
Whether to separate financial calculations and energy calcs:
* Certainly, all capex scenarios can be done *after* and *outside of*
any iterative processes.

* Tariff scenarios *may* be doable outside, but in some cases have to be done
*inside* the iterative loop. e.g. `block` tariffs.
* So, proposal is:

1. run simulations varying:

    * `arrangement`
    * `pv` file
    * `battery` id
    * `battery` control
    * all `tariff`s
and save all outputs as `.csv`
2. Calculate all financials of different:
    * `en_capex_id`
    * `pv_capex_id`
    * `a_term`
    * `a_rate`

Is it worth it?
Currently:
3 x 1 * 5 * 1 scenarios - ie speed increase x 15

hmmmm....??

__Correction to inital `_value` setup__
* add 75 x `en` scenarios
* Sort by `arrangement`,`pv_filename`, `parent`,`all_residents`, `en_capex_id`, `a_term`
* Also `parent` = `11.5c` with no `FiT` has been omitted.
* __Use `setup_en1_value3` notebook to sort this.__
* ALSO: rejig `parent` tariff do FiTs = import tariff. Why shouldn't FiT *at least* equal
 import retail & wholesale?? retailler is still saving `NUOS`
* So,
* 
| Parameter | Values                   | Treatment                     |
|-----------|--------------------------|-------------------------------|
| `arrangement`| `en` |
|   | `btm`  |
| `pv kWp  / unit`| 0, 0.5, 1.0, 1.5, 2.0, 2.5 & max
| `en_capex`|  3 scenarios             |
| `a_years`| 5,10,15,20,25 |
| `parent` (en only) | 8,12|
| parent FiT | 0, 8, 12 |

(but FiT <= import)

Allume `btm_s` Arrangements
---------------------------
Look at 2 scenarios separately:

`allume_1`:
    * 2 Solar instantaneous tariffs:
        1) pV_used
        2) pv_exported

`upfront_1`:
    * btm_capex like en_capex
    * Fixed charge ($5/month) charged as opex
    * solar instantaneous tariff = 0
__Consider role of `en` in this scenario - and relationship between allume and strata__

Two options:
1. Combine retailler tariff and Allume tariff to give total paid to `retailer`
( which is really a combination of 2 Retailer plus Allume)
2. OR Set up a second retailer for this arrangement,.....


The first has the advantage of scripting simplicity but is less transparent
The second is more transparent but requires some restructure:
    - Maybe 2 `Network`s - one pays to retailer, other to Allume
    - FOR NOW:  just run as alternate arrangement,separately calculating allume payments.

Use combined tariff:
`SIT_15_FIT8_allume1` and `SIT_15_FIT8_ allume2`
 - based on `EASO_TOU_15pc` with 8c FIT
 - with additional solar rates (for SC only) of 18c+GST and 20c+GST
 - solar rate for export = FIT

 NB Need to ascertain how `discount` is applied:

 In `TariffData.generateStaticTariffs`, `discount` is applied to all tariff rates
 *except* `fit` .
 Now, exclude all `solar_` or `Solar_` rates from discount.
 Allume tariff has named rate: `solar_self_con` of 19.8 or 22 (18 & 20 + GST)

__NEW Allume Plan__
All `btm_s` scenarios treated the same:

`btm_s_c` / `btm_s_u` for cp and units / units only
For `btm_s` arrangements:

    - Set up additional party (not a `Customer`) called `solar_retailer`
    - `solar_retailer` pays for all pv and en (actually btm) capex
    - local solar payments go to `solar_retailer`
    
    -   For `allume`: 'btm_p`
        -   `solar_retailer` pays for all pv and en capex  
        -   pv is allocated to customers and treated as self-consumption
        -   but SC solar tariff is charged for self consumption (and FiT for export)
        -   local solar payments go to `solar_retailer` 
        -   (allume is `solar retailer`)   
    -   For `upfront` `btm_s`
        - pv and en capex and en_opex split between all residents (and cp)
        - no `solar_tariff` just standard retail tariff


Try again:

shared `upfront`:
* PV is shared proportional to load
* residents get use of PV, get FiTs from export, like it was their own
* capex is shared equally, opex is shared equally
shared `allume`:
* It's not a quota system.
* PV is allocated according to load, same as `upfront`
* But residents pay `solar_rate' for their 'own' generation
* `solar_retailer` pays capex
* `solar_retailer` receives local payments




In the Future
-------------
*NB Really, what needs to happen is complete restructure.
* `Customers` are created independent of `Network`
* Maybe new object is `Building`
* `Customers` can then become part of more than 1 `Network`
    *   Embedded Network
    *   Retailer / Grid Network
    *   BTM Network
    *   P2P Network
*   `Building` is not a `Customer`
*   `Network` or `eno` is special kind of `Customer`
*   For each `Network`, calc energy flows and cash flows between all players
*   Each `Customer` has the sum of all their interactions
*   Then, collect all the data at the end.
__Much Better!__ (But not for now)




Two `EN1_value_of_pv` studies:
------------------------------
`value4` has all `en` arrangements only
`value3` also has 'btm' arrangements - no details for allume
need to redo with `value5` having allume cost structures

meanwhile, `value4` en
----------------------
- look at jupyter notebooks for results
- EN1_value Plotting (no battery) - barcharts - LINEPLOTS
- OK, except tariff scenarios are being merged. Oh dear, try again:
-(Stupid: was using `zip` misunderstoodwise
- EN1_value4 en pv - LINEPLOTS
- Now uses `for parent, capex in [(parent, capex) for parent in parents for capex in en_capexes]:`
OK, but $en_pv > $en for all acenarios - including 12c FIT,
- shurely shome mishtake.
- `APSRC` paper had at least some sites `en_pv < en` for `a_term = 12`. Here using `a_term = 5-20`,
- I think these have all been plotted as 5 years. Whoops. *FIXED*

Also, try plotting as % of `bau`
`value4' : `plots' - line plots for `a_term` = 5 years
        : `plots2` - same for all `a_terms`
        : plots3  - plotting as % of bau

26/4/18
Plotting charts from `value4` study:
* Issue with ylims - low %bau gets cut off *FIXED*
* linetypes - does it add or lose clarity?

* rename `capex_` names *DONE*
* sort tags for sites `axxx_fxx_cpxx` *DONE* needs adding to charts

__PV Inverter Costs__
1. 2016 price breakdown from apvi: 25c / 119c
2. https://www.solarquotes.com.au/inverters/ solar quotes:
   30c / Watt e.g. (SMA) 10kW inverter costs around $3,000
3. I've been using 30c

But this is wholesale cost, excluding installation.
Better estimate (based on 10c/W installation plus 24% + GST)
C:\Users\z5044992\Dropbox\UNSW\MARKET DATA\Platinum Price List March 2018.xlsx

Use
__0.55c/W for inverter inc__

- NO -__Use variable values for inverter replacement ($ decreases with kW)__
- [See PV_storage_costs_calc.xlsx and capex_pv_calc.xlsx]
- 


__NB Extract federal subsidy from PV costs??__


__Check PV capex `value4` results:__

( see C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\reference\pv_capex_testing.xlsx)

Error in pv capex calc:

in `Scenario.__init__`
Now recitified to:

`self.pv_capex = study.pv_capex_table.loc[self.pv_cap_id, 'pv_capex'] + \
                            (int(self.a_term / study.pv_capex_table.loc[self.pv_cap_id, 'inverter_life']-0.01) * \
                             study.pv_capex_table.loc[self.pv_cap_id, 'inverter_cost'])`

NB the `0.01` ensures inverter isn't replaced at end of system financial lifetime

__*SORTED* Now need to rerun `value4` and `value3` and `bat1` studies__

`value4` -> `value5`

`value3` -> `value6`



ALSO Check `siteJ_bat4` and `siteJbat5` results
-----------------------------------------------

Possible issue  with linearity of %bau vs kWp curves,
with `parent` at 12c, `FiT` @ 12c
Because Network tariff also has a /kW component, so self consumption
is worth more than export.

* But First, look at partial financials:
  * `NUOS_charges$_mean'
  * `eno$_energy_bill_mean`
Actually, this looks good:

NUOS proportional to import, and otehr financials make sense.
See C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\studies\EN1_pv_bat1\analysis\siteJ_bat4_exploration.xlsx


So to be sure (to be sure), set up a test with:
* one `siteJ` load profile,

*kWh = 0 to 2kWh
* pv = 0 to 3kWp
* capex_5, 20 years
* `parent` = 10c
* `FiT` = 0 to 20c, in 2c increments
`p_testing\study_test_pv_storage.csv`

__*LOOKS* OK__

PARENT Tariff
-------------

Add TOU element as per Nick bell email 26/4/18:
9-10 c/kWh peak and 6.5-7 offpeak

CHECK GST situation - also for FIT

So:
See here:
C:\Users\z5044992\Documents\MainDATA\DATA_EN_3\reference\tariff sources.xlsx

`EA310_TOU10` and `EA310_TOU9`
Have 10c / 7c and 0c / 6.5 c respectively.
Maybe use also `EA310_TOU_11` or `_12` for alternate scenario??
Also, NB, need to include __environmental charges__ on these and GST
`EA305_TOU10` and `EA305_TOU9`
with Fits of 8 and 12

NB Metering Service Charge is not calculated correctly for combined retail & network tariffs.
Fortunately, `EA305` and `EA310` dont have MSC. So no harm done.
Only non-capital component of MSC is required,
Capital component of MSC does not apply as meter capital costs included in en_capex
__*FIXED*__
Also NB `value4` studay had ALL sites with `EA310` which is incorrect. Should only be
for A,B,D, E. All others are EA305. __*FIXED*__

This is set up as `value5` in `EN1_value_of_pv2`

results are very odd!
- plotting issue, `p_slice`  incorrectly applied. __*FIXED*__
- NB results much 'better' than `value4` becaue of correct network tariff `EA305` applied - reduces en costs,
- also because inverter costs now correctly applied to `pv_capex`
__*FIXED*__

* Modify PV inverter replacement costs to variable $/W (see above) and re-run `.value5` and `value6`

__2/5/18__
* `.value6` (`btm` arrangements omitted zero FiT tariffs. So rerun.
* BUT also, check operation of `btm_s` allume scenarios:
    * For `btm_s` with `allume` tariffs: PV capex is zero cost.
    * Also need to track `allume` income `solar_retailer'
*ALSO, `btm` seems to be always cheaper than `bau` if `a_term != 5` . Seems a bit dodge.
* ALSO split sites into `group1` and `group2` and plot seperately

`btm_p` now sorted and checksum added to total cost calcs. __*FIXED*__

3/5/18
Fix `.value6` set up and run it.
One further question: `if btm_p_u` (or s), does it affect result if cp tariff is solar sc (although cp has no pv)
__*All Good*__

7/5/18
SS and SC plots

pv_optimiser_2_6 : `en_pv` repeat for btm_i, for cp_only and for btm_s:
pv_optimiser_2_7 : `btm_s_c`
pv_optimiser_2_8 :`btm_i_cp`
pv_optimiser_2_9 :`cp_only`

1. Run `morePVs` for these 4,

2. change legend for ss and sm plots: Use tags, __*FIXED*__
3. look at alpha  __*FIXED*__
4. then `morePVs_output.plotOutpt('scm_ssm_vs_pv_all_vbs')`  __*FIXED*__

Combine ss-sc plots for `btm_icp` and`en_pv` / `btm_s`:
combine `pv_optimser_2_8` and `2_7`


Financial Results
-----------------
__First plot to compare arrangements__
* `capex_med` for `en` arrangements
* PV = 1kW /unit vs no pv
* all resident tariffs `EASO_TOU_15pc_FIT8`
* `parent` tariff `EA???_TOU_10` no FiT
* `a_term` = 10 years
* all sites
* `arrangements`: `bau`, `cp_only`, `btm_icp`, `btm_s_c` ,`en`, `en_pv`

NOTES from Iain and Anna
------------------------
* Inverters will get cheaper. Maybe reduce inverter replacement costs?
* Model higher FITS to include environmental costs (see VIC: +2.5c?)
* Model higher parent retail tariff: Iain: up to 15c
* Take 25 years as standard, then work back


Realization re `btm_i` 14/5/18
------------------------------
`pv_capex` costs have been based on total system size.
For `btm_i` or `btm_icp`, $/W should be higher, either:
* assume samll (1-3kWp system), or
* price at top end of $/W to allow for microinverters

*All scaled PV systems use correct $/W for so DON'T need to rewrite script*

This affects `value6` results.
Tasks:
* Set up new capex scenario for `btm_i` arrangements
* Create new `value7` study file
 (Combine `value5` with `5a` and `5b` and `value6` where
* `5b` has zero FIT for `bau` and `btm` arrangements
* `5a` has `ppa` tariffs
NB `value7` has ;less scenarios than `value5_6` because of previous duplication.

* Run `morePVs` for `value7`

*   Replot ALL CHARTS

`btm_icp` results are strange only for `site_J` with ~3.0 kWp
- because $/W jumps down from 1.6 to 1.28 goig from 2.5kW to 3kW.
- Damnit - revisit these:
2 issues:
  1. monthly spikes in specific system size costs: Average over 6 months
  2. No $/Watt for 1kW and only occassional prices for 1.5kW on solarchoice:
        extrapolate line back to 1kW

# SC and SS Calculations

15/6/18

See `en2_storage_design2.md` for notes on erroneous SC and SS calcs and change to algorithm. 

Also for testing of `EN1` data under both calculations.

See also `C:\Users\z5044992\Dropbox\UNSW\PhD\misc\SC and SS metric.docx` for details of the metrics used

## NPV Calculation

typo in npv calc, (`scenario.calcFinancials`) so annual costs are applied monthly . doh. Now corrected in script,

BUT - need to change figures for `value11`, `pv_optimiser` studies in `EN1_rerun` 

DONE in main `results` file but not for scenarios

## Rerun value 11 on hpc

npv calc corrected

- Because NPV = total cashflows (scenario) - total cashflows (bau), there needs to be 5 bau scenarios (if npv is calculated within `morePVs` ) - 1 for each `a_term` These have been added to `value`` and rerun 18/7/18



## Results Compared

### Barcharts:

__TOTAL SITE COSTS:__

Looking at `a_term` = 20:

`en` and `en_pv` costs have increased in rerun.  This is likely related to the increased demand charge.

Demand charge accounts for 16% - 40% of EN energy bill

__ Need to add discussion of demand charge into EN1 paper ? (and definitely EN2)__

For `a20_f5_cp16`  NPV is -ve for `en` (max PV and 1kWp)

`btm_i_c` is more expensive (-ve NPV) for some scenarios with max PV. Same ==Good 



## Plotting

Line plots of NPV for `en_pv` compared to `en` are upside down? see [here](http://127.0.0.1:8888/notebooks/en_notebooks/en1_value_plotting/EN1_value11%20en%20pv%20-%20LINEPLOTS%20-%203%20with%20a_term%20.ipynb)

***Sorted***

### NPV for btm_s

23/7/18

- From `EN1_rerun3` / `value11`: Solar PPA is always higher NPV than `upfront` arrangement.  Should be preferable for low a_term but less for longer a_term. This suggests NPV calc is treating solar retailer profit incorrectly.

- compare `value11a` results with `value8`:

  1. household solar bills for `btm_s` with  `ppa` are massively decreased in `value11a` : to 26% - 38% 
  2. retailer bill is increased by ~70% in many scenarios: This hasn't been used anywhere but needs checking for future
  3. total building costs for `btm_s` now varies with `a_term` which it didn't previously. It should.

- Error in dst calcs of `summer_period`  if start_time > end_time for period, which will affect:

  - solar period (not solar tariff). 
  - demand charge period (ie only winter peak demand considered)

  (these both in `Tariff.__init__()` )

  - all other static TOU tariffs  are OK

  (this in `TariffData.generateStaticTariffs`)

- Solar tariffs  ***Now fixed*** , by treating start>end separately.

- BUT retailer bill still much increased. Is this due to demand charge difference (on network Tariff) as noted previously or additional demand charge error (summer periods) or something else?.

e.g. scenario 35 retailer bill:

`value11a` 74945, `value8` 44630 . Difference is 30315

```
e.g vb01: peak load is 132.6 kWh / half hour. i.e. 265 kW
demand charge (`EA310`) is 265kW x 39.3c x 365 = $38012, 
so increase in demand charge will have been approx 75% of this = 28509
```

So this looks like the difference is due to fixed demand charge.

 `EA310` demand period has 3132 timesteps which is 17.9%. (ie 6 hours/day, 5days/week)

## Rerun3:

`value11b` is as before but solar and demand tariff period fix. 11a took approx 14 hours.

### results:

1) barchart

`en` is less beneficial than previously thought because of higher demand charges.

look more at variation with PV



btm: `btm_s` as before, `btm_p` less beneficial. 

* `btm_p` is constant for `a_term`, so lose 20 years label. and add to `btm_s`charts
* % of bau or % of en is more confusing than AUD
* NPV / a_term is better for comparing a_terms.

Why is site F (`a20_` so bad for en?  compared to site J(`a26_`)?

* ​	difference is all about CP bill in `bau` scenario: site J pays more because peak is always at peak time. 

  * site F pays less in `bau` because average load is flat:

    ![1532398337856](C:\Users\z5044992\AppData\Local\Temp\1532398337856.png)

Why? because site J has three lifts while site F has 1?? or because site J has a pool?

## CO2 calcs 

are here: value11_calc CO2 jupyter