Value of PV and Storage (EN1) - Part 2: Storage
-----------------------------------------------

* Start with single site and reduced set of parameters, including multiple PVs
    * `EN1_pv_bat1` / `study_siteJ_bat1.csv`
    * Site J (APSRC had `en_pv` costs more than `en` (without FiT)
    * Take same parameters:
        * FiT 12.5
        * parent 9.5c
        * Ea310
        * capex_5 20k + 400, opex 250
        * `a_term` 12 years

 __Ungood:__
results are odd. Maybe model not dealing with battery capex costs?
`total$_building_costs` same for 0,1,2 powerwalls. Whoops.
Go look at `battery_capex_calcs`

*(NB. Currently no `capex` calcs for individual batteries
Need to update `Network.allocateAllCapex`)*

Also, en (no pv costs are massively less than `en_pv` costs, but `en_pv` costs reduce with increasing pv
To see what is goin on, need to add `repayments` to output csv
Two issues:
* `pv_capex` is constant for all `en_pv` scenarios.
* *BECAUSE* I used the same `pv_cap_id` in input file. `You dick`.
__FIXED__

* `battery_capex` has 3 values for same battery 1171,5644,5293

NB issue around `scenario` vs `Network` variables?
* NB battery capex is per network; en and pv capex are per scenario
(because battery capex depends on cycling)

`num_cycles` is not resetting because
`Network.initialiseAllBatteries` is called once per scenario, not once per load profile.
__*FIXED*__

`sitej_bat3` divided into 3 csv files for multiprocessing.
`python morePVs.py -p EN1_pv_bat1 -s sitej_bat3a -t True`
(with `3b` and `3c`
* Site J (APSRC had `en_pv` costs more than `en` (without FiT)

    * No parent FiT
    * parent 10c
    * Ea310
    * capex_5 20k + 400, opex 250
    * `a_term` 10 years
* 0,1,2,3,4 Powerwall2
* 0 - 3 kWp / unit

So, it's working.....

Running these overnight
25/4/18

__Initial results__

`siteJ_bat1` study: 10c, no FIT, 10 years, capex 5
`EN1_storage_siteJ_lineplots 2 - kWh vs kWp` (jupyter) is doing the plots:
% of bau and % of en costs vs kWp and kWh

- Doesn't look good for pv or for bat relative to en.
- Because: No Fit, Only 10c tariff, Only 10 years.

__Next Study__
`siteJ_bat4`
- 20 years
- 12c no fit, 12c with 12c fit
(`4a`, `4b`, `4c`) no FIT
(`4d`, `4e`, `4f`) 12c FIT

__Next Study__
`siteJ_bat5`
As 4, but with battery cycling

So need to run bat4 a to f
bat5 a to f


__Plotting Improvements__
For `EN1_value_of_pv`:
* Change limits for % en plots *DONE*
* Vary markers, linestyles by A-term *DONE*
* Add legend *DONE*



Looking at both of these (`bat4` and `bat5`), the results are odd:
There seem to be almost no benefits from adding storage, ONLY increased capex.
Also, no difference between battery charging strategies
So, have a look at self consumption and self-sufficiency for these studies:
using `EN1_storage_siteJ_SSC_SSM_ kWh vs kWp`


(Found an issue in `morePVs` : self consumption = 0 if PV =0.
Should be 100% - FIXED)





battery capex:
--------------
* Powerwall 8500 + 4000 installation
https://reneweconomy.com.au/tesla-enphase-lift-household-battery-storage-prices-23273/
Est, 4000, 3000, 2000, 2000 for 1st, 2nd, 3rd, 4th powerwalls
* ie 12500, 24000, 34500, 45000
* inverter cost included
* guarantee is 10 years unlimited cycles. I have used 4000 cycles


__PV Capex__ does not currently include replacement inverter costs.
__*FIXED*__

discharging cycles shifted to fit Aus Grid TOU periods as well as local peak
ie 7-10 am and 6-10pm

* * 

