# morePVs Copyright (C) 2018 Mike B Roberts
# multi-occupancy residential electricity with PV and storage model
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version. # This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details. You should have received a copy of the GNU General Public License along with this program. If not,
# see <http://www.gnu.org/licenses/>.
# Contact: m.roberts@unsw.edu.au

# IMPORT Modules
import numpy as np
import sys
import logging
import sys
import os
import pdb, traceback
import pandas as pd
import en_utilities as um
import threading
import concurrent.futures
import datetime as dt

#from en import morePVs_output as opm

# Classes
class Timeseries():
    """DateTimeIndex & related parameters used throughout."""

    def __init__(self,
                 load
                 ):
        self.timeseries = load.index
        self.num_steps = len(self.timeseries)
        self.interval = \
                pd.to_timedelta(
                pd.tseries.frequencies.to_offset(
                pd.infer_freq(self.timeseries)
                )).total_seconds()
        self.num_days = int(self.num_steps * self.interval / (24*60*60))
        # Set up weekdays and weekends
        self.days = {
            'day': self.timeseries[self.timeseries.weekday.isin([0, 1, 2, 3, 4])],
            'end': self.timeseries[self.timeseries.weekday.isin([5, 6])],
            'both': self.timeseries}

class TariffData():
    """Reference resource with time-specific price data for multiple tariffs"""

    def __init__(
            self,
            tariff_lookup_path,
            reference_path):
        """Initialise tariff look-up table."""
        self.reference_path = reference_path
        self.saved_tariff_path = os.path.join(self.reference_path, 'saved_tariffs')
        if not os.path.exists(self.saved_tariff_path):
            os.makedirs(self.saved_tariff_path)
        # read csv of tariff parameters
        self.lookup = pd.read_csv(tariff_lookup_path, index_col=[0])
        self.all_tariffs = self.lookup.index  # list of all tariff ids
        # set up dfs for static import and export tariffs
        self.static_imports = pd.DataFrame(index=ts.timeseries)
        self.static_exports = pd.DataFrame(index=ts.timeseries)
        self.static_solar_imports = pd.DataFrame(index=ts.timeseries)
        self.block_quarterly_billing_start = 0  # timestep to start cumulative energy calc
        self.steps_in_block = 4380  # quarterly half-hour steps
        self.tou_rate_list = {'name_1': ['rate_1', 'start_1', 'end_1', 'week_1'],
                              'name_2': ['rate_2', 'start_2', 'end_2', 'week_2'],
                              'name_3': ['rate_3', 'start_3', 'end_3', 'week_3'],
                              'name_4': ['rate_4', 'start_4', 'end_4', 'week_4'],
                              'name_5': ['rate_5', 'start_5', 'end_5', 'week_5'],
                              'name_6': ['rate_6', 'start_6', 'end_6', 'week_6'],
                              'name_7': ['rate_7', 'start_7', 'end_7', 'week_7'],
                              'name_8': ['rate_8', 'start_8', 'end_8', 'week_8'],
                              }

    def generateStaticTariffs(self):
        """ Creates time-based rates for all load-independent tariffs."""
        for tid in self.all_tariffs:
            # apply discounts to all tariffs:
            # -------------------------------
            if not np.isnan(self.lookup.loc[tid, 'discount']):
                discount = self.lookup.loc[tid, 'discount']
                rates = [c for c in self.lookup.columns if 'rate' in c and not 'fit' in c]
                valid_rates = [c for c in rates if not np.isnan(self.lookup.loc[tid, c])]
                self.lookup.loc[tid, valid_rates] = self.lookup.loc[tid, valid_rates] * (100 - discount) / 100
            # Allocate Flat rate and Zero Tariffs
            # -----------------------------------:
            if self.lookup.loc[tid, 'tariff_type'] == 'Zero_Rate':
                self.static_imports[tid] = 0
            elif 'Flat_Rate' in self.lookup.loc[tid, 'tariff_type']:
                self.static_imports[tid] = self.lookup.loc[tid, 'flat_rate']
            # Allocate TOU tariffs:
            # --------------------
            # including residual (non-solar) rates for Solar_Block_TOU
            elif 'TOU' in self.lookup.loc[tid, 'tariff_type'] or 'Solar_Block' in self.lookup.loc[tid, 'tariff_type'] :
                # calculate timeseries TOU tariff based on up to 8 periods (n=1 to 8)
                # volumetric tariff is rate_n, between times start_n and end_n
                # week_n is 'day' for week, 'end' for weekend, 'both' for both
                # NB times stored in csv in form 'h:mm'. Midnight saved as 23:59
                for name, parameter in self.tou_rate_list.items():
                    if not pd.isnull(self.lookup.loc[tid, parameter[1]]): # parameter[1] is rate_

                        if self.lookup.loc[tid, parameter[1]] == '0:00':  # start_
                            period = \
                                    ts.days[self.lookup.loc[tid, parameter[3]]][ # week_
                                    (ts.days[self.lookup.loc[tid, parameter[3]]].time >= pd.Timestamp( # week_
                                        self.lookup.loc[tid,  parameter[1]]).time()) # start_
                                    & (ts.days[self.lookup.loc[tid, parameter[3]]].time <= pd.Timestamp( # week_
                                        self.lookup.loc[tid, parameter[2]]).time()) # end_
                                    ]
                        else:
                            period = \
                                    ts.days[self.lookup.loc[tid, parameter[3]]][ # week_
                                    (ts.days[self.lookup.loc[tid, parameter[3]]].time > pd.Timestamp( # week_
                                        self.lookup.loc[tid, parameter[1]]).time()) # start_
                                    & (ts.days[self.lookup.loc[tid, parameter[3]]].time <= pd.Timestamp( # week_
                                        self.lookup.loc[tid, parameter[2]]).time()) #end_
                                    ]
                        if not any(s in name for s in ['solar','Solar']):
                            # Store solar rate and period separately
                            # For non-solar periods and rates only:
                            self.static_imports.loc[period, tid] = self.lookup.loc[tid, parameter[0]] # rate_
                        else: # Solar (local) periods and rates only:
                            self.static_solar_imports.loc[period, tid] = self.lookup.loc[tid, parameter[0]]  # rate_
                    pass
            # TODO: rejig this section to allow tariff periods bridging midnight \
            # (use method used for battery charge & discharge tariffs) and also change tariff_lookup.csv
            # todo: create timeseries for FiT Tariffs in the same way
            # currently only zero or flat rate FiTs)
            if self.lookup.loc[tid, 'fit_type'] == 'Zero_Rate':
                self.static_exports[tid] = 0
            elif self.lookup.loc[tid, 'fit_type'] == 'Flat_Rate':
                self.static_exports[tid] = self.lookup.loc[tid, 'fit_flat_rate']
        # Save tariffs as csvs

        import_name = os.path.join(self.saved_tariff_path, 'static_import_tariffs.csv')
        solar_name = os.path.join(self.saved_tariff_path, 'static_solar_import_tariffs.csv')
        export_name = os.path.join(self.saved_tariff_path, 'static_export_tariffs.csv')
        um.df_to_csv(self.static_imports, import_name)
        um.df_to_csv(self.static_solar_imports, solar_name)
        um.df_to_csv(self.static_exports, export_name)


