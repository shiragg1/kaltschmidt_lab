## Zeroing Script
The zeroing script takes in a spreadsheet output by the Ussing chamber containing a 'raw data' and 'protocol' tab. The script zeroes these data to the level portion before each drug was added and outputs to a new excel sheet. It also generates a tab with the maximum/minimum values for each drug and a graph for each line in the protocol.

### python3 Packages Used to Run the Script
- pandas
- openpyxl
- xlsxwriter
- numpy
- statistics

These can all be installed with `pip3 install <package>`

### Run the Script

The script can be run from command line with `/path/to/script/`.

You will be prompted to provide the path to the excel sheet. Make sure to include the `.xls` behind the file name.
