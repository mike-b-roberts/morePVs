#Apartment Network Model
###Setup Instructions

All input parameters for each study are contained or referenced in `study_xxxxxxx.csv` file.

`output_type`:
This column lists output formats required, applied to the whole study, not individual scenarios.

---
PV:
---
Name of pv file - 1 year's output within `DATA_EN_3\pv_profiles`

For en or cp arrangement, pv file has single column, must be 'cp'
For `btm_i` : btm individual:  en has column for each unit, or if not, single 'cp' or 'total' column that is split equally
For `btm_icp : en has column for eadch unit and cp. Or, single column: cp gets share according to load share; units get eqaul share of remainder
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
include folder name even if only a single file
folder within `DATA_EN_3\load_profiles`
If multiple loads for each scenario, they must all have the same list of customers within the folder,
BUT each scenario can have different number of residents, etc.

-----
CAPEX
-----
capex scenarios for en and pv are included in reference file
amortization a_term (years) and a_rate (%) are included in study_....csv file
a_rate is decimal e.g. `0.06` NOT `6%` or `6`
NB if `capex_en_lookup` has duplicate `capex id`s, it all goes to cock. (read_csv retrns series instead of single value).

-------
TARIFFS
-------
If all_residents has a tariff, it applies to all households (not cp) either internally for en arrangement or externally for bau btm etc.
If all_residents tariff is not given, each houshold can have its own tariff code
'Static tariffs' are calculated independent of energy flows; 'dynamic' tariffs calculated for each timestep dependent on network status 
(e.g. cumulative load, pv generation, battery state). Dynamic tariffs are identified by having `Block` or `Dynamic` in the the `tariff_type`

'cp' tariff:
-----------
In `en` scenarios, If ENO  is the  stratabody, `cp tariff = TIDNULL`,
		If ENO is not the strata  cp tariff is what strata pays ENO for cp load
		
Discount
--------
% discount applied to fixed and volumetric charges
		
Solar Tariffs
-------------
`STS_xx`  Solar TOU Tariff based on peak, shoulder and off-peak solar periods with rates at xx% discount from EASO TOU rates
`STC_xx`  Solar TOU Combined tariff based on EASO TOU periods, with additional off-peak solar period and xx% off EASO TOU rates

`SBTd_xx` Solar block tariff (daily):
                each customer having a fixed daily quota of solar energy, based on total annual generation during solar period
                cp allocated a fixed % (`cp_solar_allocation` in `tariff_lookup.csv`) and 
                the remainder shared equally between units.
                
`SBTi_xx` Solar block tariff (instantaneous): 
                each customer having a quota of solar energy, based on % of instantaneous generation at that timestamp 
                after cp load has been satisfied                                        

`CostPlus_xx`   Based on bills paid at parent tariff + xx%. Fixed costs (and CP?) shared evenly; Volumetric costs shared by usage; 
                How best to deal with demand charges? 



'parent' tariff
---------------
For Non EN scenarios (bau, btm, cp_only, etc.), parent tariff must be `TIDNUL`, while cp tariff is paid by strata.