class Tariff():
    def __init__(self,
                 tariff_id,
                 scenario):
        """Create time-based rates for single specific tariff."""

        # ------------------------------
        # Export Tariff and Fixed Charge
        # ------------------------------
        self.export_tariff = (scenario.static_exports[tariff_id]).values  # NB assumes FiTs are fixed
        self.fixed_charge = scenario.lookup.loc[tariff_id, 'daily_fixed_rate']
        # Add in Metering Service Charge for network tariff:
        if scenario.lookup.loc[tariff_id, 'rorn'] == 'network':
            self.fixed_charge += \
                scenario.lookup.loc[tariff_id, 'metering_sc_non_cap'] + \
                scenario.lookup.loc[tariff_id, 'metering_sc_cap']

        # -------------
        # Demand Tariff
        # -------------
        if tariff_id in scenario.demand_list:
            self.is_demand = True
            self.demand_type = scenario.lookup.loc[tariff_id, 'demand_type']
            # Demand period is weekday or weekend between demand_start and demand_end:
            self.demand_period = ts.days[
                scenario.lookup.loc[tariff_id, 'demand_week']][
                (ts.days[scenario.lookup.loc[tariff_id, 'demand_week']
                 ].time > pd.Timestamp(
                    scenario.lookup.loc[tariff_id, 'demand_start']).time())
                & (ts.days[scenario.lookup.loc[tariff_id, 'demand_week']
                   ].time <= pd.Timestamp(
                    study.tariff_data.lookup.loc[tariff_id, 'demand_end']).time())
                ]
            s = pd.Series(0, index=ts.timeseries)
            s[self.demand_period] = 1
            self.demand_period_array = np.array(s)
            self.assumed_pf = 1.0  ##   For kVA demand charges, What is good assumption for this????
            self.demand_tariff = scenario.lookup.loc[tariff_id, 'demand_tariff']
        else:
            self.is_demand = False
        # ------------------------------------------------------
        # Solar tariff periods and rates (block or instantaneous)
        # ------------------------------------------------------
        if tariff_id in scenario.solar_inst_list:
            self.is_solar_inst = True
        else:
            self.is_solar_inst = False

        # Get solar tariff data:
        if tariff_id in scenario.solar_list:
            for name, parameter in study.tariff_data.tou_rate_list.items():
                if any(s in name for s in ['solar','Solar']):
                    self.solar_period = \
                        ts.days[scenario.lookup.loc[tariff_id, parameter[3]]][  # week_
                            (ts.days[scenario.lookup.loc[tariff_id, parameter[3]]].time > pd.Timestamp(  # week_
                                scenario.lookup.loc[tariff_id, parameter[1]]).time())  # start_
                            & (ts.days[scenario.lookup.loc[tariff_id, parameter[3]]].time <= pd.Timestamp(  # week_
                                scenario.lookup.loc[tariff_id, parameter[2]]).time())  # end_
                            ]
                    self.solar_rate = scenario.lookup.loc[tariff_id, parameter[0]]  # rate_
                    self.solar_cp_allocation = scenario.lookup.loc[tariff_id, 'solar_cp_allocation'].fillna(0) # % of total solar generation allocated to cp
            self.solar_import_tariff = (scenario.static_solar_imports[tariff_id]).values
        else:
            self.solar_import_tariff = np.zeros(ts.num_steps)
        # -----------------------------
        # All volumetric import tariffs
        # -----------------------------
        # initialise to zero if dynamically calculated, e.g block tariff,
        # otherwise copy from scenario
        if tariff_id not in scenario.dynamic_list:
            self.import_tariff = (scenario.static_imports[tariff_id]).values
        else:
            self.import_tariff = np.zeros(ts.num_steps)


    def calcDynamicTariff(self,
                          tariff_id,
                          scenario,
                          step,
                          customer_load):
        """Dynamically calculate tariffs by timestep according to status (eg cumulative load for block tariffs)."""
        if tariff_id in scenario.dynamic_list:
            if scenario.lookup.loc[tariff_id, 'tariff_type'] == 'Block_Quarterly':
                # Block Quarterly tariff has fixed load tariff blocks per quarter
                self.steps_since_reset = np.mod((step - scenario.block_quarterly_billing_start),
                                                scenario.steps_in_block)
                self.cumulative_energy = customer_load[step - self.steps_since_reset:step + 1].sum()
                if self.cumulative_energy <= scenario.lookup.loc[tariff_id, 'high_1']:
                    self.import_tariff[step] = scenario.lookup.loc[tariff_id, 'block_rate_1']
                elif self.cumulative_energy > scenario.lookup.loc[tariff_id, 'high_1'] \
                        and self.cumulative_energy <= scenario.lookup.loc[tariff_id, 'high_2']:
                    self.import_tariff[step] = scenario.lookup.loc[tariff_id, 'block_rate_2']
                elif self.cumulative_energy > scenario.lookup.loc[tariff_id, 'high_2']:
                    self.import_tariff[step] = scenario.lookup.loc[tariff_id, 'block_rate_3']
            else:
                logging.info("*****************Dynamic Tariff %s of unknown Tariff type", tariff_id)

class Battery():
    # adapted from script by Luke Marshall
    def __init__(self, scenario, battery_id, battery_strategy):
        self.battery_id = battery_id
        self.scenario = scenario
        # Load battery parameters from battery lookup
        # -------------------------------------------
        self.capacity_kWh = study.battery_lookup.loc[battery_id, 'capacity_kWh']
        self.charge_kW = study.battery_lookup.loc[battery_id, 'charge_kW']
        self.efficiency_cycle = study.battery_lookup.loc[battery_id, 'efficiency_cycle']
        self.maxDOD = study.battery_lookup.loc[battery_id, 'maxDOD']
        self.maxSOC = study.battery_lookup.loc[battery_id, 'maxSOC']
        self.max_cycles = study.battery_lookup.loc[battery_id,'max_cycles']
        self.battery_cost = study.battery_lookup.loc[battery_id, 'battery_cost']
        self.battery_inv_cost = study.battery_lookup.loc[battery_id, 'battery_inv_cost']
        self.life_bat_inv = scenario.a_term if np.isnan(study.battery_lookup.loc[battery_id, 'life_bat_inv'])\
                                         else study.battery_lookup.loc[battery_id, 'life_bat_inv']

        # Use default values if missing:
        # ------------------------------
        if pd.isnull(self.charge_kW):
            self.charge_kW = self.capacity_kWh * 0.5
        if pd.isnull(self.maxDOD):
            self.maxDOD = 0.8
        if pd.isnull(self.efficiency_cycle):
            self.efficiency_cycle = 0.95
        if pd.isnull(self.max_cycles):
            self.max_cycles = 2000
        # Set up restricted discharge period and additional charge period
        # ---------------------------------------------------------------
        discharge_start1 = study.battery_strategies.loc[battery_strategy, 'discharge_start1']
        discharge_end1 = study.battery_strategies.loc[battery_strategy, 'discharge_end1']
        discharge_day1 = study.battery_strategies.loc[battery_strategy, 'discharge_day1']
        discharge_start2 = study.battery_strategies.loc[battery_strategy, 'discharge_start2']
        discharge_end2 = study.battery_strategies.loc[battery_strategy, 'discharge_end2']
        discharge_day2 = study.battery_strategies.loc[battery_strategy, 'discharge_day2']
        charge_start = study.battery_strategies.loc[battery_strategy, 'charge_start']
        charge_end = study.battery_strategies.loc[battery_strategy, 'charge_end']
        charge_day = study.battery_strategies.loc[battery_strategy, 'charge_day']
        # Calculate discharge period(s):
        # -----------------------------
        if pd.isnull(discharge_start1):
            discharge_period1 = ts.timeseries
        elif pd.Timestamp(discharge_start1) > pd.Timestamp(discharge_end1):
            discharge_period1 = (ts.days[discharge_day1][(ts.days[discharge_day1].time > pd.Timestamp(discharge_start1).time()) & (
                        ts.days[discharge_day1].time <= pd.Timestamp('23:59').time())].append(
                ts.days[discharge_day1][(ts.days[discharge_day1].time >= pd.Timestamp('0:00').time()) & (
                            ts.days[discharge_day1].time <= pd.Timestamp(discharge_end1).time())])).sort_values()
        else:
            discharge_period1 = \
                ts.days[discharge_day1][(ts.days[discharge_day1].time > pd.Timestamp(discharge_start1).time())
                                       & (ts.days[discharge_day1].time <= pd.Timestamp(discharge_end1).time())]
        if pd.isnull(discharge_start2):
            discharge_period2 = pd.DatetimeIndex([])
        elif pd.Timestamp(discharge_start2) > pd.Timestamp(discharge_end2):
            discharge_period2 = (
            ts.days[discharge_day2][(ts.days[discharge_day2].time > pd.Timestamp(discharge_start2).time()) & (
                    ts.days[discharge_day2].time <= pd.Timestamp('23:59').time())].append(
                ts.days[discharge_day2][(ts.days[discharge_day2].time >= pd.Timestamp('0:00').time()) & (
                        ts.days[discharge_day2].time <= pd.Timestamp(discharge_end2).time())])).sort_values()
        else:
            discharge_period2 = \
                ts.days[discharge_day2][(ts.days[discharge_day2].time > pd.Timestamp(discharge_start2).time())
                                        & (ts.days[discharge_day2].time <= pd.Timestamp(discharge_end2).time())]
        self.discharge_period = discharge_period1.join(discharge_period2, how='outer')

        # Calculate additional charging period:
        # -------------------------------------
        if pd.isnull(charge_start):
            self.charge_period = pd.DatetimeIndex([])
        elif pd.Timestamp(charge_start) > pd.Timestamp(charge_end):
            self.charge_period = (ts.days[charge_day][(ts.days[charge_day].time > pd.Timestamp(charge_start).time()) & (
                        ts.days[charge_day].time <= pd.Timestamp('23:59').time())].append(
                ts.days[charge_day][(ts.days[charge_day].time >= pd.Timestamp('0:00').time()) & (
                            ts.days[charge_day].time <= pd.Timestamp(charge_end).time())])).sort_values()
        else:
            self.charge_period = \
                ts.days[charge_day][(ts.days[charge_day].time > pd.Timestamp(charge_start).time())
                                       & (ts.days[charge_day].time <= pd.Timestamp(charge_end).time())]
        # Initialise battery variables
        # ----------------------------
        self.charge_level_kWh = 0.0
        self.number_cycles = 0
        self.max_timestep_discharge = self.charge_kW * ts.interval / 3600
        self.max_timestep_charge = self.charge_kW * ts.interval / 3600
        # Initialise SOC log
        # ------------------
        self.SOC_log = np.zeros(ts.num_steps)

    def charge(self, desired_charge):
        amount_to_charge = min((self.capacity_kWh * self.maxSOC - self.charge_level_kWh)
                               / self.efficiency_cycle, desired_charge)
        self.charge_level_kWh += amount_to_charge*self.efficiency_cycle
        return desired_charge - amount_to_charge  # returns unstored portion of energy

    def discharge(self, desired_discharge):
        if self.charge_level_kWh > self.capacity_kWh * (1 - self.maxDOD):
            amount_to_discharge = min(desired_discharge,
                                  self.charge_level_kWh - self.capacity_kWh * (1 - self.maxDOD),
                                  self.max_timestep_discharge)
        else:
            amount_to_discharge =0
        self.charge_level_kWh -= amount_to_discharge
        self.number_cycles += amount_to_discharge / self.capacity_kWh
        return amount_to_discharge  # returns delivered energy

    def calcBatCapex(self):
        # Battery capex includes inverter replacement if amortization period > inverter lifetime
        if self.life_bat_inv > self.scenario.a_term:
            bat_inv_capex = (int((self.life_bat_inv / self.scenario.a_term))+1) * self.battery_inv_cost
        else:
            bat_inv_capex = self.battery_inv_cost
        # Battery capex includes battery replacement if it exceeds max_cycles in amortization period
        if self.number_cycles > self.max_cycles:
            bat_capex = (int(self.number_cycles / self.max_cycles)+1) * self.battery_cost
        else:
            bat_capex = self.battery_cost
        tot_capex = bat_inv_capex + bat_capex
        return tot_capex

    def dispatch(self, available_kWh, step):
        """Determines charge and discharge of battery at timestep."""

        # -------------------------------
        # Make battery control decisions:
        # -------------------------------
        # 1) Use excess PV to charge
        # --------------------------
        if available_kWh > 0:
            available_kWh = \
            self.charge(available_kWh)
        # 2) Discharge if needed to meet load, within discharge period
        # ------------------------------------------------------------
        elif available_kWh < 0 and ts.timeseries[step] in self.discharge_period:
            available_kWh += \
                self.discharge(-available_kWh)
        # 3) Charge from grid in additional charge period:
        # ------------------------------------------------
        elif available_kWh <= 0 and ts.timeseries[step] in self.charge_period:
            available_kWh -= (self.max_timestep_charge -
                                 self.charge(self.max_timestep_charge))
        # TODO 4) Dispatch battery to address peak demand ....(later)

        # For monitoring purposes, log battery SOC:
        # -----------------------------------------
        self.SOC_log[step] = self.charge_level_kWh / self.capacity_kWh * 100
        return available_kWh


