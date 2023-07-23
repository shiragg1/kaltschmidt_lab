#!/usr/bin/env python3

import pandas as pd
from statistics import mean
import numpy as np


def least_sd(data, time, rate):
    """
    function to find the region within the 5 minutes prior to an infusion time
    inputs: dataset in the form of a list and the infusion time
            rate refers to the amount of time between each reading
    """
    start = time-300//rate
    print(start)
    end = time-240//rate

    # set the default range to 5 minutes before infusion
    range = data[start:end]
    # iterate through the 5 minutes before (in 10 second intervals)
    i = time - 240//rate
    while i <= time - 60//rate:
        # check if the standard deviation of each range is less than the previous
        if np.std(data[i:i+60//rate]) > np.std(range):
            range = data[i:i+60//rate]
        i+=10//rate
    # output the best range
    return range


# path to the excel sheet
# file = "test.xls"

# get file from terminal input
print("please type the file name (and path)")
file = str(input())

# get the rate the ussing chamber was set to
print("what was the rate of data retrieval?")
rate = int(input())

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
    # if the drug is ATP, break out of the process
    if "ATP" in drug:
        break
    max_min_index.append("MAX " + drug)
    max_min_index.append("MIN " + drug)

# create a column list for the max/min dataframe
max_min_cols = ['1', '1 time', '2', '2 time', '3', '3 time', '4', '4 time', '5', '5 time', '6', '6 time']

# add sheet for max/min data
output["Max_Min Values"] = pd.DataFrame(index = max_min_index, columns = max_min_cols)

# create a list to keep track of new sheet names
new_sheets = []

# iterate through the protocol rows
for row in protocol.index:
    # extract drug name
    drug = protocol["Element"][row]
    # if the drug is ATP, break out of the process
    if "ATP" in drug:
        break
    # extract time it was added
    time = protocol["Time"][row]
    print(raw["Time"][raw["Time"]==time].index.values)
    time_index = raw["Time"][raw["Time"]==time].index.values[0]
    print(time_index)
    # extract relevant channels
    # note: must be a cast to string for edge case that there is just one channel
    channels = str(protocol["Tissues"][row]).split()
    # create a dataframe for the drug's altered data
    alt = pd.DataFrame()

    # add relevent data to the columns
    for channel in channels:
        # note: for some reason the "raw data" column names have 2 spaces in front
        channel_data = raw["  I-" + channel]
        print(least_sd(channel_data, time, rate))
        avg_current = mean(least_sd(channel_data, time_index, rate))

        # find the time of next infusion for the drug
        for row2 in protocol.index:
            # condition for having one tissue in the row
            if isinstance(protocol["Tissues"][row2], int):
                if row2 > row and str(protocol["Tissues"][row2]) == channel:
                    end = protocol["Time"][row2]
                    break
            elif row2 > row and protocol["Tissues"][row2].find(channel) >= 0:
                end = protocol["Time"][row2]
                break
            else:
                end = raw.index[-1]

        # define a series for the altered data
        altered_data = channel_data[time_index:end].apply(lambda x : x - avg_current)
        # create a DataFrame with the altered data
        altered_data_df = pd.DataFrame({channel: altered_data})
        # add the altered data to the main DataFrame
        alt = pd.concat([alt, altered_data], axis=1)
        
        # add value to sheet for max/min data
        output["Max_Min Values"][channel]["MAX " + drug] = altered_data_df[channel].max()
        output["Max_Min Values"][channel + " time"]["MAX " + drug] = altered_data_df[channel].idxmax()
        output["Max_Min Values"][channel]["MIN " + drug] = altered_data_df[channel].min()
        output["Max_Min Values"][channel + " time"]["MIN " + drug] = altered_data_df[channel].idxmin()

    # save the altered data to the sheet
    # note: the sheet names can't be > 31 char
    output[drug[:30]] = alt
    # add the name to list of new sheets
    new_sheets.append(drug[:30])

# remove the .xls from the file name
file_name = file.split('.', 1)[0]

# save file to "output" sheet
with pd.ExcelWriter(file_name + "_alt.xlsx", engine='xlsxwriter') as writer:
    for ws_name, df_sheet in output.items():
        df_sheet.to_excel(writer, sheet_name=ws_name)
        # add a chart to sheets in the protocol
        if ws_name in new_sheets:
            workbook = writer.book
            worksheet = writer.sheets[ws_name]
            chart = workbook.add_chart({'type': 'line'})

            start_time = df_sheet.index[1]
            end_time = df_sheet.index[-1]
            for i in range(len(df_sheet.columns)):
                col = i + 1
                chart.add_series({
                    'name':       [ws_name, 0, col],
                    'categories': [ws_name, 1, 0, end_time, 0],
                    'values':     [ws_name, 1, col, end_time - start_time, col]
                })

            chart.set_x_axis({'name': 'Time (sec)', 'min': start_time, 'max': end_time})
            chart.set_y_axis({'name': 'Normalized Current (a.u.)'})
            worksheet.insert_chart('K2', chart)

print('the altered data has been output to ', file_name, "_alt.xlsx")
