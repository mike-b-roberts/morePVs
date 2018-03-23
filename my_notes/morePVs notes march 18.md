## morePVs working notes

21/3/18
Issues with Solar Block Tariffs
-------------------------------
- SBTi is not a block tariff. It can be calculated for whole period (year), assuming no demand shifting
- More major issue is that currently tariffs may be calculated dynamically, but bills are still calculated statically. 
ie a tariff rate is allocated for each time step. this is __bad__.
- Need to cal $ dynamically. 
ie for each timestep:
    calc solar rate x allocation (or x load if less)
    calc base rate x residual load
- this also affects quarterly block tariffs, but current approximation (each step is either inside block or outside block)
works better for quarterly period. It is less good for daily period
and bad for instantaneous.
- Maybe this means reworking the whole f***ing model??

__Nah!__

 These changes:
 --------------
   `Customer.calcCashFlows`
        Contained in `scenario.calcResults(eno)`
   
   Possibly, `Network.calcDynamicEnergyFlows` 
            `Customer.calcDynamicTariffs`
            
`Customer.calcCashflow`

        `self.cashflows = \
            np.multiply((self.imports - self.local_imports),self.tariff.import_tariff) \
            + np.multiply(self.local_imports,self.tariff.local_import_tariff) \
            - np.multiply((self.exports - self.local_exports),self.tariff.export_tariff) \
             - np.multiply(self.local_exports,self.tariff.local_export_tariff)
         # These are all 1x17520 Arrays. 
         # local_tariffs are for, e.g. `solar_rate` energy, maybe alo p2p later`
         
`Customer.initialiseCustomerLoad:`

        `self.local_exports = np.zeros(self.ts.num_steps) # not used, available for local trading 
        self.local_imports = np.zeros(self.ts.num_steps) # used for import of local generation    `
        
 `Network.calcDynamicEnergyFlows` - only for storage. don't adjust now
 
 For __instantaneous solar tarifs__
 `Customer.calcStaticEnergyFlows:`
 
 `    self.local_imports = np.minimum(self.imports,self.local_quota)`
 
 Where is `local_quota` calculated?
 For __instantaneous solar tarifs__, it's based on eno.generation and allocated%
 - calculated for the eno:
 `network.initialiseBuildingLoads:`
 
        if self.pv['cp'] > self.resident['cp'].load:
            for c in self.households:
                self.resident[c].local_quota = (self.pv['cp'] - self.resident['cp'].load) / len(self.households) # for all timesteps
        else:
            self.resident[c].local_quota = np.zeros(self.study.ts.num_steps)
 
 
 For __Solar Block Daily tariff__, need to calc local_imports dynamically based on Customer.allocated_kW
    
So, either in  `Network.calcDynamicEnergyFlows` or new dynamic function `calcLocalAllocation`

or `Tariff.calcDynamicTariffs`
- if here, maybe adjust method for block tariffs too? Maybe not.

Actually, do it here:

`Customer.calcCustomerTariffs`

    `self.steps_since_reset = np.mod((step - scenario.block_quarterly_billing_start),
                                                    scenario.steps_in_day)
    self.prev_cum_energy = self.cumulative_energy
    self.cumulative_energy = customer_load[step - self.steps_since_reset:step + 1].sum()
    if self.cumulative_energy <= self.daily_local_quota:
        self.local_imports[step] = customer_load[step]
    elif self.prev_cum_energy < self.daily_local_quota \
        and self.cumulative_energy > self.daily_local_quota :
        self.local_imports[step] = customer_load[step] - self.daily_local_quota / self.steps_in_day
    else:
        self.local_imports[step] = self.daily_local_quota / self.steps_in_day`

To confirm,  __instantaneous solar tarifs__ is not dynamic, but __Solar Block Daily tariff__ is dynamic

For __Solar Block Daily tariff__, need to allocate  value to `Customer.daily_local_quota` for all residents, 
dependent on `solar_cp_allocation` - can be done per `Scenario`, but AFTER pv has been initialised, 
needs data from the tariff so better to do it in `Network` class:

