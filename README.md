# BSc in Industrial Technologies Engineering thesis (TFG)
## Summary
**Purpose:** This tool was developed from February 2018 to June 2018 for the BSc in Industrial Technologies Engineering final thesis in the Polytechnic University of Catalonia (UPC), ESEIAAT school, in Terrassa (Barcelona).  

**Thesis goal:** Assess the ambient temperature influence over the energy demand of a public concurrence building to keep indoor comfort conditions. Analyze the energy demand in several locations within Catalonia territory during a year.

**What is this?** This is a tool developed in Python to download weather data to use it as the input to run an energy demand simulator and plot the results.  
The main goals of the tool are:
1. Download temperatures data from different locations and create a cumulative register.
2. Run an energy demand simulator using as an input the temperatures data.
3. Plot the energy demand for each location.

**BSc thesis report:** [REPORT.pdf](https://github.com/arnaugp/BSc-Thesis/blob/master/BSc%20thesis%20docs/REPORT.pdf) :page_facing_up:

## Simulator input
The energy demand simulator takes as input .csv files with temperatures data from [Meteorological Service of Catalonia](meteo.cat).

## Output
The tool creates two graphs for each location and a map plot with overall results.
#### Pie chart
![Image of Pie chart](https://github.com/arnaugp/TFG/blob/master/PNGGraphs/oneYearEnergyPercentage/ED_X4_Barcelona-elRaval_20160519-20180518.png)

#### Combo chart
![Image of combo chart](https://github.com/arnaugp/TFG/blob/master/PNGGraphs/oneYearMonthlyDemandAndAvgTemp/ED_X4_Barcelona-elRaval_20160519-20180518.png)

### Map with overall results
![Image of overall map](https://github.com/arnaugp/TFG/blob/master/PNGGraphs/2017locationsEnergyDemand.png)

## Tool flowchart:
![Image of tool flowchart](https://github.com/arnaugp/TFG/blob/master/BSc%20thesis%20docs/Tool_flowchart.png)
