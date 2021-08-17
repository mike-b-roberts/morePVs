## Notes on battery implementation
28/3/18

__Battery Input Parameters__
* Storage Capacity kWh
* Charge / Discharge rate kW
* Efficiency % (Charge & Discharge separate? or Cycle?) (Li-ion: 95-98%)
* Max Depth of Discharge (70-90% for Li-ion)
* Initial State of Charge

__Battery Variables__
* State of Charge
* Number of Cycles

__Charge & Discharge Functions__

* If SOC will be <= minSOC, don't discharge
* If SOC will be >= max SOC, don't charge
* Only charge or discharge max kWh per 30min ts 

__Battery Control Strategies__
KISS initially - from eno pov only
(alternative is to optimise for whole building minimum cost)
(eg look at Ratnam 2014) 
SIMPLEST:
* If PV > building load, and SOC < maxSOC, charge battery
* If PV < building_load and SOC > minSOC, discharge

NEEDS MORE SOPHISTICATION:

__APPROACH 1__
* Explore range of time-based options, eg:
1. Only discharge battery during peak period
2. Only discharge battery during peak and shoulder periods
3. During off-peak, charge battery from grid if required. (double cycle)
4. ? Keep some reserve in battery and use for peak demand (above given threshold level)
Talk to jose

__APPROACH 3__ (Maybe later)
Compare costs at each timestamp:
* Estimate $/kWh for battery discharge. How best estimate this?
* Dispatch battery when bat cost < import cost

So, for initial model, go with simple strategy plus additional periods:
* Limit period of discharge
* additional period of charging *even if no excess PV*

__ Some notes on charging and discharging__
http://batteryuniversity.com/learn/article/charging_lithium_ion_batteries
*Charging* 0.7C - 1C, Discharging  *~1C*
So: use inverter power for discharging and charging and recommend inverter poer <~ 0.8C .
(ie power (kW) is 0.8* capacity (kWh))
Useful table here: http://batteryuniversity.com/learn/article/bu_216_summary_table_of_lithium_based_batteries

Currently assuming cycle efficiency applies to charging, with discharge & 100%. Needs some refinement

## Battery Initialisation
Assuming only a central battery at this stage:
Is the battery attached to the `eno` or to `resident['cp']`?? Currently, to `eno` set up in 
`eno.initailiseBuildingBattery(scenario)` 

## Battery calcs
'eno.calcDynamicEnergy(step)' calculates flows for whole network. calls battery charge / discharge functions
For individual batteries, need to move this function to `Customer` class

NB when 'eno.calcDynamicEnergy(step)' is carried out, `eno.calcBuildingStaticEnergyFlow` has already
been carried out and so has calculated imports and exports for all residents for all timesteps (inc `'cp'`
) and aggregated these as `eno.load` and `eno.generation` 

Process at each timestep is this:
If `pv > load` then charge 
if `pv < load` and in `discharge_period`,  then discharge
if `pv <= load`and in `additional_charge` period, then charge

*BUT* what if pv <= load and time is in `charge_period` AND time is in `discharge_period`?)
Answer: `discharge_period` trumps `charge_period`. So if network load requires energy from the battery 
within discharge period, use it, don't try and charge from grid in `discharge_period`.
(This scenario is unlikely because `charge_period` and `discharge_period` should be exclusive.)

NB, although this does do some demand shifting, (i.e. charge from grid in `charge_period` and discharge to meet load in `discharge_period`), it doesn't discharge to the grid. A TOU FiT would make it worth looking at this arbitrage strategy.)

##TESTING
1) Set up a simple network: 2 units, plus cp. simple load profile and pv profile
- can i do 1 week or 1 day??
2) log generation, import, export, soc to csv
3) run different scenarios

##STRUCTURE ISSUE
_Still_ not right:
Is it nomenclature or structure?
`eno.generation` is sum of exports from all residents and cp
`eno.load` is sum of imports from all residents and cp
- Bad name choice. But they have these names because 
`Customer.calcStaticEnergy` uses `.generation` and `.load` to calculate `.imports` and `.exports`

One possibility: (new branch - `change_network_structure`) is to __NOT__ call `.calcStaticEnergy` for `eno` but
instead do the calcs in `eno.calcBuilding StaticEnergyFlows`

Code to be replicated / changed is this:

        `self.flows = self.generation - self.load
        self.exports = self.flows.clip(0)
        self.imports =  (-1 * self.flows).clip(0)`