(Could be `Network.allocatePv(scenario)` but better is new function):
 
 `def initialiseLocalQuotas(self, scenario):

        # Check that all residents have same solar_cp_allocation basis , otherwise raise an exception:
        allocation_list = list(set((self.resident[c].tariff.solar_cp_allocation for c in self.resident_list)))
        if len(allocation_list) >1:
            sys.exit("Inconsistent cp allocation of local generation")
        else:
            solar_cp_allocation = allocation_list[0]
        # Calc daily quotas for cp and households:
        self.resident['cp'].daily_local_quota = self.pv.loc[self.resident['cp'].solar_period,'cp'] * solar_cp_allocation / 365
        for c in self.households:
            self.resident[c].daily_local_quota = self.pv.loc[self.resident[c].solar_period,'cp'] * (1 - solar_cp_allocation) / (365 * len(self.households))`
        
  Only call this if needed:
   if scenario.has_solar_block:
                eno.initialiseLocalQuotas(scenario)
  
___ 22/3/18___ 
---------------

To recap:
------

* `Customer.local_imports` (and `local_exports`) are set ito zero in `Customer.initialiseCustomerLoad`

For __Solar_Block_Daily__:

* calculation is dynamic
* `Customer.daily_local_quota` (single number) is set in `Network.initialiseLocalQuotas(self, scenario)`
* In `Customer.calcCustomerTariffs` `Customer.local_imports` is calculated for single `timestep` based on cumulative daily energy and `Customer.daily_local_quota`
* `Customer.local_imports` is calculated dynamically, but `Customer.cashflows` is still done statically *afterwards* in `Customer.calcCashflow` called from `Scenario.calcResults`


For __Solar_Instantaneous__:

* Calculation is static.
* `Customer.local_quota` is % of instantaneous generation charged at solar tariff, and is set in `network.initialiseBuildingLoads` for all timesteps
* `Customer.local_imports` for all timesteps is calculated in `Customer.calcStaticEnergyFlows` as the minimum of `Customer.imports` and 'Customer.local_quota'
* In `Customer.calcCashflow`, `local_imports` (and `local_exports`) are used to calc `Customer.cashflows` as 17520 array, 
            using `solar_tariff` for local_imports` and residual tariffs for `imports`'

* For both, `Customer.Tariff.solar_import_tariff` is set as a 1x17520 array with the solar tariff rate, and non-solar reverts to `import_tariff` rates
So, it *looks* __good__

###Tidy up: Then git, then test.
Start by running previous study to check it's not broken.
(Then set up trial data for solar tariffs,. May need to make some of the above changes *conditional*.)
2 problems in `Network.initialiseBuildingLoads`
        `if self.pv['cp'] > self.resident['cp'].load:
            for c in self.households:
                self.resident[c].local_quota = (self.pv['cp'] - self.resident['cp'].load) / len(self.households) # for all timesteps
        else:
            self.resident[c].local_quota = np.zeros(self.study.ts.num_steps)`

* 1 This calc is happening and ot doesnt need to, should be if `has_solar_instantaneous_tariff`
* 2 Need to compare individual timesteps

en_notebooks/solar_tariffs.ipynb 
    `        for c in self.households:
            self.resident[c].local_quota = np.where((self.pv['cp'] > self.resident['cp'].load), \
                                                    (self.pv['cp']- self.resident['cp'].load)/len(self.households),0)`
is much neater too. Q what format do i want? array or df or series?? I think `np.array` is good
 
 Issue because `local_quota` is not set for `'cp'` but it needs a vlaue in `Customer.calcStatic EnergyFlows`
 Should calculate it for cp so `Network.initialiseBuildingLoads` iterates over `resident_list` instead of `households`
 BUT, also then need to ensure `solar_rate` is zero for `'cp'` and `solar_import_tariff` is array of zeros
 * BTW, above assumes that if one resident is on solar tariff, they all are... this could be changed later in calculating quotas
 * but in any event, 'cp' can be on non-solar tariff (certainly `TIDNULL` but possibly others)
 
 Issue: `Customer.calcStaticEnergyFlows` wants to calculate `Customer.local_imports` even when `Customer` is the `Network`
    but `Network` doesn't have `local_quota` nor dies `retailer`
    so set `self.local_quota = 0` in `network.initialiseBuildingLoads` 


Issue:
btm_icp - there is no `Network.pv`    maybe because `Network.allocatePv` is called before `resident.load` exists?
Issue is for `pv_allocation = 'load_dependent'`
- goes to `initialiseBuildingLoads` before `allocatePv`
Need to take initialisation of instantaneous quotas OUT of `initialiseBuildingLoads` and make new function
`Network.initialiseSolarInstQuotas`
Also renameing the existing `initaliseLocalQuotas` to `initialiseDailySolarBlockQuotas` in the name


OK, first run it doesn't look broken. But some error in morePVs_output line 102, looking up # units in building
For now, comment out output
Git again and 
Now set up test data    