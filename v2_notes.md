#Change log for `morePVs_v2`
**22/8/19**
Annotated changes made to `morePVs_v2.py`. These are recorded here, with rationale, in order to reproduce them applied to `energy sharing` model.

Principal chages to be made are:

0. A bit of tidying up and improved documentation.
 [] allow .csv spec for load files instead of folder
 [X-ish] Remove Solar daily block and solar instantaneous quotas for allocating central PV within and EN
 
1. Enable combined `load-pv` net load profiles to be used for customers within an `en`
2. Enable customers within an EN to have individual PV 
3. Enable customers within an EN to have individual BESS
4. Specify network tariffs for `bau`, `btm_i`, etc. arrangements to enable calculation of retailer and DNSP profits.


##1. Combined `load-pv` profiles
- Set up sample profile including negative load and run it, see wh'appen `study_test_net_load`
using `W_building_profile_kWh_net.csv`
- It runs. So compare `bau` with net load to `btm_i_c` with pv and load
- seems to give correct bills, nice, but doesn't calculate capex because is `bau` scenario,
so try again with `btm_i_c` arrangement and an empty pv_profile.
- Still no capex, because, for `btm_i`, capex is allocated according to proportional
 distribution of PV in `Network.allocateAllCapex()` and there is no PV, so this will always be an issue.
- This is a problem inherent to using Net Loads, because there is no information about the PV so costs cannot be allocated. 
- **Net loads don't work for `btm_i` arrangements**

- What is the desired use case in `en`?? Can we ignore capex of the PV included in the Net Load?
If so, all good: Add indi PV to en first and then Net Loads will follow....

##2. Individual PV in an EN
 Need to confirm / modify:
   -  `eno.calcBuildingStaticEnergyFlows()` [x] 
   - `eno.calcBuildingDynamicEnergyFlows(step)` [x]
   - `Customer.calcStaticEnergy()` [x]
   - `Customer.calcDynamicEnergy()` [x]
   - None of the above need changing
   
   
   Need to incorporate separate central and indi PV capex into the `study_....csv` file
   and 
    -  `Network.__init__` reads capex values 
   
   Questions:
   
    -  Is this a separate `xx_pv_capex_id` for each resident and for central?
    -  Are these also used for `btm_i_` etc.?
    -  Is there an `all_pv_capex_id` that overrides?
    -  Need to maintain backward compatibility:
        - If only one `pv_capex_id` then:
            If `en` pr `en_pv`, rename it `pv_capex_id_central`
            If `btm_i`,`btm_s` or `btm_p` rename it `pv_capex_id_all`
            If `cp_only`, rename it `pv_capex_id_cp` or include this in line above      
                  
   Or (better?):
   
        -  for each pv system: `xxx_pv_kWp`
        -  for each scenario: `pv_capex_id` ONLY ONE id
        -  if `pricepoint` in `pv_capex_id` then :
               - selec sys cost / w and pv cost / w according to size bands (`sys_0_10`, `sys_0_20`)
               - pv capex = `xxx_pv_kWp` * sys cost/w
        - if not, use legacy method
        -  MAY ALSO need to look at how individual pv_profiles are scaled.
  
  
   THIS IS COOL, except that in some arrangements (`btm_i` where the generation profile has been distributed 
   between customers), the pv system size is not known, so must calculate as a share of `kWp_total`
   

   
 | Arrangement   | pv_profile | pv_capex allocation  | BESS capex allocation |  Changes |
 |----|-------|----------|-------|-------|
  | `bau_bat` |   |  |   |   |
 | `btm_i`  | multiple individual pv profiles | allocated according to generation  allocation  | | Use `kWp` for each system to calc capex |
 | `btm_i`  | single profile divided up (cp share according to load) | allocated according to generation  allocation | | Calculate `kWp` for each system as share of `kWp_total`|
 | `btm_s`  | single shared profile | shared between units | | Allow $/W bands, No change |
 | `btm_p`  | single shared profile | Paid by solar retailer | | Allow $/W bands, No change |
 | `en_pv`  | single central profile | paid by ENO  | | Allow $/W bands,No Change |
 | `en_pv` with indi pv | Central pv capex paid by ENO | | Allow $/W bands, add separate capex values|
 | | Individual pv capex paid by customers | | |
  
  
  Currently, `Scenario.__init__` calculates single capex and repayment for PV, for BESS and for EN.
  These are shared amongst stakeholders in `Network.allocateAllCapex` because some (`btm_i` is load-dependent)
  **So, is it BETTER, is to scrap load-dependent allocation of PV??**
 
  
### Changes:

- **`Scenario.__init__` [ ]**
   - [x] Read ALL `pv_kWp`s and `pv_capex_id`s, including `pricepoint`
   - [x] Identify `pv_capex[pv_system]` (for `pv_system` including units, 'cp' and 'central')
   - [x] Calc pv capex repayments for each `pv_system`
   - follow through in `Network` and `Customer` functions to convert `pv_capex` and `pv_capex_repayments` to dicts.
    -  `Network.allocatePV()` [x] 

- **`Network.allocatePV` [ ]** 

N.B. this will need to allow for individual AND central PV in the same pv profile file.
   *MAYBE* it already does allow for this, in which case the only issues is capex?
    -  [ ] Need to test en with indi PV
    
   - [o] `Customer.initialiseCustomerPV()` 
   - [o] `Customer.calcCashFlow()` 
   - [ ] **`Network.allocateAllCapex()`**    *Here is the key change.*
       - [x] Add individual pv for each resident in `en` arrangement
       - [ ] Change calc of pv capex for `btm_i` with individual pv's - will also need changes to `Scenario.__init__`
  
 ##3. Individual BESS in an EN
 - [o] `Battery` No changes needed]
 - [o] `Scenario.__init__`  No changes needed
-  [o] `Network.allocatePV()` No changes needed
-  [o] `Scenario.calcFinancials()`
-  [o] `Scenario.collateNetworkResults()`
-  [] `Scenario.logScenarioData()`  
-  [o] `Network.initialiseAllBatteries()` No changes needed
-  [o] `Network..resetAllBatteries()`  No changes needed
- [o] `Network.calcBuildingDynamicEnergyFllows()`  No changes needed
- [o] `Network.calcBuildingStaticEnergyFllows()`  No changes needed
 - [] `Network`
 - [o] `Customer.calcCashFlow()` No changes needed
 - [o] `Customer` everything else: No changes needed

   - [o] `Network.allocateAllCapex()`   
       - [o] Add individual battery capex for each resident in `en` arrangement. No change needed - already done
       - [ ] 


##BIG QUESTION
Will it work with `en_pv` arrangement with individual pv but no central pv.