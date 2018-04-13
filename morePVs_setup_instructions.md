#morePVs model
morePVs Copyright (C) 2018 Mike B Roberts

multi-occupancy residential electricity with PV and storage model
 
*This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
Contact: m.roberts@unsw.edu.au*

###Setup Instructions

All input parameters for each study are contained or referenced in `study_xxxxxxx.csv` file.

`scenario` :    Scenario identifier (integer)

`output_type`:
This column lists output formats required, applied to the whole study, not individual scenarios.
All other parameters are given *per scenario* i.e. per line of `.csv` file.




---
PV:
---
Name of pv file - 1 year's output within `DATA_EN_3\pv_profiles`

For `en` or `cp` arrangement, pv file has single column, must be 'cp'

For `btm_i` : btm individual:  en has column for each unit, or if not, single 'cp' or 'total' column that is split equally

For `btm_icp` : en has column for eadch unit and cp. Or, single column: cp gets share according to load share; units get equal share of remainder

For Shared btm inc cp:  `btm_s_c` A single `total` or 'cp' column that is split according to instantaneous load between all units AND cp

For Shared btm Units only:`btm_s_u` single `total` or 'cp' column that is split according to instantaneousload between all units EXCLUDING cp

For en_external scenario: `cp tariff != TIDNULL`

Scaleable PV:
-------------
filename of 1kWp PV output is `pv_filename` column

`pv_scaleable = TRUE`

`pv_kW_peak` = value to scaleby, eg 50 for 50kWp

In this case, `pv_cap_id` refers to a scaleable capex scenario with capex and repayments also scaled by `pv_kW_peak`
NB - use of this should be restricted to system sizes with equal $/kWp capex

-----
LOADS
-----
`load_folder` contains the name of sub-folder within `base_path\load_profiles` that contains the load profile(s)
Can be a single file or multiple files for multiple iterations
Load files contain: 
    `timestamp` (first column) in format `d/mm/yyyy h:mm`
    30 minute timestamps assumed. Up to 1 year (17520) but can be less.
    customer load columns (in kW)
    `'cp'` (optional) common property load (kW)
    

If multiple loads for each scenario, they must all have the same list of customers within the folder,
BUT each scenario can have different number of residents, etc.

-----
CAPEX
-----
capex scenarios for en and pv are included in reference file
amortization a_term (years) and a_rate (%) are included in study_....csv file
a_rate is decimal e.g. `0.06` NOT `6%` or `6`
NB if `capex_en_lookup` has duplicate `capex id`s, it all goes to cock. (read_csv retrns series instead of single value).

`pv_capex` is full system cost (*including inverter cost * ), after rebates and including GST
`inverter_cost` is only required if `inverter_life` > amortization period

-------
TARIFFS
-------
If all_residents has a tariff, it applies to all households (not cp) either internally for en arrangement or externally for bau btm etc.
If all_residents tariff is not given, each houshold can have its own tariff code
'Static tariffs' are calculated independent of energy flows; 'dynamic' tariffs calculated for each timestep dependent on network status 
(e.g. cumulative load, pv generation, battery state). Dynamic tariffs are identified by having `Block` or `Dynamic` in the the `tariff_type`

'cp' tariff:
-----------
In `en` scenarios, If ENO  is the  strata body, `cp tariff = TIDNULL`,
		If ENO is not the strata  cp tariff is what strata pays ENO for cp load
		
Discount
--------
% discount applied to fixed and volumetric charges
		
Solar Tariffs
-------------
`STS_xx`  Solar TOU Tariff based on peak, shoulder and off-peak solar periods with rates at xx% discount from EASO TOU rates
`STC_xx`  Solar TOU Combined tariff based on EASO TOU periods, with additional off-peak solar period and xx% off EASO TOU rates

`SBTd_xx_yy` Solar block TOU tariff (daily):
                Based on TOU with `xx%` discount 
                and each customer having a fixed daily quota of solar energy, based on total annual generation during solar period
                cp allocated a fixed % (`cp_solar_allocation` given as decimal (`0.yy`)in `tariff_lookup.csv`) and 
                the remainder shared equally between units.
                
`SIT_xx` Solar Instantaneous TOU tariff : 
                Based on TOU with `xx%` discount
                and each customer having a quota of solar energy, based on % of instantaneous generation at that timestamp 
                after cp load has been satisfied. This is *not* a block tariff. l`local_import` is calculated statically                                       

`CostPlus_xx`   Based on bills paid at parent tariff + xx%. Fixed costs (and CP?) shared evenly; Volumetric costs shared by usage; 
                How best to deal with demand charges? 



'parent' tariff
---------------
For Non EN scenarios (bau, btm, cp_only, etc.), parent tariff must be `TIDNULL`, while cp tariff is paid by strata.

-------
BATTERY
-------
__For central Battery__
In `study_xxxxxxx.csv` file, battery is identified by `battery_id` and battery control strategy by `battery_strategy` 
If `battery_id` and `battery_strategy` are in the headers, then both must be supplied; 
If `battery_id` and `battery_strategy` are NOT BOTH in the headers, then battery is not included.

__For Individual Batteries__
Batteries are identified by `x_battery_id` and battery control strategy by `x_battery_strategy` 
    where `x = customer id` from load file


__Battery Characteristics__
All battery technical data is kept in `reference\battery_lookup.csv`
`battery_scenario`  - identifier unique to battery characteristics and control strategy
`capacity_kWh`      - Single capacity figure
`efficiency_cycle`  - for charge and discharge (default `0.95`)
`charge_kW` - for charge and discharge. constrained by inverter power and/or max ~0.8C for charging. Defaults to `0.5C`
`maxDOD` (default `0.8`
`maxSOC` (default `0.9`)
`max_cycles`(default `2000`)

`battery_cost`: Installed battery cost *excluding* inverter, including GST
`battery_inv_cost` : Installed cost of battery inverter, inc GST
`life_bat_inv` : lifetime of battery inverter (years)) (Defaults to capital amortization period `a_term` )



__Control Strategies__
kept in `reference/battery_control_strategies`

`discharge_start1` and `discharge_end1` (optional) Discharge *only* allowed between these hours 
or these hours: `discharge_start2` and `discharge_end2` 

Optional additional grid-charging period
`charge_start` and `charge_end` 
`discharge_day1` , `discharge_day2`and `charge_day` (=`both`) `week`, `end` or `both` : days to discharge / charge



------------
OUTPUT TYPES
------------
Column `output_type` in `'study_...csv` *applies to all scenarios*

`log_timeseries_csv`: Creates a `.csv` for each scenario and load profile, containing:
total load,total import & export for building, total generation, battery saved charge


    