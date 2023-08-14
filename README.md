## Zeroing Script
The zeroing script takes in a spreadsheet output by the Ussing chamber containing a 'raw data' and 'protocol' tab. The script zeroes these data to the level portion before each drug was added and outputs to a new excel sheet including a line graph for each drug. It also generates a tab with the maximum/minimum values for each drug and a graph for each line in the protocol.

### Python Package Installations to Run the Script
- pandas
- openpyxl
- xlsxwriter

These can all be installed with `pip install <package>`

### Run the Script

The script can be run from command line with `/path/to/script/`.

You will be prompted to provide the path to the excel sheet. Make sure to include the `.xls` behind the file name.

You will also be asked to provide the rate that data was taken by the Ussing chamber software. If it was every second, enter `1`. If it was every 5 seconds, enter `5`. And so on.

### Output

The altered sheet will be output to the specified path to `Sheet_Name_alt.xlsx`. <br><br>

## Pellet Dimensioning Script
The pellet dimensioning script takes in an image containing an ArUco marker and mouse pellets. The script will return the image with each pellet labeled with its area, a bounding rectangle, and the rectangle dimensions.

### Python Package Installations to Run the Script
- opencv (opencv-python and opencv-contrib-python)
- matplotlib

These can all be installed with `pip install <package>`

### Image Requirements
The image must contain a 20x20mm ArUco marker that can be printed from [ArUco_Marker.svg](https://github.com/shiragg1/kaltschmidt_lab/blob/c6aa81a471a53feb5485f1a84fc4c1752430445c/ArUco_Marker.svg) or [this printout](https://docs.google.com/document/d/1ssPMNkhV7cSZT2itob3hjTp1seTUuteVR22VcEJyFa0/edit?usp=sharing).

The photo can be in any lighting, but *you will need to adjust the thresholds for different lighting*. Make sure that the pellets are spaced out and not touching.

### Run the Script
Before running the script, you will need to replace `'pellet_with_aruco.jpg'` on line 9 with your filename. You will also likely need to tweak the lower and upper bounds for thresholding on lines 34-35. [This color picker site](https://imagecolorpicker.com/en) is useful for determining the appropriate color codes. *Note that the color codes should be written in BGR order as opposed to the usual RGB.* If the script isn't picking up all of the pellets or if it is picking up non-pellet objects, adjust the size bounds on lines 93-94.

The script can be run from command line with `/path/to/script/`.

### Output

The script will show images at a few points in the process to help narrow down on the correct threshold. To move to the next image, press any key. The final image will have contours outlined in purple. Pellets of within the size bounds will be labeled with a green bounding rectangle and teal text with the area and rectangle dimensions.