class Customer():
    """Can be resident, strata body, or ENO representing aggregation of residents."""

    def __init__(self,
                 name,  # string
                 ):
        self.name = name
        self.tariff_data = study.tariff_data
        self.en_capex_repayment = 0
        self.en_opex = 0
        self.bat_capex_repayment = 0

    def initialiseCustomerLoad(self,
                               customer_load):  # as 1-d np.array
        """Set customer load, energy flows and cashflows to zero."""
        self.load = customer_load
        self.exports = np.zeros(ts.num_steps)
        self.imports = np.zeros(ts.num_steps)
        self.local_exports = np.zeros(ts.num_steps)  # not used, available for local trading
        self.local_imports = np.zeros(ts.num_steps)  # used for import of local generation
        self.flows = np.zeros(ts.num_steps)
        self.cashflows = np.zeros(ts.num_steps)

    def initialiseCustomerTariff(self,
                                 customer_tariff_id,  # string
                                 scenario):
        self.tariff_id = customer_tariff_id
        self.scenario = scenario
        self.tariff = Tariff(
                            tariff_id=self.tariff_id,
                            scenario=scenario)

    def initialiseCustomerPv(self, pv_generation):  # 1-D array
        self.generation = pv_generation

    def calcStaticEnergyFlows(self):
        """Calculate Customer imports and exports for whole time period"""
        self.flows = self.generation - self.load
        self.exports = self.flows.clip(0)
        self.imports = (-1 * self.flows).clip(0)
        self.local_imports = np.minimum(self.imports, self.local_quota) # for use of local generation

    def calcDynamicEnergyFlows(self,step):
        """Calculate Customer imports and exports for single timestep"""
        # -------------------------------------------------------------------------------
        # Calculate energy flow without battery, then modify by calling battery.dispatch:
        # -------------------------------------------------------------------------------
        self.flows[step] = self.generation[step] - self.load[step]
        if self.has_battery:
            self.flows[step] = self.battery.dispatch(available_kWh=self.flows[step], step=step)
        self.exports[step] = self.flows[step].clip(0)
        self.imports[step] = (-1 * self.flows[step]).clip(0)
        #TODO: @@@ Sort this local quota - might be OK
        self.local_imports[step] = np.minimum(self.imports[step], self.local_quota[step])  # for use of local generation

    def calcCustomerTariff (self, step):
        """Calculates import rates for timestep for dynamic (eg block) tariff."""
        # For block tariffs, go calculate rate for timestep:
        # --------------------------------------------------
        self.tariff.calcDynamicTariff(
                                      tariff_id=self.tariff_id,
                                      scenario=self.scenario,
                                      step=step,
                                      customer_load=self.imports
                                      )
        # For solar block daily tariff, calc kWh local import / solar allocation
        # ----------------------------------------------------------------------
        if self.scenario.lookup.loc[self.tariff_id, 'tariff_type'] == 'Solar_Block_Daily':
            self.tariff.steps_since_reset = np.mod((step - self.scenario.block_quarterly_billing_start),
                                            self.tariff.steps_in_day)
            # Cumulative Energy for this day:
            if self.cumulative_energy.all():
                self.prev_cum_energy = self.cumulative_energy
            else:
                self.prev_cum_energy= np.zeros(ts.num_steps)
            self.cumulative_energy = self.imports[step - self.steps_since_reset:step + 1].sum()
            # Allocate local_import depending on cumulative energy relative to quota:
            if self.cumulative_energy <= self.daily_local_quota:
                self.local_imports[step] = self.imports[step]
            elif self.prev_cum_energy < self.daily_local_quota \
                    and self.cumulative_energy > self.daily_local_quota:
                self.local_imports[step] = self.imports[step] - self.daily_local_quota / self.steps_in_day
            else:
                self.local_imports[step] = self.daily_local_quota / self.steps_in_day


    def calcDemandCharge(self):
        if self.tariff.is_demand:
            max_demand = np.multiply(self.imports,self.tariff.demand_period_array).max()/2 # in kW
            self.demand_charge = max_demand * self.tariff.demand_tariff * ts.num_days
            # Use nominal pf to convert to kVA?
            if self.tariff.demand_type == 'kVA':
                self.demand_charge = self.demand_charge / self.tariff.assumed_pf
        else:
            self.demand_charge = 0

    def calcCashflow(self):
        """Calculate receipts and payments for customer.

        self.cashflows is net volumetric import & export charge,
        self.energy_bill is total elec bill, ic fixed charges
        self.total_payment includes opex & capex repayments"""
        self.cashflows = \
            np.multiply((self.imports - self.local_imports), self.tariff.import_tariff) \
            + np.multiply(self.local_imports, self.tariff.solar_import_tariff) \
            - np.multiply((self.exports - self.local_exports), self.tariff.export_tariff)
            # - np.multiply(self.local_exports, self.tariff.local_export_tariff) could be added for LET / P2P
        # These are all 1x17520 Arrays.
        # local_tariffs are for, e.g. `solar_rate` energy,
        # maybe extendable for p2p later
        self.energy_bill = self.cashflows.sum() + \
                           self.tariff.fixed_charge * ts.num_days + \
                           self.demand_charge
        if self.name == 'retailer':
            self.total_payment = self.energy_bill
        else:
            self.total_payment = self.energy_bill + \
                            (self.pv_capex_repayment + \
                             self.en_capex_repayment + \
                             self.en_opex +\
                             self.bat_capex_repayment) * 100 # capex, opex in $, energy in c (because tariffs in c/kWh)

    # def staticDemandResponse(self,shift_time,shift_pc):
    #     self.load= self.load * (100% - shift_pc) + shift(self.load,shift_time)  * shift_pc ???
    #     pass


