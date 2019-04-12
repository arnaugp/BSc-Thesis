'''
Created on 2017/11/27

@author: Marcel Macarulla

Modified on 2018/05/29

@author: Arnau Gatell
'''
# Import necessary libraries
import pandas
import numpy as N
from pyfmi import load_fmu
from collections import deque
import csv

class simulatorRunner(object):
    '''
    classdocs
    '''

    def __init__(self, csvFileName):
        '''
        Constructor
        '''
        self.csvFileName = csvFileName
        
        # Inputs/outputs folders
        self.temperaturesDataToRunFolder = 'dataToRunAndPlot/temperaturesDataToRun/'
        self.totalEnergyDemandDataFolder = 'data/totalEnergyDemandData/'
        
        self.totalSimulationTime = self.get_total_simulation_time()
    
    def run_simulation_model(self):
        '''
        @summary: requests the input object, runs the simulation model and calls the output generator to get the results CSV.
        '''
        input_object = self.generate_input()
        
        model = load_fmu('Test_2.Examples.Example_10.fmu')
        opts = model.simulate_options()
        opts['ncp'] = 0
        opts['CVode_options']['discr'] = 'Adams'
        opts['CVode_options']['atol'] = 1.0e-3
        opts['write_scaled_result'] = True
        #opts['filter']=['sensor']
        result = model.simulate(final_time = self.totalSimulationTime, input = input_object, options = opts)
        
        self.generate_output(result)
       
    def generate_input(self):
        '''
        @summary: reads the CSV file containing temperatures data and creates the input object to be used by the simulation model.
        '''
        # Open CSV file
        df = pandas.read_csv(self.temperaturesDataToRunFolder + self.csvFileName, sep=';')
        numpy_data = df.as_matrix()
        u=numpy_data.T[1:2]
        
        # Generate input
        csvFileLinesNumber = self.get_csvFile_lines_number()
        t = N.linspace(0., float(self.totalSimulationTime), int(csvFileLinesNumber-1))    
        u_traj = N.transpose(N.vstack((t,u[0])))
                
        # Create input object
        input_object = ('u', u_traj)
        
        return input_object
    
    def get_csvFile_lines_number(self):
        '''
        @summary: counts and returns the total number of lines of a CSV file.
        '''
        linesNumber = sum(1 for line in open(self.temperaturesDataToRunFolder + self.csvFileName))
        
        return linesNumber
    
    def get_total_simulation_time(self):
        '''
        @summary: gets the last time register (corresponding to the last temperature register) in the CSV file.
        '''
        fileContent = open(self.temperaturesDataToRunFolder + self.csvFileName, 'r')
        reader = csv.reader(fileContent, delimiter = ";")
        lastRegisteredTimeInCsv = int(deque(reader, 1)[0][0])
        fileContent.close()
        
        return lastRegisteredTimeInCsv
    
    def generate_output(self, result):
        '''
        @summary: creates the CSV output file with the energy demand.
        @param: result: simulation result.
        '''
        h_res = result['sensor']
        h_res1 = result['E_ven']
        h_res2 = result['E_cool']
        h_res3 = result['E_heat']
        t = result['time']
        
        output = N.transpose(N.vstack((t, h_res, h_res1, h_res2, h_res3)))
            
        n_out = pandas.DataFrame(output)
            
        n_out[2] = (n_out[2].T/3600000).T
        n_out[3] = (n_out[3].T/3600000).T
        n_out[4] = (n_out[4].T/3600000).T
            
        n_out.columns = ['Time[s]', 'Sensor[ppm]', 'E_ven[kWh]', 'E_cool[kWh]', 'E_heat[kWh]']
        
        n_out.to_csv(self.totalEnergyDemandDataFolder + 'ED_' + self.csvFileName, sep = ';')
