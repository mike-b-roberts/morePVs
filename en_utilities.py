# #This module contains a bunch of utility functions for
# use in processing timeseries data, load profiles, etc.
# import utility_module as um

# IMPORT Modules
import pandas as pd
import pythoncom
import win32api
import win32com.client
# import io
# from pytz import UTC
# from pytz import timezone
import datetime as dt
import numpy as np
import logging
import os
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as md
# import pdb, traceback, sys
# import calendar
# import pytz
# import seaborn as sns

def setup_logging(pyname):
    # Set up logfile
    log_folder = "C:\\PYTHONprojects\\py_logfiles"
    pyroot =  os.path.splitext(pyname)[0]
    runtime = dt.datetime.now()
    log_dir = os.path.join(log_folder, pyroot)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logname = "python_logfile_" + str(runtime.year) + "_" + str(runtime.month).zfill(2) + "_" + str(runtime.day).zfill(
        2) + "_" + str(runtime.hour).zfill(2) + str(runtime.minute).zfill(2) + ".txt"
    logpath = os.path.join(log_dir, logname)

    logging.basicConfig(level=logging.DEBUG, filename=logpath, filemode='w', format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')
    logging.info('Python Script is: %s',pyname )

###############################################################
def reshape_profile(df):
    # take an annual load profile organised as a single column df with column 'kW'
    # and returns a df with rows indexed by date, and columns by time (decimal hours)
    df_copy = df.copy() # so as to leave the original DataFrame intact
    df_copy.index = [df.index.date, df.index.hour + df.index.minute / 60]
    return df_copy['kW'].unstack()
###############################################################
def reshape_profile_gen(df,column):
    # More generalised version of reshape_profile that takes column name aswell
    # takes an annual load profile organised as a single column df with column 'kW'
    # and returns a df with rows indexed by date, and columns by time (decimal hours)
    df_copy = df.copy() # so as to leave the original DataFrame intact
    df_copy.index = [df.index.time,df.index.date]
    return df_copy[column].unstack()
###############################################################
def shift_tz(df):
    # Acts on a reshaped df timeseries with time as index, dates as columns
    # and does a crude timezone shift including DST
    year = df.columns[0].year
    dst_start = pd.to_datetime(dt.datetime(year,10,1))
    dst_end = pd.to_datetime(dt.datetime(year,4,1))
    #...... tbc

###############################################################
def df_to_csv(df,path):
    """Writes dataframe to .csv, first closing the .csv if it's open elsewhere."""
    # tries to save a df to a csv file,
    # traps io error and if the file is open elsewhere, closes the file
    # Adapted from
    # http: // timgolden.me.uk / python / win32_how_do_i / see - if -an - excel - workbook - is -open.html

    try:
        df.to_csv(path)
        logging.info('saved to %s', path)
        pass
    except IOError:
        context = pythoncom.CreateBindCtx(0)
        for moniker in pythoncom.GetRunningObjectTable():
            name = moniker.GetDisplayName(context, None)
            if name == path:
                obj = win32com.client.GetObject(path)
                obj.Close(True)
        df.to_csv(path)

###############################################################
def find_between( s, first, last ):
    # find string between 2 substrings
    # from https://stackoverflow.com/questions/3368969/find-string-between-two-substrings
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
###############################################################
def plot_tariffs(path = 'C:\\Users\\z5044992\\Documents\\MainDATA\\DATA_EN_3\\reference',
                 filename = 'static_import_tariffs.csv',
                 tariff_list = ['all']):
    """Plot a chart of price vs time for weekday and weekend."""

    # Set up plot path
    # ----------------
    plotpath = os.path.join(path,'tariff_plots')
    if not os.path.exists(plotpath):
        os.makedirs(plotpath)

    # Use static import and export tariffs saved in en reference folder
    # -----------------------------------------------------------------
    file = os.path.join(path,filename)
    data = pd.read_csv(file, parse_dates=['timestamp'],index_col='timestamp')
    if tariff_list != ['all']:
        data = data [tariff_list]
    # Average over weekday or weekend
    # -------------------------------
    df={}
    data['time'] = data.index.hour + data.index.minute / 60
    df['weekday'] = data.loc[data.index.weekday.isin([0, 1, 2, 3, 4])]
    df['weekend'] = data.loc[data.index.weekday.isin([5,6])]
    df['weekday'] = df['weekday'].groupby([df['weekday'].index.hour, df['weekday'].index.minute]).mean()
    df['weekend'] = df['weekend'].groupby([df['weekend'].index.hour, df['weekend'].index.minute]).mean()
    df['weekday'].set_index(['time'],inplace=True)
    df['weekend'].set_index(['time'],inplace=True)

    # Plot dataframes
    # ---------------
    colours = ['r', 'b', 'g', 'y', 'm', 'c'][0:len(df['weekday'].columns)]
    # NB: This uses pd.plot, not mpl.plot.
    # Note technique to plot 2 dfs on same axes
    ax = df['weekday'].plot(kind='line', linestyle='-', color=colours)
    df['weekend'].plot(kind='line',linestyle='--', color=colours, ax=ax)
    ax.xaxis.xmin=0
    ax.xaxis.xmax=24
    ax.set_xlabel("Hour", fontsize=20)
    ax.set_ylabel("tariff c/kWh", fontsize=20)
    ax.legend(df['weekday'].columns, fontsize=12, loc='best')
    ax.grid(True)
    #plt.show()
    print()
    plotFile = os.path.join(plotpath,('-'.join(tariff_list) +'.png'))

    # fig = ax[0].get_figure()
    plt.savefig(plotFile,dpi=1000)
    plt.close()


#MAIN PROGRAM

def main():
    plot_tariffs(tariff_list =['EASO_TOU_25pc','STS_35','STC_15' ])

    pass

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()

