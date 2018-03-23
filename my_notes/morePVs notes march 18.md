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


So, it *looks* __good__

Tidy up: Then git, then test.

    

 