class Network(Customer):
    """A group of customers (residents) with loads, flows, financials, and is itself an aggregated customer.

    In embedded network scenarios, this object is equivalent to the ENO, takes payments from residents,
    and pays the retailer. It may be the strata body (when resident 'cp' has null tariffs) or a retailer or ENO.
    In other scenarios, it has no meaning irw, just passes energy and $ between other players"""

    def __init__(self, scenario):
        self.resident_list = scenario.resident_list.copy() # all residents plus cp
        self.households = scenario.households.copy()  # just residents, not cp
        # (these may change later if different_loads)
        #initialise characteristics of the network as a customer:
        super().__init__('network')
        #  initialise the customers / members within the network
        # (includes residents and cp)
        self.resident = {c: Customer(name=c) for c in self.resident_list}
        self.retailer = Customer(name='retailer')

    def initialiseBuildingLoads(self,
                                load_name,  # file name only
                                scenario
                                ):
        """Initialise network for new load profiles."""
        # read load data
        # --------------
        self.load_name = load_name
        self.network_load = scenario.dict_load_profiles[load_name]
        # set eno load, cumulative load and generation to zero
        # ----------------------------------------------------
        self.initialiseCustomerLoad(np.zeros(ts.num_steps))
        self.cum_resident_imports = np.zeros(ts.num_steps)
        self.cum_resident_exports = np.zeros(ts.num_steps)
        # initialise residents' loads
        # ---------------------------
        for c in self.resident_list:
            self.resident[c].initialiseCustomerLoad(
                           customer_load=np.array(self.network_load[c])
                           .astype(np.float64))

        # Calculate total site load
        # --------------------------
        self.total_building_load = self.network_load.sum().sum()

        # Initialise cash totals
        # ----------------------
        self.receipts_from_residents = 0
        self.total_building_payment = 0
        self.energy_bill = 0

    def initialiseAllTariffs(self, scenario):
        # initialise parent meter tariff
        self.initialiseCustomerTariff(scenario.tariff_in_use['parent'],scenario)
        # initialise internal customer tariffs
        for c in self.resident_list:
            self.resident[c].initialiseCustomerTariff(scenario.tariff_in_use[c],scenario)
        # initialise retailer's network tariff
        self.retailer.initialiseCustomerTariff(scenario.dnsp_tariff, scenario)
        # copy tariff parameter(s) from scenario
        self.has_dynamic_tariff = scenario.has_dynamic_tariff


    def allocatePv(self, scenario, pv):
        """set up and allocate pv generation for this scenario."""

        # Also used to allocate pv capex costs for some scenarios
        # Copy profile from scenario and then allocate
        # Allocation happens here as the Customers are part of the Network
        self.pv_exists = scenario.pv_exists
        self.pv = pv.copy()

        # Set up pv dataframe for each scenario:
        # --------------------------------------
        if 'en' in scenario.arrangement:
            # rename single column in pv file if necessary
            # TODO This will change to allow distributed PV within EN
            if 'cp' not in self.pv.columns:
                self.pv.columns = ['cp']
        elif scenario.arrangement == 'cp_only':
            # no action required
            # rename single column in pv file if necessary
            if 'cp' not in self.pv.columns:
                self.pv.columns = ['cp']
        elif scenario.arrangement == 'btm_i':
            # For btm_i, if only single pv column, split equally between all units (NOT CP)
            if len(self.pv.columns) == 1:
                self.pv.columns = ['total']
                for r in scenario.households:
                    self.pv[r] = self.pv['total']/len(scenario.households)
                self.pv = self.pv.drop('total', axis=1)
        elif scenario.arrangement == 'btm_icp':
            # For btm_icp, if only single pv column, split % to cp according tp cp_ratio and split remainder equally between all units
            # If more than 1 column, leave as allocated
            if len(self.pv.columns) == 1:
                self.pv.columns = ['total']
                self.pv['cp'] = self.pv['total'] * (self.resident['cp'].load.sum() / self.total_building_load)
                for r in scenario.households:
                    self.pv[r] = (self.pv['total'] - self.pv['cp']) / len(scenario.households)
                self.pv = self.pv.drop('total', axis=1)
        elif scenario.arrangement == 'btm_s_c':
            # For btm_s_c, split pv between all residents INCLUDING CP according to INSTANTANEOUS load
            if len(self.pv.columns) != 1:
                logging.info('***************Exception!!! PV %s has more than one column for shared btm arrangement ', scenario.pvFile)
                sys.exit("PV file doesn't match btm_s_c arrangement")
            else:
                self.pv.columns = ['total']
                self.pv = self.network_load.div(self.network_load.sum(axis=1), axis=0).multiply(
                    self.pv.loc[:,'total'], axis=0)
        elif scenario.arrangement == 'btm_s_u':
            # For btm_s_u, split pv between all residents EXCLUDING CP according to INSTANTANEOUS  load
            if len(self.pv.columns) != 1:
                logging.info(
                    '***************Exception!!! PV %s has more than one column for shared btm arrangement ',
                    scenario.pvFile)
                sys.exit("PV file doesn't match btm_s_u arrangement")
            else:
                self.pv.columns = ['total']
                load_units_only = self.network_load.copy().drop('cp',axis=1)
                self.pv = load_units_only.div(load_units_only.sum(axis=1), axis=0).multiply(
                    self.pv.loc[:, 'total'], axis=0)

        # Create list of customers with PV:
        if not self.pv_exists:
            self.pv_customers = []
        else:
            self.pv_customers = [c for c in self.pv.columns if self.pv[c].sum() >0]
            # Add blank columns for all residents with no pv
            blank_columns = [x for x in self.resident_list if x not in self.pv.columns]
            self.pv = pd.concat([self.pv, pd.DataFrame(columns=blank_columns)]).fillna(0)

        # Initialise all residents with their allocated PV generation
        # -----------------------------------------------------------
        for c in self.resident_list:
            self.resident[c].initialiseCustomerPv(np.array(self.pv[c]).astype(np.float64))

    def initialiseDailySolarBlockQuotas(self, scenario):
        """For Solar Block Daily tariff, allocate block limits for all residents."""
        # Check that all residents have same solar_cp_allocation basis , otherwise raise an exception:
        allocation_list = list(set((self.resident[c].tariff.solar_cp_allocation for c in self.resident_list)))
        if len(allocation_list) > 1:
            sys.exit("Inconsistent cp allocation of local generation")
        else:
            solar_cp_allocation = allocation_list[0]
        # Calc daily quotas for cp and households:
        self.resident['cp'].daily_local_quota = self.pv.loc[
                                                    self.resident['cp'].solar_period, 'cp'] * solar_cp_allocation / 365
        for c in self.households:
            self.resident[c].daily_local_quota = self.pv.loc[self.resident[c].solar_period, 'cp'] * (
                        1 - solar_cp_allocation) / (365 * len(self.households))

    def initialiseSolarInstQuotas(self, scenario):
        # calculate local quotas for solar or LET tariffs
        # -----------------------------------------------
        # (NB Applies to EN arrangements only, so PV allocation is fixed and PV has already been initialised.)
        # This is for instantaneous solar tariff.
        self.local_quota = np.zeros(ts.num_steps)
        self.retailer.local_quota = np.zeros(ts.num_steps)
        if 'en' in scenario.arrangement:
            for c in self.resident_list:
                if self.resident[c].tariff.is_solar_inst:
                    self.resident[c].local_quota = np.where((self.pv['cp'] > self.resident['cp'].load),\
                                                            (self.pv['cp'] - self.resident['cp'].load) / len(
                                                            self.households), 0)
                else:
                    self.resident[c].local_quota =np.zeros(ts.num_steps)
        else:
            for c in self.resident_list:
                self.resident[c].local_quota = np.zeros(ts.num_steps)

    def initialiseAllBatteries(self, scenario):
        """Initialise central and individual batteries as required."""
        # Central Battery
        # ---------------
        self.has_central_battery = scenario.has_central_battery
        if self.has_central_battery:
            self.battery = Battery(scenario=scenario,
                                   battery_id=scenario.battery_id,
                                   battery_strategy=scenario.battery_strategy)

        # Individual Batteries
        # --------------------
        self.cum_ind_bat_charge = np.zeros(ts.num_steps)
        self.tot_ind_bat_capacity =0
        self.any_resident_has_battery = False
        if scenario.has_ind_batteries != 'none':
            for c in self.resident_list:
                bat_name = str(c) + '_battery_id'
                bat_strategy = str(c) + '_battery_strategy'
                if bat_name in scenario.parameters.index and bat_strategy in scenario.parameters.index:
                    if not pd.isnull(scenario.parameters[bat_name]) and \
                            not pd.isnull(scenario.parameters[bat_strategy]):
                        self.resident[c].battery = Battery(scenario=scenario,
                                                           battery_id=scenario.parameters[bat_name],
                                                           battery_strategy=scenario.parameters[bat_strategy])
                        self.resident[c].has_battery = True
                        self.any_resident_has_battery = True
                        scenario.has_ind_batteries = 'True'
                        self.tot_ind_bat_capacity += self.resident[c].battery.capacity_kWh
                    else:
                        self.resident[c].has_battery = False
                else:
                    self.resident[c].has_battery = False

    def calcBuildingStaticEnergyFlows(self):
        """Calculate all internal energy flows for all timesteps (no storage or dm)."""

        # Calculate flows for each resident and cumulative values for ENO
        for c in self.resident_list:
            self.resident[c].calcStaticEnergyFlows()
            # Cumulative load and generation are what the "ENO" presents to the retailer:
            self.cum_resident_imports += self.resident[c].imports
            self.cum_resident_exports += self.resident[c].exports
        # Calculate aggregate flows for ENO
        self.flows = self.cum_resident_exports - self.cum_resident_imports
        self.exports = self.flows.clip(0)
        self.imports = (-1 * self.flows).clip(0)

    def setupRetailerFlows(self):
        # NB retailer acts like a customer too, buying from DNSP
        # These are the load and generation that it presents to DNSP
        self.retailer.initialiseCustomerLoad(self.imports)
        self.retailer.initialiseCustomerPv(self.exports)

    def calcAllDemandCharges(self):
        """Calculates demand charges for ENO and for all residents."""
        self.calcDemandCharge()
        for c in self.resident_list:
            self.resident[c].calcDemandCharge()
        self.retailer.calcDemandCharge()

    def calcBuildingDynamicEnergyFlows(self, step):
        """Calculate all internal energy flows for SINGLE timesteps (with storage)."""

        # ---------------------------------------------------------------
        # Calculate flows for each resident and cumulative values for ENO
        # ---------------------------------------------------------------
        for c in self.resident_list:
            # Calc flows (inc battery dispatch) for each resident
            # ---------------------------------------------------
            self.resident[c].calcDynamicEnergyFlows(step)
            # Cumulative load and generation are what the "ENO" presents to the retailer:
            self.cum_resident_imports[step] += self.resident[c].imports[step]
            self.cum_resident_exports[step] += self.resident[c].exports[step]
            # For diagnostics, log cumulative charge state
            if self.resident[c].has_battery:
                self.cum_ind_bat_charge[step] += self.resident[c].battery.charge_level_kWh

        # ----------------------------------------------------------------------------------------
        # Calculate energy flow without central  battery, then modify by calling battery.dispatch:
        # ----------------------------------------------------------------------------------------
        self.flows[step] = self.cum_resident_exports[step] - self.cum_resident_imports[step]
        if self.has_central_battery:
            self.flows[step] = self.battery.dispatch(available_kWh=self.flows[step], step=step)
        # Calc imports and exports
        # ------------------------
        self.exports[step] = self.flows[step].clip(0)
        self.imports[step] = (-1 * self.flows[step]).clip(0)


    def calcDynamicTariffs(self,step):
        """Dynamic calcs of (eg block) tariffs by timestep for ENO and for all residents."""
        for c in self.resident_list:
            self.resident[c].calcCustomerTariff(step)
        self.calcCustomerTariff(step)


    def allocateAllCapex(self, scenario):
        """ Allocates capex repayments and opex to customers according to arrangement"""
        # For some arrangements, this depends on pv allocation, so must follow allocatePv call
        # Called once per load profile where capex is allocated according to load; once per scenario otherwise
        # Moved from start of iterations to end to incorporate battery lifecycle impacts
        # Initialise all to zero:
        self.en_opex = 0
        self.pv_capex_repayment = 0
        self.en_capex_repayment = 0
        self.bat_capex_repayment =0
        for c in self.resident_list:
            self.resident[c].pv_capex_repayment = 0
            self.resident[c].bat_capex_repayment = 0

        # Calculate capex costs for battery
        # ---------------------------------
        if self.has_central_battery:
            self.bat_capex = self.battery.calcBatCapex()
        else:
            self.bat_capex = 0
        if self.bat_capex > 0:
            self.bat_capex_repayment = -12 * np.pmt(rate=scenario.a_rate / 12,
                                                   nper=12 * scenario.a_term,
                                                   pv=self.bat_capex,
                                                   fv=0,
                                                   when='end')
        # Allocate capex & opex payments depending on network arrangements
        # ----------------------------------------------------------------
        if scenario.arrangement in ['en_strata', 'en', 'en_pv']:
            # For en, all capex & opex are borne by the ENO
            self.en_opex = scenario.en_opex
            self.pv_capex_repayment = scenario.pv_capex_repayment
            self.en_capex_repayment = scenario.en_capex_repayment
        elif scenario.arrangement =='cp_only':
            # pv capex allocated by customer 'cp' (ie strata)
            self.resident['cp'].pv_capex_repayment = scenario.pv_capex_repayment
        elif 'btm_i' in scenario.arrangement:
            # For btm_i apportion capex costs according to pv allocation
            for c in self.pv_customers:
                self.resident[c].pv_capex_repayment = self.pv[c].sum() / self.pv.sum().sum() * scenario.pv_capex_repayment
        elif 'btm_s_c' in scenario.arrangement:
            # For btm_s_c, apportion capex costs equally between units and cp.
            # (Not ideal - needs more sophisticated analysis of practical btm_s arrangements)
            for c in self.resident_list:
                self.resident[c].pv_capex_repayment = scenario.pv_capex_repayment / len(self.resident_list)
        elif 'btm_s_u' in scenario.arrangement:
            # For btm_s_u, apportion capex costs equally between units only
            # (Not ideal - needs more sophisticated analysis of practical btm_s arrangements)
            for c in self.households:
                self.resident[c].pv_capex_repayment =  scenario.pv_capex_repayment / len(self.households)

    def calcEnergyParameters(self, scenario):
        # ---------------------------------------------------------------
        # calculate total exports / imports & pvr, cpr & self consumption
        # ---------------------------------------------------------------
        if scenario.arrangement == 'bau' or scenario.arrangement == 'cp_only' or 'btm' in scenario.arrangement:
            # Building export is sum of customer exports
            # Building import is sum of customer imports
            self.total_building_export = 0
            self.total_import = 0
            for c in self.resident_list:
                self.total_building_export += self.resident[c].exports.sum()
                self.total_import += self.resident[c].imports.sum()
        else:
            # For en scenarios, import and exports are aggregated:
            self.total_building_export = self.exports.sum()
            self.total_import = self.imports.sum()
        self.pv_ratio = self.pv.sum().sum() / self.total_building_load * 100
        self.cp_ratio =self.resident['cp'].load.sum()/ self.total_building_load *100
        if scenario.pv_exists:
            self.self_consumption = 100 - (self.total_building_export / self.pv.sum().sum() * 100)
        else:
            self.self_consumption=0

    def logTimeseries(self,scenario):
        """Logs timeseries data for whole building to csv file."""

        timedata = pd.DataFrame(index=ts.timeseries)
        timedata['network_load'] = self.network_load.sum(axis=1)
        timedata['pv_generation'] = self.pv.sum(axis=1)
        timedata['grid_import'] = self.imports
        timedata['grid_export'] = self.exports
        if scenario.has_central_battery:
            timedata['battery_SOC'] = self.battery.SOC_log
            timedata['battery_charge_kWh'] = self.battery.SOC_log * self.battery.capacity_kWh / 100
        if scenario.has_ind_batteries == 'True':
            timedata['ind_battery_SOC'] = self.cum_ind_bat_charge / self.tot_ind_bat_capacity *100
        time_file = os.path.join(study.timeseries_path,
                                 self.scenario.label + '_' +
                                 self.load_name )
        um.df_to_csv(timedata, time_file)

