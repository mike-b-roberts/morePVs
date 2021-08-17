en_3.py

Revision Notes 9/3/18

en.initialiseNetPv is inside scenario / load loop (which is slow)
- it only needs to be for btm_s_u and btm_s_c arrangements,
so move outside load loop and add conditional call inside loop

en.InitialiseNetCapex can be calculated independent of load. Capex depends on pv allocation 
Only for btm_i scenarios where a single pv profile has been provided that needs to be allocated
Previous version en_var_2.1 had pv capex allocated acording to pv allocation for ALL btm arrangements.
This is wrong. btm_s must have capital costs allocated independent of load. So share equally.

capex repayments:
previously came from csv. In order to explore more possibilities, calucalte them from capital cost, years and rate of amortization
scenario.en_capex_repayment
scenario.en_opex
scenario.pv_capex_repayment
 - all are nor calculated in Scenario.__init__

-----------------
output dataframes:
-----------------
Notes to self:
Some confusion previously caused by 2 sets of output dataframes (and csvs).
Existing (en_var_2.1) situation was this:
A) mutiple load profiles (e.g. iterations of virtual buildings):
   1) Study.op_perscenario
        for each scenario
       file created with 1 load profile per row. Contains energy & total $ for each resident & for en & retailer.
       Also total load,import, export, sc etc for whole building
   2) Study.op_mean and Study.op_std (THIS HAS NEVER BEEN USED - bug in en_var_2.1 had different_loads set to true)
        for whole study
       file created with 1 row per scenario, contains mean & std of selected parameters: $ for average customer & network & retailer
B) for single load profile per scenario (relevant for wwapi analysis):
    file created for study with one line per scenario, using specific data.
    Study.op_all
Study.op is for different_loads - assumes multiple loads for each scenario

Issues are:
A) means and std devs in same file is messy?
haven't really tried B)
Coding is messy and changes to output need to be made in several places and it gets mixed up.
Would be great to have a simplified code for this.

Structurally:
Study.__init__  establishes output_cols and cols
Scenario.cash_totals has all teh outputs for the scenario
BUT If different_loads, each scenario has different columns for individual data.
it it has to be kept like this. BUT can simplify column lists??
BUT old output data has _mean_by_n.csv which comes from different_loads

Individual customer data for virtual buildings is only useful if you keep the metadata, do loads of iterations and then look at how a particular cust does in diff scenarios,
BUT the vb's used for this have customer_id stripped out.

Summary output depends on the 3 types of studies:
NB different_loads is only used if also multiple_loads

-------------
resident_list
-------------
residents are strings ['1','2'....'cp']

-----------------
output dataframes:
-----------------
new arrangement:
Scenario.calcFinancials(en)
 - calculates cashflows and other parameters for each network / load profile
 - creates df Scenario.results with one row per network / load profile (ie single row if not multiple_loads)

Scenario.logScenarioData
 - saves Scenario.results as a csv in \scenarios
 - copies or averages scenario data to one row of Study.op
 - Study.op has less columns if different_loads

Study.logStudyData
- saves Study.op as .csv
- creates summary df and saves as csv (#TODO)

en_output.en_output(Study)
function in external module that produces summary csv files and charts

---------------------------------------------------
Output requirements from APSRC and EnergyCon Papers
---------------------------------------------------

APSRC
-----
Input Files: sc_all2 or as_all3 ?
vb's for all sites
max PV
fixed tariffs

Output Type:
Bar Chart: Total EN ($/unit) vs Site and Arrangement X


EnergyCon
---------

Input Files: envb_6r (full pv) and envb_6s (reduced pv)
vb's for site G only: 
combine these into study_energycon

Output Types:
Scatter plot of % Customer Saving vs SC Metric
Bar Chart: Total EN ($ per unit) vs tariff and PV/years X
Table: Distribution of benefits tenant / landlord / OO vs tariff scenarios


en_output module:
 has class-wide variables (data, parameters, etc)
 - use __init__ to pass it a project (from within en_3.py or externally) and it sets up paths, loads results and scenario files


Issues in energyCON o/p:
1) When no PV, gaps in total en cost - proably due to pv capex?. 
Issue with a_term and a_rate missing from study_ csv. but still used in calc
Made pv capex repayment calc conditional - FIXED

2) total cp$ is zero??
---- a long story:


---------------------------------------
Clarify relationship between net and cp
---------------------------------------
net includes all residents and cp in all arrangements. In this sense, it is the building.


    arrangement		net payments			cp payments	network_receipts_from_residents		retailer receipts
    -----------		------------			-----------	-------------------------------		-----------------
	bau		for cp, net = strata		zero		zero					sum of resident payments (inc cp)
	cp_only		for cp, net = strata		zero		zero					sum of resident payments (inc cp)
	btm		for cp, net = strata		zero		zero					sum of resident payments (inc cp)
	en		for EN, net = ENO / strata	zero		sum of resident payments 		EN payment

Suggestion to improve the logic:
	Stop making cp payments zero
	For bau, cp_only, btm, make net payments zero . net is not the strata strata still pays cp bill
	For en arrangement, net payments are ENO payments, cp still makes a payment BUT if ENO = strata, at ZERO TARIFF, so payment is ZERO 
							if ENO != strata, cp tariff maybe non zero, and 'cp' is the strata

	Rename net as ENO. In btm, bau, cp only scenarios, ENO is virtual.Makes no payments.
			   In en scenarios, it is the eno

New approach:

    arrangement		net payments			cp payments	network_receipts_from_residents		retailer receipts
    -----------		------------			-----------	-------------------------------		-----------------
	bau		zero				for cp load	zero					sum of resident payments (inc cp)
	cp_only		zero				for cp load	zero					sum of resident payments (inc cp)
	btm		zero				for cp load	zero					sum of resident payments (inc cp)
	en		for EN, net = ENO / strata	zero		sum of resident payments 		EN payment



Change started 12:18 on 13/3/18 en_3.1

Pay special attenation to households vs resident_list
QUESTION: In non-en scenarios, Does cp pay en and en pay retailer OR does cp pay retailer direct? CP PAYS RETAILER
	 in cp_only and btm, does cp have pv or does the en have pv? CP HAS PV GENERATION

BIG INPUT CHANGE: For NON-EN scenarios, parent tariff = TIDNULL, cp tariff is whatever cp is paying 
Change these in energyCON and APSRC study files. DONE

In non-en scenarios, ENO still has inports and exports that are cumulative, but tariffs are zero.
So ENO acts as ENO from energy perspective, but does not engage in financial transactions.
Energy <-> building. Cash <-> operator

New fn network.calcEnergyMetrics
Total import, export etc is calculated per  load_profile (network), not per scenario

N.B EnergyCON pbar plot: net en$ costs / unit are after en capex repayments and en opex. For the paper, they were before these costs.
Now capecx repayyments and opex are logged to results .csv and used to cal op for plot
Whereas total_building_costs (used for ASPRC bar chart) exclude en costs, so en's look very cheap. All to cock
Now sorted I think.

Except: APSRC en total costs are higher now than previously.
en_capex settings:
previously: capex was null or cp5 (2000+400n), 250, 12yrs, 6%)
now: capex is capex_6: (50000 + 400n),	250, 12 yrs, 6%. Should be capex_5
rerun. finally fu**ing sorted
