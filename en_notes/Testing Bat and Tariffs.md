##Testing morePVs Battery branch before Merging
4/4/18

1) Test Battery Functionality

* Use 2-3 day load profile 



2) Test Solar Tariffs

plotting is in `en_utilities\plot_battery`

`test_bat3` study: 
* 02 `no_time_constraints` - battery does not discharge
* 03 `evening_discharge` - charging rate is very fast but does not reduce import by much
* 04 `single_cycle_1` 
* 05 `double_cycle_1` and  06 `test_cycle` are the same

*fixed bugs*
Now, 02,03 and 04 give same output.
* `no_time_constraints` and `evening_discharge` will be same as time period for `evening_discharge` is when discharge would've been anyway
* `evening_discharge` and `single_cycle_1` difference is `22:00` to `04:00` charging window, 
* `single_cycle_1` is Not doing overnight charging 
ISSUE was that evern though `charge_period` was set, `discharge_period` was set to whole of `ts` and took precedent.
Now sorted, BUT __maybe `charge` should take precedent??__

Anyway, 
    Battery now seems to work, __still need to log and verify battery costs__


Individual Batteries Added
--------------------------

20/4/18
Issue with ind batteries, not charging..:
1.  get rid of threading.
__OF COURSE IT DOESN'T CHARGE - it has no PV!__
2.  Try `single_cycle_1` strategy





__25/5/18__

-----------



Added battery capex calcs.

Retesting with 

`project='EN1a_pv_bat2'`
`study_name='siteJ_bat2_test1'`

Jupyter: `Battery testing 2`

there is an issue with `en_pv` where `en_export` and `total_grid_export` are different, but maybe is OK actually: 

* `total_grid_export`  and `total_grid_import` have no meaning in this scenario. It is `en_export` plus internal exports .

testing: Looks ok.  storage with `btm_i` kicks in more gradually and discharges more gradually



