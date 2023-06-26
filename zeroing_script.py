#!/usr/bin/env python3

import pandas as pd
from statistics import mean
import numpy as np


def least_sd(data, time):
    """
    function to find the region within the 5 minutes prior to an infusion time
    inputs: dataset in the form of a list and the infusion time
    """

    # set the default range to 5 minutes before infusion
    range = data[time-300:time-240]
    # iterate through the 5 minutes before (in 10 second intervals)
    i = time - 240
    while i <= time - 60:
        # check if the stnadard deviation of each range is less than the previous
        if np.std(data[i:i+60]) > np.std(range):
            range = data[i:i+60]
        i+=10
    # output the best range
    return range


# path to the excel sheet
# file = "test.xls"

# get file from terminal input
print("please type the file name (and path)")
file = str(input())

# load the sheet
output = pd.read_excel(file, sheet_name = None)

# load the raw data
raw = pd.read_excel(file, sheet_name = 'raw data', header = 1)

# load the protocol
protocol = pd.read_excel(file, sheet_name = 'protocol', header = 1)

# create a list of drugs for the max/min sheet
max_min_index = []
# iterate through the protocol rows to get the list of drugs
for row in protocol.index:
    # extract drug name
    drug = protocol["Element"][row]
    max_min_index.append("MAX " + drug)
    max_min_index.append("MIN " + drug)

# create a column list for the max/min dataframe
max_min_cols = {'1', '2', '3', '4', '5', '6'}

# add sheet for max/min data
output["Max_Min Values"] = pd.DataFrame(index = max_min_index, columns = max_min_cols)

# iterate through the protocol rows
for row in protocol.index:
    # extract drug name
    drug = protocol["Element"][row]
    # extract time it was added
    time = protocol["Time"][row]
    # extract relevant channels
    channels = protocol["Tissues"][row].split()
    # create a dataframe for the drug's altered data
    alt = pd.DataFrame()

    # add relevent data to the columns
    for channel in channels:
        # note: for some reason the "raw data" column names have 2 spaces in front
        channel_data = raw["  I-" + channel]

        # first iteration code:

        # time_data = raw["Time"]
        # # find indeces of relavent time points for averaging 
        # # (if statements avoid errors if the time was skipped)
        # if (time - 60) in set(time_data):
        #     start = time_data[time_data == (time - 60)].index[0]
        # else:
        #     start = time_data[time_data == (time - 61)].index[0]

        # if time in set(time_data):
        #     stop = time_data[time_data == time].index[0]
        # else:
        #     stop = time_data[time_data == (time - 1)].index[0]

        # # calculate average current 1 min before infusion
        # avg_current = mean(channel_data[start:stop])

        avg_current = mean(least_sd(channel_data, time))

        # find the time of next infusion for the drug
        for row2 in protocol.index:
            # print(channel)
            # print(protocol["Tissues"][row2].find(channel))
            # print(protocol["Tissues"][row2])
            # print(row2 > row and protocol["Tissues"][row2].find(channel) >= 0)
            
            if row2 > row and protocol["Tissues"][row2].find(channel) >= 0:
                end = protocol["Time"][row2]
                break

        # define a series for the altered data
        altered_data = channel_data[time:end].apply(lambda x : x - avg_current)
        # create a DataFrame with the altered data
        altered_data_df = pd.DataFrame({channel: altered_data})
        # add the altered data to the main DataFrame
        alt = pd.concat([alt, altered_data], axis=1)

        # add value to sheet for max/min data
        output["Max_Min Values"][channel]["MAX " + drug] = altered_data_df.max()
        output["Max_Min Values"][channel]["MIN " + drug] = altered_data_df.min()

    # save the altered data to the sheet
    # note: the sheet names can't be > 31 char
    output[drug[:30]] = alt

# remove the .xls from the file name
file_name = file.split('.', 1)[0]

# save file to "output" sheet
with pd.ExcelWriter(file_name + "_alt.xlsx", engine='xlsxwriter') as writer:
    for ws_name, df_sheet in output.items():
        df_sheet.to_excel(writer, sheet_name=ws_name)

print('the altered data has been output to ', file_name, "_alt.xlsx")