Scrap this line:
        `self.local_imports = np.minimum(self.imports, self.local_quota) # for use of local generation`
        (Don't need `local_imports` for `eno`)
Also, refactor:
    `Network.load` to `Network.cum_resident_imports`
    and `Network.generation` to `Network.cum_resident_exports`
    
So, also look at `Network.calcDynamicStorageEnergyFlows`
and make same refactors there.

Now, log the *actual* load and generation totals instead.
ALL GOOD for pv , but battery is all to cock:
5kWh does seem to have gone into the battery when there is excess PV, but `SOC` and `battery_charge_kW` is wrong.

Merge above changes and back to `Battery` branch:

OK. Small discrepancy in Battery SOC because of charging efficiency:
`ammount_to_charge` is calculated using capacity - charge held, but then less is actually added because of efficiency
Divide spare battery capacity by efficiency. This is all assuming that cycle efficiency acts on charging.
OK.
But, battery does not discharge:

step is an integer not a timestamp, so when looking to see if `step` is in `discharge_period`,
use `self.ts.timeseries[step]`

OK
__N.B.__ Discharge Period set to start at `18:00` only starts discharging at `18:30`

Problem with the control strategy 3. with off-peak charge from grid:
- still only 1 discharge period, so 'single-cycle' 
- means battery is already full when there is excess PV.
So double-cycle should have additional discharge period.
ok, GOOD. 

3 MORE THINGS:
1) WHY ANOMALLY WITH STARTING AT 00:00   AND WHY IS 1ST TS 30 MINS AFTER START OF PERIOD?
2) iSSUE IF PERIOD RUNS OVER MIDNIGHT
3) Separate battery tariff_lookup file and battery control tariff_lookup file

3)OK. Tick
1) This comes from tariff periods. If tariff runs from 16:00 to 20:00,

*__ASIDE Panic:__ The whole model should be running in kWh 
------------------------------------------------------ but kW may have crept in.....
Check vb loads (again):
cp: Site A is huxham 1 (208 units) cp load is around 38 in original datafiles. 
Is 19 in vb profiles. ie 19 kWh / 30 minutes is 38 kWh / hour is 38kW. So good.

email from GH 3/11/15: "attached is 12-months 30min kW interval data "

sgsc: 
e.g Site G - vb 001:
Customers 0-4:
10050420	10359364	10208114	8629119	10922644
1st load reading:
0.085	0.117	0.065	0.337	0.153
(these from vb profiles)
Look at original sgsc (`generl_units_all_kWh') - get the same readings.*
***ALL GOOD***

__ALSO__
Check PV profiles too: e.g. `Site_A` has kWpeak is 47kW.
Max reading is ~20kWh/half hour = 40kW

__*ALL GOOD*__

Back to periods:
So, 30-min readings are kWh in the period ending? at the time given. Assumed this, is it true??
So 6am reading *ends* at 6:00 so is *outside* period that starts at `0600`.

OK. Next 2) Allow periods that span midnight:
Tick. Need to extend to tariffs

3/4/18
*__ANOTHER ASIDE__* Found a bug in the solar tariff calculations,
*where solar instantaneous quotas were being calculated when there was no solar tariff
or even where there was no en.
Fixed in `Battery` branch.*


__BATTERY CAPEX__
Two elements:
* `capex_bat_inv` Inverter may need replacing, depending on `life_bat_inv` compared to amortization period
* `capex_bat` Battery replacement depends on `max_cycles`

`initialiseAllCapex` is refactored to `allocateAllCapex` 
and moved to end of the iterative cycles . Has to be called once per load_profile to allow for scenarios
where `pv_capex` is allocated according to load 
capex must be calculated before `scenario.calcFinancials`

Adding Battery to All Customers
-------------------------------
13/4/18
* Add individual battery columns to `study_....csv` 
* refactor `initailiseBuildingBattery` to `initailiseAllBatteries` 
   and Initialise  batteries for customers as well as central bat
* Move `dispatch` from `Network` to `Battery` 
* Call `calcDynamicEnergy` for all customers and `eno`
    - initialise `flows` using `generation` and `load` for `Customer`
* Also make `ts` global
* Dispatch individual batteries
* then calc `cum_resident_exports`
* Then dispatch central bat
* Possible issues with local quotas for solar tariffs - ***#TODO Come back to this***
  __Question:__  central (eno) battery vs `cp` battery??
* central battery has to be treated differently to customer battery
* (But note inconsistency: strata pv is treated as belonging to resident 'cp').
  Anyway, is there poss scenario of having central battery *and* `cp` battery???
  No, but could have `cp` battery in non-en scenario (as for `cp` having pv)`
  manage this with inputs: run battery calcs for all residents inc `cp` but Don't give cp battery and central battery
* See table in `morePVs_setup_instructions`

deBugging battery 20/4/18
-----------------------

* individual batteries not having expected impact on output
* scenario 0 running twice??????
* timeseries output doesn't include ind batteries.  Maybe create cumulative SOC?

  ***was this resolved??***

   I think it was
