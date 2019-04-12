'''
Created on 2018/04/03

Modified on 2018/05/29

@author: Arnau Gatell
'''
# Import necessary libraries
import os, time
import pandas as pd

# Import submodules
from HTMLParserAndCSVGenerator import HTMLParserAndCSVGenerator
#from energyDemandSimulator import simulatorRunner
from energyDemandDataConverter import energyDemandDataConverter
from graphsGenerator import graphsGenerator
from graphsGenerator import mapGenerator

# Init folder routes
temperaturesDataToRunFolder = 'dataToRunAndPlot/temperaturesDataToRun/'
energyDemandDataToPlotFolder = 'dataToRunAndPlot/energyDemandDataToPlot/'

# Init file routes to delete before each simulation
FMULog = 'Test_2.Examples.Example_10_log.txt'
FMUResult = 'Test_2.Examples.Example_10_result.txt'

# Set tool working mode
'''
____TOOL_WORKING_MODES____
----
toolWorkingMode variable integer possible values:
----
0. Complete --> Get temperatures, run simulator and create graphs.
1. Get temperature CSV files --> Get or refresh temperature CSV files.
2. Run simulator --> Run energy demand simulator for temperature files in folder temperaturesDataToRun. Output is located on totalEnergyDemandData folder.
3. Create graphs --> Create graphs from energy demand files in folder dataToRunAndPlot/energyDemandDataToPlot. Output is located on PNGGraphs.
----
'''
toolWorkingMode = 3

def runner():
    '''
    @summary: runner of the tool. Manager of all different submodules.
    '''
    if toolWorkingMode == 1 or toolWorkingMode == 0:
        get_and_create_temperatures_data_csvs()
    
    if toolWorkingMode == 2 or toolWorkingMode == 0:
        prepare_temperatures_data_csvs_structure_for_simulator()
        run_energy_demand_simulator_and_get_demand_csvs()
    
    if toolWorkingMode == 3 or toolWorkingMode == 0:
        create_graphs_from_csv_energy_demand_files()
    
    
def get_and_create_temperatures_data_csvs():
    '''
    @summary: creates temperatures csv files.
    '''
    meteocatStationsUrl = "http://www.meteo.cat/observacions/llistat-xema"
    meteocatStationsDataToCsv = HTMLParserAndCSVGenerator.HTMLParserAndCSVGenerator(meteocatStationsUrl)
    meteocatStationsDataToCsv.init_stations_list()
    meteocatStationsDataToCsv.fill_stations_list()
    meteocatStationsDataToCsv.fill_stations_temperature_data()
     
def prepare_temperatures_data_csvs_structure_for_simulator():
    '''
    @summary: deletes temperature csv columns with additional info and prepares csv to be run by the model 
                for each temperatures data csv in temperaturesDataToRun folder.
    '''
    temperaturesDateAndHourFilesList = os.listdir(temperaturesDataToRunFolder)
    for temperatureDateAndHourFile in temperaturesDateAndHourFilesList:
        # Check the file extension is .csv to avoid opening other temp files in directory
        if temperatureDateAndHourFile.endswith(".csv"):
            largeTempFile = pd.read_csv(temperaturesDataToRunFolder + temperatureDateAndHourFile, delimiter = ";")
            columnsToKeep = ['t', 'temp']
            shortTempFile = largeTempFile[columnsToKeep]
            shortTempFile.to_csv(temperaturesDataToRunFolder + temperatureDateAndHourFile, index = False, sep = ";")

def run_energy_demand_simulator_and_get_demand_csvs():
    '''
    @summary: runs energy demand simulator for each temperatures data csv in temperaturesDataToRun folder.
    '''
    temperaturesFilesList = os.listdir(temperaturesDataToRunFolder)
    for temperatureFile in temperaturesFilesList:
        # Check the file extension is .csv to avoid opening other temp files in directory
        if temperatureFile.endswith(".csv"):
#             linesNumber = sum(1 for line in open('temperaturesDataToRun/'+temperatureFile))
#             print temperatureFile, linesNumber
            simulator = simulatorRunner.simulatorRunner(temperatureFile)
            simulator.run_simulation_model()
            time.sleep(10)
            os.remove(FMULog)
            os.remove(FMUResult)
            time.sleep(10)

def create_graphs_from_csv_energy_demand_files():
    '''
    @summary: creates the graphics of each energy demand csv in dataToRunAndPlot/energyDemandDataToPlot folder.
    '''
    # List all files to plot
    energyDemandFilesNamesList = os.listdir(energyDemandDataToPlotFolder)
    
    # Iterate over each station to plot and plot it
    for energyDemandFileName in energyDemandFilesNamesList:
        if energyDemandFileName.endswith(".csv"):
            # Create all daily and monthly csvs
            energyDemandDataConverter.energyDemandDataConverter(energyDemandFileName)
            # Generate graphs from the csvs created right before
            graphs = graphsGenerator.graphsGenerator(energyDemandFileName)
            graphs.generate_monthly_demand_and_avg_temp_graph()
            graphs.generate_one_year_energy_distribution_ring_diagram()
            pass
    
    maps = mapGenerator.mapsGenerator(energyDemandFilesNamesList)
    maps.generate_locations_one_year_energy_demand_map()
    
    print 'All graphs created!'
    
if __name__ == '__main__':
    runner()