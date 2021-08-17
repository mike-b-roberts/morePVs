#Designing `finance2` study:
For each site, look at `finance1`, choose appropriate parameters and then run for $250 / kWh and different battery strategies.
For all sites, `20 years` and `TOU12` give the most battery-friendly environment, so start with these.

###Site J

![](https://i.imgur.com/ox7hknk.jpg)


-  PV  1- 2 kWp/unit drives positive npv, but larger PV redices npv
- battery reduces npv with this strategy, except for oversized PV, 

whereas, with a Fit:
![](https://i.imgur.com/YyPQxCv.jpg)

- npv keeps increasing with PV.

Can strategy be adjusted so that:
- battery increases npv compared to PV only
- npv continues to increase with PV

### Main parameters:
- 20 years
- TOU12
- capex_med
- PV: full range
- KWh: 0,1,2

### bat Strategies:
Need to run a script to extract from `energy4a` and `energy4b`:

- delta(SS)
- delta(SC)
- delta(pd)
for each strategy
- either for specific kWp, kWh, or find the max across all kWp-kWh combinations.

 - `ch` strategies (ie charge-priority) are the only ones to date with any significant reduction in peak demand with `1700` preferable for 4 sites, but `1600` preferable for site J
 - Self-sufficiency: `ed1700_s_cmax` gives max increase 
 - Self-Consumption: With `ch`, BESS reduces SC, with `ed` it increases.  	
	so `ed1700_s_cmax` ispreferable

- `ed1700_s_cmax`
- `ch_ed1700_s_cmax`
- `ch_ed1600_s_cmax`

So....
Compare financials for:
-  `ed1700_s_cmax` and `ch_ed1700_s_cmax` for 4 sites
-  `ed1700_s_cmax` and `ch_ed1600_s_cmax` for site J

PLUS: New peak strategy:?? 


    ***Meanwhile...***
    ##`cponly_` study
    same strategies for energy and financial ouputs  with PV applied to cp only
    
    
***Meanwhile....
## PeakDemand strategy:
* Discharge ***only*** when total import >= x% of peak load 
* for x = 80 / 90 / 95% ??
`morePVs` branch: peak_demand

1st test run: 90% gives better peak reduction that 80% or 95% if applied at any time.
Worth running some tests and plotting delta(PD) vs %threshold

## `finance2` results:

running a range of strategies:
 
* @ $250/kWh, BESS can increase NPV and PV-BESS combo wins for most sites

 (not `F`)
* $500 / kWh is close* to working for a number of scenarios.
* Look at those scenarios and run for 
	 $200, $300, $400, $500 /kWh