
20/4/18 : Optimisation
----------------------

1. Preload load profiles
If not `different_loads` - ie different load profile for each scenario,
read all load files at `Study.__init__`
If `different_loads`, read all load files at start of `Scenario.__init__`

That way, shouldn't have implications for threading....:


Run study_test7b and compare results with test 7. All good.


1. PV files are read per load profile. change this to per scenario
2. Move from `Network.__init__` to `Scenario.__init__`


__Major issue:__

Allocating `self.pv` = `scenario.pv` is not making a copy, so
when `self.pv` is changed, it affects `scenario.pv`
Can sort this but where else is this an issue?????
*sorted*

I want to put the threads back, because it's too slow......
There may be more `Lock`s needed
*sorted*

1. next big one is to seperate kWh from $ calcs. Not now.


__Issue in battery calc  / dynamic energy calcs:
Some imports are `nan`, because both `generation` and `load` include `nan` values
- issue is due to missing `maxSOC` parameter in `ballery_lookup.csv' - now defaults to `1.0`
__RESOLVED__

With battery (ie dynamic) calcs, scenarios take approx 3 minutes each (without threading)
(146seconds , but that includes some static scenarios)
Ouch.  Bring back threads!

24/4/18
Running 6 threads with dynamic calcs, cpu usage is seemingly
not the limiting factor, and network activity is high. __
Why?__
* There is still some csv read and write, but limited to once per `Scenario`
unless timeseries logging is specifically requested.

NB running `value5` using 5 processes with 6 threads. No Battery (ie static calcs). Approx 2.5 hours for all sites



## Timings 29/5/18

Running dynamic_timings.csv 

6 dynamic `en_pv`  scenarios (central battery)

1) No threading

Completed 7 scenarios in 1438.000000 **************
29/05/2018 09:37:03 AM  ********* Time per Scenario is  205.428571

2) threading:

Completed 7 scenarios in 1488.000000 **************
29/05/2018 10:17:15 AM  ********* Time per Scenario is  212.571429 *********



But, TBF, threading run had some other plotting going on, so much of a muchness.



***So, say 4 mins per scenario.***