class Scenario():
    """Contains a single set of input parameters, but may contain multiple load profiles."""
    def __init__(self, scenario_name):
        # ------------------------------
        # Set up key scenario parameters
        # ------------------------------
        self.name = scenario_name
        self.label = study.name + '_' + "{:03}".format(self.name)
        # Copy all scenario parameters to allow for threading:
        # with lock: REINSTATE lock if using Threads
        self.parameters = study.study_parameters.loc[self.name].copy()
        # --------------------------------------------
        # Set up network arrangement for this scenario
        # --------------------------------------------
        self.arrangement = self.parameters['arrangement']
        self.pv_exists = not (self.parameters.isnull()['pv_filename']) and study.pv_exists
        if self.arrangement in ['btm_s_c', 'btm_s_u','btm_icp']:
            self.pv_allocation = 'load_dependent'
        else:
            self.pv_allocation = 'fixed'

        # -----------------------------------------------------------------
        # Set up load profiles, resident list & results df for the scenario
        # -----------------------------------------------------------------
        # if same load profile(s) used for all scenarios, this comes from Study
        # If different loads used, get resident list from first load
        self.load_folder = self.parameters['load_folder']
        if study.different_loads:
            load_path = os.path.join(study.base_path, 'load_profiles', self.load_folder)
            self.load_list = os.listdir(load_path)

            # read all load profiles into dict of dfs
            # ---------------------------------------
            self.dict_load_profiles ={}
            for load_name in self.load_list:
                loadFile = os.path.join(load_path,load_name)
                temp_load = pd.read_csv(loadFile,
                                        parse_dates=['timestamp'],
                                        dayfirst=True)
                temp_load = temp_load.set_index('timestamp')
                if not 'cp' in temp_load.columns:
                    temp_load['cp'] = 0
                self.dict_load_profiles[load_name] = temp_load.copy()
            # use first load profile in list to establish list of residents:
            # --------------------------------------------------------------
            self.resident_list = list(self.dict_load_profiles[self.load_list[0]].columns.values)  # list of potential child meters - residents + cp

        else:
            # Loads are the same for every scenario and have been read already:
            # -----------------------------------------------------------------
            self.dict_load_profiles = study.dict_load_profiles.copy()
            self.resident_list = study.resident_list.copy()  # includes cp
            self.load_list = study.load_list.copy()

        self.households = [c for c in self.resident_list if c != 'cp']
        self.results = pd.DataFrame()

        # ---------------------------------
        # read PV profile for this scenario
        # ---------------------------------
        if not self.pv_exists:
            self.pv = pd.DataFrame(index=ts.timeseries, columns=self.resident_list).fillna(0)
        else:
            self.pvFile = os.path.join(study.pv_path,
                                  self.parameters['pv_filename'])
            if not os.path.exists(self.pvFile):
                logging.info('***************Exception!!! PV file %s NOT FOUND', self.pvFile)
                sys.exit("PV file missing")
            else:
                # Load pv generation data:
                # -----------------------
                self.pv = pd.read_csv(self.pvFile, parse_dates=['timestamp'], dayfirst=True)
                self.pv.set_index('timestamp', inplace=True)
                if not self.pv.index.equals(ts.timeseries):
                    logging.info('***************Exception!!! PV %s index does not align with load ', self.pvFile)
                    sys.exit("PV has bad timeseries")
                # Scaleable PV has a 1kW gneration input file scaled to array size:
                self.pv_scaleable = ('pv_scaleable' in self.parameters.index) and \
                                    self.parameters['pv_scaleable']
                if self.pv_scaleable:
                    self.pv = self.pv * self.pv_kW_peak

        # ---------------------------------------
        # Set up tariffs for this scenario
        # ---------------------------------------
        # Customer tariffs can be individually allocated, or can be fixed for all residents
        # if 'all residents' is present in scenario csv, it trumps individual customer tariffs
        # and is copied across (except for cp):
        if 'all_residents' in self.parameters.index:
            if (self.parameters['all_residents'] == ''):
                logging.info('Missing tariff data for all_residents in study csv')
            else:  # read tariff for each customer
                for c in self.households:
                    # with lock: REINSTATE lock if using Threads
                    self.parameters[c] = self.parameters['all_residents']

        # Create list of tariffs used in this scenario
        # --------------------------------------------
        self.customers_with_tariffs = self.resident_list + ['parent']
        self.dnsp_tariff = self.parameters['network_tariff']
        self.tariff_in_use = self.parameters[self.customers_with_tariffs] # tariff ids for each customer
        self.tariff_short_list = self.tariff_in_use.tolist()  + [self.dnsp_tariff]  # list of tariffs in use
        self.tariff_short_list = list(set(self.tariff_short_list)) # drop duplicates
        #  Slice tariff lookup table for this scenario
        self.lookup = study.tariff_data.lookup.loc[self.tariff_short_list]
        self.dynamic_list = [t for t in self.tariff_short_list \
                if any(word in self.lookup.loc[t, 'tariff_type'] for word in ['Block','block','Dynamic','dynamic'])]
                # Currently only includes block, could also add demand tariffs
                # if needed - i.e. for demand tariffs on < 12 month period
        self.solar_list = [t for t in self.tariff_short_list \
                if any(word in self.lookup.loc[t, 'tariff_type'] for word in ['Solar','solar'])]
        solar_block_list = [t for t in self.solar_list \
                if any(word in self.lookup.loc[t, 'tariff_type'] for word in ['Block','block'])]
        self.solar_inst_list = [t for t in self.solar_list \
                           if any(word in self.lookup.loc[t, 'tariff_type'] for word in ['Inst', 'inst'])]
        self.demand_list = [t for t in self.tariff_short_list \
                if 'Demand' in self.lookup.loc[t, 'tariff_type']]
        self.has_demand_charges = len(self.demand_list) > 0
        self.has_dynamic_tariff = len(self.dynamic_list) > 0
        #  previously:(list(set(self.tariff_short_list).intersection(self.dynamic_list)))
        self.has_solar_block = len(solar_block_list) > 0
        self.has_solar_inst = len(self.solar_inst_list) > 0

        self.block_quarterly_billing_start = study.tariff_data.block_quarterly_billing_start
        self.steps_in_block = study.tariff_data.steps_in_block
        self.steps_in_day = 48 # used for daily block tariffs eg solar block
        #  Slice  static tariffs for this scenario
        # ----------------------------------------
        self.static_imports = study.tariff_data.static_imports[self.tariff_short_list]
        self.static_exports = study.tariff_data.static_exports[self.tariff_short_list]
        if len(self.solar_list) > 0:
            self.static_solar_imports = study.tariff_data.static_solar_imports[self.solar_list]

        # ------------------------------------
        # identify batteries for this scenario
        # ------------------------------------
        if 'battery_id' in self.parameters.index and 'battery_strategy' in self.parameters.index:
            self.battery_id = self.parameters['battery_id']
            self.battery_strategy = self.parameters['battery_strategy']
            self.has_central_battery = not pd.isnull(self.battery_id)
        else:
            self.has_central_battery = False

        # Possible individual batteries:
        if self.parameters.index.str.contains('_battery_id').any() \
                and self.parameters.index.str.contains('_battery_strategy').any():
            self.has_ind_batteries = 'maybe'
        else:
            self.has_ind_batteries = 'none'


        # --------------------------------------------------------
        # Set up annual capex & opex costs for en in this scenario
        # --------------------------------------------------------
        # Annual capex repayments for embedded network
        self.pc_cap_id = self.parameters['pv_cap_id']
        if 'en' in self.arrangement:
            self.en_cap_id = self.parameters['en_capex_id']
            self.en_capex = study.en_capex.loc[self.en_cap_id, 'site_capex'] + \
                (study.en_capex.loc[self.en_cap_id, 'unit_capex']  * \
                len(self.households))
        else:
            self.en_capex =0
        self.a_term = self.parameters['a_term']
        self.a_rate = self.parameters['a_rate']

        if self.en_capex>0:
            self.en_capex_repayment = -12 * np.pmt(rate=self.a_rate/12,
                                         nper=12 * self.a_term,
                                         pv=self.en_capex,
                                         fv=0,
                                         when='end')
        else:
            self.en_capex_repayment=0
        # Opex for embedded network:
        if 'en' in self.arrangement:
            self.en_opex = study.en_capex.loc[self.en_cap_id, 'site_opex'] + \
                          (study.en_capex.loc[self.en_cap_id, 'unit_opex'] * \
                           len(self.households))
        else:
            self.en_opex = 0
        # --------------------------------------------------------
        # Allocate annual capex repayments for pv in this scenario
        # --------------------------------------------------------
        if not self.pv_exists:
            self.pv_capex_repayment = 0
        else:
            # Calculate pv capex
            # ------------------
            # PV capex includes inverter replacement if amortization period > inverter lifetime
            self.pv_capex = study.pv_capex_table.loc[self.pc_cap_id, 'pv_capex'] + \
                            (int((study.pv_capex_table.loc[self.pc_cap_id, 'inverter_life'] / self.a_term)) * \
                             study.pv_capex_table.loc[self.pc_cap_id, 'inverter_cost'])
            #  Option to use standard 1kW PV output and scale
            #  with pv_capex and inverter cost given as $/kW
            if self.pv_scaleable:
                self.pv_kW_peak = self.parameters['pv_kW_peak']
                self.pv_capex = self.pv_capex * self.pv_kW_peak
            # Calculate annual repayments
            # ---------------------------
            if self.pv_capex>0:
                self.pv_capex_repayment = -12 * np.pmt(rate=self.a_rate/12,
                                                 nper=12 * self.a_term,
                                                 pv=self.pv_capex,
                                                 fv=0,
                                                 when='end')
            else:
                self.pv_capex_repayment=0

    def calcResults(self, network):
        """ Calculates results for specific network within scenario.

         Includes: cashflows for whole period  - for each resident
                   cashflows for network and retailer
                   total imports and exports,
                   self consumption and pv_ratio."""
        # This function and Customer.calcCashflow() are the heart of the finances
        # -------------------------------
        # Calculate cashflows for network
        # -------------------------------
        # Use network import and export which are summed from resident & cp import and export
        # (plus dynamic battery calcs)
        # to calculate external cashflows.
        # NB if non-en scenario, tariffs are zero, so cashflows =0
        network.calcCashflow()
        # ----------------------------------
        # Cashflows for individual residents
        # ----------------------------------
        for c in network.resident_list:
            network.resident[c].calcCashflow()
            network.receipts_from_residents = network.receipts_from_residents + network.resident[c].energy_bill
            network.total_building_payment = network.total_building_payment + network.resident[c].total_payment
        # For en, total_building_payment is sum of customer payments less ENO profit
        if 'en' in self.arrangement:
            # Sum of all resident (bills + cap/opex) plus eno total (bills plus cap/opex) less what residents pay to eno
            network.total_building_payment = network.total_building_payment + network.total_payment - network.receipts_from_residents
        # Calculate external retailer cashflows:
        network.retailer.calcCashflow()
        # -----------------
        # Retailer receipts
        # -----------------
        if self.arrangement == 'bau' or self.arrangement == 'cp_only' or 'btm' in self.arrangement :
            network.energy_bill = 0
            network.total_payment = 0
            network.retailer_receipt = network.receipts_from_residents.copy()
            network.receipts_from_residents = 0
        elif 'en' in self.arrangement:
            network.retailer_receipt = network.energy_bill.copy()
        else:
            print('************************Unknown network arrangement********************')
            logging.info('************************Unknown network arrangement********************')
        # --------------------------------------------------------
        # Collate all results for network in one row of results df
        # --------------------------------------------------------
        # includes c -> $ conversion
        result_list = [network.total_building_payment / 100,
                       network.receipts_from_residents / 100,
                       network.energy_bill / 100,
                       network.total_payment / 100,
                       (network.receipts_from_residents - network.total_payment) / 100,
                       network.retailer_receipt / 100,
                       network.retailer.energy_bill / 100,
                       network.total_building_load,
                       network.total_building_export,
                       network.total_import,
                       network.cp_ratio,
                       network.pv_ratio,
                       network.self_consumption] + \
                    [network.resident['cp'].energy_bill/100] + \
                    [network.resident[c].energy_bill/100 for c in network.resident_list if c != 'cp'] + \
                    [network.resident['cp'].total_payment/100] + \
                    [network.resident[c].total_payment/100 for c in network.resident_list if c != 'cp']

        result_labels = ['total$_building_costs',
                        'eno$_receipts_from_residents',
                        'eno$_energy_bill',
                        'eno$_total_payment',
                        'eno_net$',
                        'retailer_receipt$',
                        'NUOS_charges$',
                        'total_building_load',
                        'export_kWh',
                        'import_kWh',
                        'cp_ratio',
                        'pv_ratio',
                        'self-consumption'] +\
                        ['cust_bill_cp'] + \
                        ['cust_bill_' + '%03d' % int(r) for r in network.resident_list if r != 'cp']  + \
                        ['cust_total$_cp'] + \
                        ['cust_total$_' + '%03d' % int(r) for r in network.resident_list if r != 'cp']

        self.results = self.results.append(pd.Series(result_list,
                                                     index=result_labels,
                                                     name=network.load_name))


    def logScenarioData(self):
        """Saves a csv file for each scenario and logs a row of results to output df."""

        # ---------------------------------
        # Save all results for the scenario
        # ---------------------------------
        opScenarioFile = os.path.join(study.scenario_path, self.label + '.csv')
        um.df_to_csv(self.results, opScenarioFile)
        # create parameter lists
        cols = self.results.columns.tolist()

        # Scenario label and key parameters for scenario
        study.op.loc[self.name,'scenario_label'] = self.label
        study.op.loc[self.name,'arrangement'] = self.arrangement
        study.op.loc[self.name,'number_of_households'] = len(self.households)
        study.op.loc[self.name,'load_folder'] = self.load_folder

        # Scenario total capex and opex repayments
        # ----------------------------------------
        study.op.loc[self.name, 'en_opex'] = self.en_opex
        study.op.loc[self.name, 'en_capex_repayment'] = self.en_capex_repayment
        study.op.loc[self.name, 'pv_capex_repayment'] = self.pv_capex_repayment

        # ----------------------------------------------------------------
        # Customer payments averaged for all residents, all load profiles:
        # ----------------------------------------------------------------
        cust_bill_list = [c for c in cols if 'cust_bill_' in c and 'cp' not in c ]
        cust_total_list = [c for c in cols if 'cust_total$_' in c and 'cp' not in c ]
        study.op.loc[self.name,'average_hh_bill$'] = self.results[cust_bill_list].mean().mean()
        study.op.loc[self.name,'std_hh_bill$'] = self.results[cust_bill_list].values.std(ddof=1)
        study.op.loc[self.name,'average_hh_total$'] = self.results[cust_total_list].mean().mean()
        study.op.loc[self.name,'std_hh_total$'] = self.results[cust_total_list].values.std(ddof=1)
        # ----------------------------------------
        # Reduced data logging for different_loads
        # ----------------------------------------
        if study.different_loads:
        # Don't log individual customer $ if each scenario has different load profiles
        # (because each scenario may have different number of residents):
            cols = [c for c in cols if c not in (cust_bill_list + cust_total_list)] # .tolist()
        # -------------------------------------
        # Average results across multiple loads
        # -------------------------------------
        # For remaining parameters in results, average across multiple load profiles:
        mcols = [c + '_mean' for c in cols]
        stdcols = [c + '_std' for c in cols]
        for c in cols:
            i = cols.index(c)
            study.op.loc[self.name,mcols[i]]=self.results.loc[:,c].mean(axis=0)
            study.op.loc[self.name,stdcols[i]]=self.results.loc[:,c].std(axis=0)

