# #This module contains a bunch of utility functions for
# use in processing timeseries data, load profiles, etc.
# import utility_module as um

# IMPORT Modules
import pandas as pd
import os
import pythoncom
import win32api
import win32com.client
# import io
# from pytz import UTC
# from pytz import timezone
import datetime as dt
# import requests
# import numpy as np
import logging
import os
# import time
# import matplotlib as mpl
# import matplotlib.pyplot as plt
# import matplotlib.dates as md
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
    # takes an annual load profile organised as a single column df with column 'kW'
    # and returns a df with rows indexed by date, and columns by time (decimal hours)
    df_copy = df.copy() # so as to leave the original DataFrame intact
    df_copy.index = [df.index.date, df.index.hour + df.index.minute / 60]
    return df_copy['kW'].unstack()
###############################################################
def reshape_profile_gen(df,column):
    # More generalised version of reshape_profile
    # takes column name aswell
    # takes an annual load profile organised as a single column df with column 'kW'
    # and returns a df with rows indexed by date, and columns by time (decimal hours)
    df_copy = df.copy() # so as to leave the original DataFrame intact
    df_copy.index = [df.index.time,df.index.date]
    return df_copy[column].unstack()
###############################################################
def shift_tz(df):
    # Acts on a reshaped df timeseries with time as index, dates as columns
    # and does a crudetimezone shift including DST
    year = df.columns[0].year
    dst_start = pd.to_datetime(dt.datetime(year,10,1))
    dst_end = pd.to_datetime(dt.datetime(year,4,1))

###############################################################

def df_to_csv(df,path):
    """Writes dataframe to .csv, first closing the .csv if it's open elsewhere."""
    # tries to save a df to a csv file,
    # traps io error and if the file is open in excel, closes the file
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


#MAIN PROGRAM

def main():
    pass

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()

