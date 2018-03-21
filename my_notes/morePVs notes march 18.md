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

 Principal functions to address are:
 
   `Customer.calcCashFlows`
        Contained in `scenario.calcResults(eno)`
   
   Possibly, `Network.calcDynamicEnergyFlows` 
            `Customer.calcDynamicTariffs`
            
`Customer.calcCashflow`
        self.cashflows = \
            np.multiply((self.imports - self.local_imports),self.tariff.import_tariff) \
            + np.multiply(self.local_imports,self.tariff.local_import_tariff) \
            - np.multiply((self.exports - self.local_exports),self.tariff.export_tariff) \
             - np.multiply(self.local_exports,self.tariff.local_export_tariff)
         # These are all 1x17520 Arrays. 
         # local_tariffs are for, e.g. `solar_rate` energy, maybe alo p2p later
         
        
        self.local_exports = 0
        self.local_imports = 0