class Study():
    """A set of different scenarios to be compared."""

    def __init__(self,
                 base_path,
                 project,
                 study_name
                 ):
        # --------------------------------
        # Set up paths and files for Study
        # --------------------------------
        # All input and output datafiles are located relative to base_path and base_path\project
        self.base_path = base_path
        self.name = study_name
        self.project_path = os.path.join(self.base_path,'studies',project)
        # reference files
        # ---------------
        self.reference_path = os.path.join(self.base_path, 'reference')
        self.input_path = os.path.join(self.project_path, 'inputs')
        tariff_name='tariff_lookup.csv'
        self.t_lookupFile = os.path.join(self.reference_path, tariff_name)
        capex_pv_name = 'capex_pv_lookup.csv'
        self.capexpv_file = os.path.join(self.reference_path, capex_pv_name)
        capex_en_name = 'capex_en_lookup.csv'
        self.capexen_file = os.path.join(self.reference_path, capex_en_name)
        battery_lookup_name = 'battery_lookup.csv'
        self.battery_file = os.path.join(self.reference_path, battery_lookup_name)
        battery_strategies_name= 'battery_control_strategies.csv'
        self.battery_strategies_file = os.path.join(self.reference_path, battery_strategies_name)
        # study file contains all scenarios
        # ---------------------------------
        study_filename = 'study_' + study_name + '.csv'
        study_file = os.path.join(self.input_path, study_filename)

        # --------------------
        # read study scenarios
        # --------------------
        self.study_parameters = pd.read_csv(study_file)
        self.study_parameters.set_index('scenario', inplace=True)
        self.scenario_list = [s for s in self.study_parameters.index if not pd.isnull(s)]
        # Read list of output requirements and strip from df
        if 'output_types' in self.study_parameters.columns:
            self.output_list = self.study_parameters['output_types'].dropna().tolist()
        else:
            self.output_list = []
        # -------------------
        # Set up output paths
        # -------------------
        self.output_path = os.path.join(self.project_path, 'outputs')
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        self.output_path = os.path.join(self.output_path, study_name)
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        self.scenario_path = os.path.join(self.output_path,'scenarios')
        if not os.path.exists(self.scenario_path):
            os.makedirs(self.scenario_path)
        if 'log_timeseries_csv' in self.output_list:
            self.log_timeseries = True
            self.timeseries_path = os.path.join(self.output_path, 'timeseries')
            if not os.path.exists(self.timeseries_path):
                os.makedirs(self.timeseries_path)
        else:
            self.log_timeseries = False

        # --------------
        #  Locate pv data
        # --------------
        self.pv_path = os.path.join(self.base_path, 'pv_profiles')
        if os.path.exists(self.pv_path):
            self.pv_list = os.listdir(self.pv_path)
            if len(self.pv_list) > 0:
               self.pv_exists = True
            else:
                self.pv_exists = False
                logging.info('************Missing PV Profile ***************')
                sys.exit("Missing PV data")
        else:
            self.pv_exists = False
            logging.info('************Missing PV Profile ***************')
            sys.exit("Missing PV data")
        # --------------------------------------
        #  read capex costs into reference tables
        # --------------------------------------
        self.en_capex = pd.read_csv(self.capexen_file,
                                    dtype={'site_capex': np.float64,
                                           'unit_capex': np.float64,
                                           'site_opex': np.float64,
                                           'unit_opex': np.float64,
                                           })
        self.en_capex.loc[:,['site_capex', 'unit_capex', 'site_opex', 'unit_opex']] \
            = self.en_capex.loc[:,['site_capex','unit_capex','site_opex','unit_opex']].fillna(0.0)
        self.en_capex = self.en_capex.set_index('en_capex_id')
        if self.pv_exists:
            self.pv_capex_table = pd.read_csv(self.capexpv_file,
                                              dtype = {'pv_capex' : np.float64,
                                                       'inverter_cost': np.float64,
                                                       'inverter_life' : np.float64,
                                                       })
            self.pv_capex_table = self.pv_capex_table.set_index('pv_cap_id')
            self.pv_capex_table.loc[:,['pv_capex', 'inverter_cost']] \
                    = self.pv_capex_table.loc[:,['pv_capex','inverter_cost']].fillna(0.0)
        # ----------------------------------
        # read battery data into lookup file
        # ----------------------------------
        self.battery_lookup = pd.read_csv(self.battery_file, index_col='battery_id')
        self.battery_strategies = pd.read_csv(self.battery_strategies_file, index_col='battery_strategy')

        # -------------------
        #  Identify load data
        # -------------------
        if len(self.study_parameters['load_folder'].unique()) == 1:
            self.different_loads = False  # Same load or set of loads for each scenario
        else:
            self.different_loads = True  # Different loads for each scenario
        self.load_path = os.path.join(self.base_path, 'load_profiles', self.study_parameters.loc[self.study_parameters.index[0], 'load_folder'])
        self.load_list = os.listdir(self.load_path)
        if len(self.load_list) == 0:
            logging.info('***************** Load folder %s is empty *************************', self.load_path)
            sys.exit("Missing load data")
        elif len(self.load_list) == 1:
            self.multiple_loads = False  # single load profile for each scenario
        else:
            self.multiple_loads = True  # multiple load profiles for each scenario - outputs are mean ,std dev, etc.

        # ---------------------------------------------
        # If same loads throughout Study, get them now:
        # ---------------------------------------------
        self.dict_load_profiles = {}
        if not self.different_loads:
            for load_name in self.load_list:
                loadFile = os.path.join(self.load_path, load_name)
                temp_load = pd.read_csv(loadFile,
                                        parse_dates=['timestamp'],
                                        dayfirst=True)
                temp_load = temp_load.set_index('timestamp')
                if not 'cp' in temp_load.columns:
                    temp_load['cp'] = 0
                self.dict_load_profiles[load_name] = temp_load

        # Otherwise, get the first load anyway:
        # -------------------------------------
        else:
            loadFile = os.path.join(self.load_path, self.load_list[0])
            temp_load = pd.read_csv(loadFile,
                                    parse_dates=['timestamp'],
                                    dayfirst=True)
            self.dict_load_profiles[self.load_list[0]] = temp_load.set_index('timestamp')

        # -----------------------------------------------------------------
        # Use first load profile to initialise timeseries and resident_list
        # -----------------------------------------------------------------
        # Initialise timeseries
        # ---------------------
        global ts  # (assume timeseries are all the same for all load profiles)
        ts = Timeseries(self.dict_load_profiles[self.load_list[0]])

        # Lists of meters / residents (includes cp)
        # -----------------------------------------
        # This is used for initialisation (and when different_loads = FALSE),
        # but RESIDENT_LIST CAN VARY for each scenario:
        self.resident_list = list(self.dict_load_profiles[self.load_list[0]].columns.values)
        # ---------------------------------------------------------------
        # Initialise Tariff Look-up table and generate all static tariffs
        # ---------------------------------------------------------------
        self.tariff_data = TariffData(tariff_lookup_path=self.t_lookupFile,
                                     reference_path=self.reference_path
                                     )
        self.tariff_data.generateStaticTariffs()
        # -----------------------------
        # Initialise output dataframes:
        # -----------------------------
        self.op = pd.DataFrame(index=self.scenario_list)

    def logStudyData(self):
        """Saves study outputs and summary to .csv files."""

        # For ease of handling, 3 csv files are created:
        # results_ has key values for all scenarios, averaged across multiple load profiles
        # customer_results has individual customer bills and total costs
        # results_std_dev has standard deviations of all averaged values
        # idex by scenario:

        self.op.index.name = 'scenario'
        # Separate individual customer data and save as csv
        if not self.different_loads:
            op_cust = self.op[[c for c in self.op.columns if 'cust_'in c and 'cp' not in c]]
            self.op = self.op.drop(op_cust.columns, axis =1)
            opcustFile = os.path.join(self.output_path, self.name + '_customer_results.csv')
            um.df_to_csv(op_cust, opcustFile)

        # Separate standard deviations and save as csv
        op_std = self.op[[c for c in self.op.columns if 'std'in c]]
        self.op = self.op.drop(op_std.columns, axis=1)
        opstdFile = os.path.join(self.output_path, self.name + '_results_std_dev.csv')
        um.df_to_csv(op_std, opstdFile)

        # Save remaining results for all scenarios
        opFile = os.path.join(self.output_path, self.name + '_results.csv')
        um.df_to_csv(self.op, opFile)

# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------


def runScenario(scenario_name):
    logging.info("Running Scenario number %i ", scenario_name)
    # Initialise scenario
    scenario = Scenario(scenario_name=scenario_name)
    eno = Network(scenario=scenario)
    # N.B. in embedded network scenarios, eno is the actual embedded network operator,
    # but in other scenarios, it is a virtual intermediary to organise energy and cash flows
    eno.initialiseAllTariffs(scenario)
    eno.initialiseAllBatteries(scenario)

    # Set up pv profile if allocation not load-dependent
    if scenario.pv_allocation == 'fixed':
        print('scenario', scenario.name, 'fixed')
        eno.allocatePv(scenario, scenario.pv)

    if scenario.has_solar_block:
        eno.initialiseDailySolarBlockQuotas(scenario)

    # Iterate through all load profiles for this scenario:
    for load_name in scenario.load_list:
        eno.initialiseBuildingLoads(load_name, scenario)
        if scenario.pv_allocation == 'load_dependent':  # ie. for btm_icp, btm_s_u and btm_s_c arrangements
            eno.allocatePv(scenario, scenario.pv)
            print('scenario', scenario.name, 'load_dep')
        eno.initialiseSolarInstQuotas(scenario)  # depends on load and pv

        # If no battery, calc all internal energy flows statically (i.e. as single df calculation)
        # ----------------------------------------------------------------------------------------
        if not eno.has_central_battery and not eno.any_resident_has_battery:
            eno.calcBuildingStaticEnergyFlows()
        else:
            # If battery, calculate energy flows stepwise:
            # --------------------------------------------
            for step in np.arange(0, ts.num_steps):
                eno.calcBuildingDynamicEnergyFlows(step)

        # If tariffs are dynamic (e.g block), calculate them stepwise:
        # ------------------------------------------------------------
        if eno.has_dynamic_tariff:
            for step in np.arange(0, ts.num_steps):
                eno.calcDynamicTariffs

        # Energy Flows for retailler (static)
        # -----------------------------------
        eno.setupRetailerFlows()  # Move this??
        eno.retailer.calcStaticEnergyFlows()

        # Summary energy metrics
        # ----------------------
        eno.calcEnergyParameters(scenario)

        # Financials
        # ----------
        eno.calcAllDemandCharges()
        eno.allocateAllCapex(scenario)  # per load profile to allow for scenarios where capex allocation depends on load
        scenario.calcResults(eno)
        if study.log_timeseries:
            eno.logTimeseries(scenario)
        #print(scenario_name, loadFile, eno.total_building_payment/100, (eno.receipts_from_residents - eno.total_payment)/100)
    # collate / log data for all loads in scenario
    # with lock: REINSTATE lock if using Threads
    scenario.logScenarioData()
    logging.info('Completed Scenario %i', scenario_name)
# ------------
# MAIN PROGRAM
# ------------
def main(base_path,project,study_name):

    # set up script logging
    pyname = os.path.basename(__file__)
    um.setup_logging(pyname)
    start_time = dt.datetime.now()

    try:
        # --------------------------------------
        # Initialise and load data for the study
        # --------------------------------------
        global study
        logging.info("study_name = %s", study_name)
        study = Study(base_path=base_path,
                    project=project,
                    study_name=study_name)

        # # -------------
        # # Use Threading
        # # -------------
        # global lock
        # num_worker_threads = num_threads
        # lock = threading.Lock()
        # with concurrent.futures.ThreadPoolExecutor(max_workers=num_worker_threads) as x:
        #     results = list(x.map(runScenario, study.scenario_list))

        # WITHOUT Threads (simpler to debug):
        # ----------------------------------
        for s in study.scenario_list:
            runScenario(s)
        study.logStudyData()
        # if len(study.output_list)>0:
        #     op = opm.Output(base_path = base_path,
        #                     project = project,
        #                     study_name = study_name)
        #     op.csv_output()
        #     op.plot_output()
        end_time = dt.datetime.now()
        duration = end_time-start_time
        print("***COMPLETED STUDY ***", study_name)
        logging.info("***COMPLETED STUDY %s ***", study_name)
        logging.info(" ********* Completed %i scenarios in %f **************", len(study.scenario_list), duration.seconds)
        logging.info(" ********* Time per Scenario is  %f **************", duration.seconds / len(study.scenario_list))

    except:
        pass
        logging.exception('\n\n\n Exception !!!!!!')
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

if __name__ == "__main__":

    # start = dt.datetime.now()
    # main(project='p_testing',
    #     study_name='test7a',
    #     base_path='C:\\Users\\z5044992\\Documents\\MainDATA\\DATA_EN_3')
    # end = dt.datetime.now()
    # duration = end - start
    # print(duration)

    # This is legacy code for optimising number of threads. left here as it is likely to be machine specific:
    # -------------------------------------------------------------------------------------------------------
    # global num_threads
    # thread_options = [4,6,8, 10, 12, 15, 20]
    # times = pd.DataFrame(columns=['start', 'end', 'time'], index=thread_options)
    # for num_threads in thread_options:
    #     times.loc[num_threads,'start'] = dt.datetime.now()
    #     print ('RUNNING WITH ',num_threads,' THREADS:')
    #     main(project='p_testing',
    #         study_name='test7a',
    #         base_path='C:\\Users\\z5044992\\Documents\\MainDATA\\DATA_EN_3')
    #     times.loc[num_threads,'end'] = dt.datetime.now()
    #     times.loc[num_threads,'time'] = times.loc[num_threads,'end'] -times.loc[num_threads,'start']
    # print(times)


    # This optimised to n = 6 threads
    # -------------------------------
    num_threads = 6



    # Import arguments - allows multi-processing from command line
    # ------------------------------------------------------------
    opts = {}  # Empty dictionary to store key-value pairs.
    while sys.argv:  # While there are arguments left to parse...
        if sys.argv[0][0] == '-':  # Found a "-name value" pair.
            opts[sys.argv[0]] =sys.argv[1]  # Add key and value to the dictionary.
        sys.argv = sys.argv[1:]
        # Reduce the argument list by copying it starting from index 1.
    if '-p' in opts:
        project = opts['-p']
    else:
        project = 'p_testing'
    if '-s' in opts:
        project = opts['-s']
    else:
        study = 'test7b'

    main(project=project,
         study_name=study,
         base_path='C:\\Users\\z5044992\\Documents\\MainDATA\\DATA_EN_3')


# TODO - FUTURE - Variable allocation of pv between cp and residents
# TODO - en_external scenario: cp tariff != TIDNULL

# TODO Add import-export plot to output module
# TODO test solar tariffs
# TODO Add combined central and individual PV
# TODO - Go through all tech arrangements and allow central and ind batteries / PC
# TODO Test battery
# TODO - Optimisaition: load all load files at start of scenario, only if different
# TODO - OpTIMISATION Separate financial settings from scenarios to reduce calculation
# TODO - Optimisaition: for loops -> i in np.arange rather than iter  thru' list
# TODO - Optimisaition: change all calcs to np.calcs
# TODO - Optimisaition: remove print, sort, etc.
# TODO - Optimisaition: time runs: i/o vs calcs
# TODO: Exception handling
# TODO Python anywhere / HPC
