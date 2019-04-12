'''
Created on 2018/05/10

Modified on 2018/05/29

@author: Arnau Gatell
'''
# Import necessary libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas

class graphsGenerator(object):
    '''
    classdocs
    '''

    def __init__(self, ED_csvFileName):
        '''
        Constructor
        '''
        self.ED_csvFileName = ED_csvFileName
        self.daySeconds = 86400
        
        # Inputs/outputs folders
        self.energyDemandDataToPlotFolder = 'dataToRunAndPlot/energyDemandDataToPlot/'
        self.energyDemandDataByDaysFolder = 'data/energyDemandDataByDays/'
        self.energyDemandDataByMonthsFolder = 'data/energyDemandDataByMonths/'
        self.energyDemandDataAndAvgTempByMonthsFolder = 'data/energyDemandAndAvgTempDataByMonths/monthly'
        self.PNGMonthlyDemandAndAvgTempGraphsFolder = 'PNGGraphs/oneYearMonthlyDemandAndAvgTemp/'
        self.PNGOneYearEnergyPercentage = 'PNGGraphs/oneYearEnergyPercentage/'
        
        # Get file data dates range
        self.firstRegisterDateInCsv = self.ED_csvFileName[-21:-13]
        self.lastRegisterDateInCsv = self.ED_csvFileName[-12:-4]
        
    def parse_monthly_ED_and_AvgTemp_csv_data(self):
        '''
        @summary: reads monthly energy demand and average temperature csv file and creates a list for each column.
        '''
        print 'Parsing energy demand and average temperature csv file to generate graph from ' + self.ED_csvFileName + ' file.'
        
        columnsNames = ['month', 'E_ven','E_cool', 'E_heat', 'E_total', 'AvgTemp', 'MaxTemp', 'MinTemp']
        columnsDataTypes = {'month': 'string', 'E_ven': 'string', 'E_cool': 'string', 'E_heat': 'string', 'E_total': 'string', 'AvgTemp': 'string',
                            'MaxTemp': 'string', 'MinTemp': 'string'}
        fileContent = pandas.read_csv(self.energyDemandDataAndAvgTempByMonthsFolder + self.ED_csvFileName, delimiter = ";", names = columnsNames, dtype = columnsDataTypes)
        
        timeByMonth = fileContent.month.tolist()[1:]
        ventilationEnergyByMonth = self.convert_list_string_elems_to_float(fileContent.E_ven.tolist()[1:])
        coolingEnergyByMonth = self.convert_list_string_elems_to_float(fileContent.E_cool.tolist()[1:])
        heatingEnergyByMonth = self.convert_list_string_elems_to_float(fileContent.E_heat.tolist()[1:])
        totalEnergyByMonth = self.convert_list_string_elems_to_float(fileContent.E_total.tolist()[1:])
        averageTempByMonth = self.convert_list_string_elems_to_int(fileContent.AvgTemp.tolist()[1:])
        maxTempByMonth = self.convert_list_string_elems_to_int(fileContent.MaxTemp.tolist()[1:])
        minTempByMonth = self.convert_list_string_elems_to_int(fileContent.MinTemp.tolist()[1:])
        
        return timeByMonth, ventilationEnergyByMonth, coolingEnergyByMonth, heatingEnergyByMonth, totalEnergyByMonth, averageTempByMonth, maxTempByMonth, minTempByMonth
    
    def convert_list_string_elems_to_float(self, stringsList):
        '''
        @summary: converts all string elements in a list into float type.
        @param: stringsList: list of string elements.
        '''
        floatsList = [float(i) for i in stringsList]
        
        return floatsList
    
    def convert_list_string_elems_to_int(self, stringsList):
        '''
        @summary: converts all string elements in a list into int type.
        @param: stringsList: list of string elements.
        '''
        integersList = [int(i) for i in stringsList]
        
        return integersList
    
    def generate_monthly_demand_and_avg_temp_graph(self):
        '''
        @summary: catches data by years to plot only complete years and calls the function that finally makes the plot.
        '''
        timeByMonth, ventilationEnergyByMonth, coolingEnergyByMonth, heatingEnergyByMonth, totalEnergyByMonth, averageTempByMonth, maxTempByMonth, minTempByMonth = self.parse_monthly_ED_and_AvgTemp_csv_data()
        
        # Edit month name to be plot. Change format from yyyymm to mm-yyyy
        timeByMonthToGraph = []
        numberOfMonths = []
        elem = 1
        for monthName in timeByMonth:
            timeByMonthToGraph.append(monthName[4:] + '-' + monthName[0:4])
            numberOfMonths.append(elem)
            
            elem += 1
            
        # Divide data to plot only complete years
        listElemNum = 0
        firstMonthFound = False
        for monthName in timeByMonthToGraph:
            if '01-' in monthName and firstMonthFound is False:
                firstMonthToPlotElemNum = listElemNum
                firstMonthFound = True
            if '12-' in monthName:
                lastMonthToPlotElemNum = listElemNum + 1
                
            listElemNum += 1
        
        # Create new lists containing only the elements to complete one year from the total elements lists
        yAxisVentE = ventilationEnergyByMonth[firstMonthToPlotElemNum:lastMonthToPlotElemNum]
        yAxisCoolE = coolingEnergyByMonth[firstMonthToPlotElemNum:lastMonthToPlotElemNum]
        yAxisHeatE = heatingEnergyByMonth[firstMonthToPlotElemNum:lastMonthToPlotElemNum]
        yAxisTotalE = totalEnergyByMonth[firstMonthToPlotElemNum:lastMonthToPlotElemNum]
        yAxisAvgTemp = averageTempByMonth[firstMonthToPlotElemNum:lastMonthToPlotElemNum]
        yAxisMaxTemp = maxTempByMonth[firstMonthToPlotElemNum:lastMonthToPlotElemNum]
        yAxisMinTemp = minTempByMonth[firstMonthToPlotElemNum:lastMonthToPlotElemNum]
        monthsNamesMMYYYY = timeByMonthToGraph[firstMonthToPlotElemNum:lastMonthToPlotElemNum]
        xAxisTime = numberOfMonths[0:len(monthsNamesMMYYYY)]
        
        # Create graph
        self.generate_three_stacked_bars_diagram_and_average_temp_line(xAxisTime, yAxisVentE, yAxisCoolE, yAxisHeatE, yAxisTotalE, monthsNamesMMYYYY, 150, yAxisAvgTemp, yAxisMaxTemp, yAxisMinTemp)
        
    def generate_three_stacked_bars_diagram_and_average_temp_line(self, xAxisTime, yAxisVentE, yAxisCoolE, yAxisHeatE, yAxisTotalE, names, energyUpperLimit, yAxisAvgTemp = None, yAxisMaxTemp = None, yAxisMinTemp = None):
        '''
        @summary: creates three stacked bars energy demand graph and plots three lines representing the period average, max and min temperature if parameter is passed.
        '''
        # Init some configuration parameters
        fontArial = {'fontname':'Arial'}
        barWidth = 0.9
        xUpperLimit = len(names) + 1
        yUpperLimit = max(yAxisTotalE) + 5
        
        # Height of barPart1 + barPart2
        bar3Bottom = map(sum, zip(yAxisVentE, yAxisCoolE))
        
        # Plot energy demand bars
        barPart1 = plt.bar(xAxisTime, yAxisVentE, color = '#03e707', edgecolor = 'white', width = barWidth, align = 'center')
        barPart2 = plt.bar(xAxisTime, yAxisCoolE, color = '#0beaf0', edgecolor = 'white', width = barWidth, align = 'center', bottom = yAxisVentE)
        barPart3 = plt.bar(xAxisTime, yAxisHeatE, color = '#d62728', edgecolor = 'white', width = barWidth, align = 'center', bottom = bar3Bottom)
        
        # Configure energy demand plot
        plt.ylim(0, yUpperLimit)
        plt.xlim(0, xUpperLimit)
        plt.legend((barPart1[0], barPart2[0], barPart3[0]), ('Ventilation Energy', 'Cooling Energy', 'Heating Energy'), loc = 9, prop={'size': 8, 'family': 'Arial'})
        plt.xticks(np.arange(1, len(names) + 1), names, fontsize = 10, rotation = 90, fontname = 'Arial')
        plt.yticks(np.arange(0, energyUpperLimit, 10.0))
        plt.ylabel('Energy demand [kWh]', **fontArial)
        plt.xlabel('Time [months]', **fontArial)
        plt.title("Location: " + self.ED_csvFileName.split('_')[2], **fontArial)
        
        if yAxisAvgTemp is not None:
            # Create temperature secondary y axis located on the right
            secondary_yaxis = plt.twinx()
            secondary_yaxis.set_yticks(np.arange(-14, 48, 2.0))
            secondary_yaxis.set_xlim(0, xUpperLimit)
            secondary_yaxis.set_ylim(-15, 50)
            secondary_yaxis.set_ylabel('Temperature [degrees Celsius]', **fontArial)
            # Plot average temperature
            secondary_yaxis.plot(xAxisTime, yAxisAvgTemp, marker='o', color='green')
            secondary_yaxis.plot(xAxisTime, yAxisMaxTemp, marker='o', color='red')
            secondary_yaxis.plot(xAxisTime, yAxisMinTemp, marker='o', color='blue')
            # Create average temperature legend
            secondary_yaxis.legend(['Average temperature', 'Maximum temperature', 'Minimum Temperature'], loc = 1, prop={'size': 8, 'family': 'Arial'})
        
        # Save to the specified route the figure created as a .png
        plt.savefig(self.PNGMonthlyDemandAndAvgTempGraphsFolder + self.ED_csvFileName[:-4], dpi = 240, bbox_inches='tight')
        
        # Clear saved figure to avoid next figure overwriting problems
        plt.clf()
        
        print 'Three stacked bars figure from ' + self.ED_csvFileName[3:] + ' generated! \n'
        
    def generate_one_year_energy_distribution_ring_diagram(self):
        '''
        @summary: plots one year energy demand distribution in percentage in a ring diagram.
        '''
        timeByMonth, ventilationEnergyByMonth, coolingEnergyByMonth, heatingEnergyByMonth, totalEnergyByMonth, averageTempByMonth, maxTempByMonth, minTempByMonth = self.parse_monthly_ED_and_AvgTemp_csv_data()
        
        fontArial = {'fontname':'Arial'}
        
        # Edit month name to be plot. Change format from yyyymm to mm-yyyy
        timeByMonthToGraph = []
        numberOfMonths = []
        elem = 1
        for monthName in timeByMonth:
            timeByMonthToGraph.append(monthName[4:] + '-' + monthName[0:4])
            numberOfMonths.append(elem)
            
            elem += 1
        
        # Divide data to plot only complete years
        listElemNum = 0
        firstMonthFound = False
        for monthName in timeByMonthToGraph:
            if '01-' in monthName and firstMonthFound is False:
                firstMonthToPlotElemNum = listElemNum
                firstMonthFound = True
            if '12-' in monthName:
                lastMonthToPlotElemNum = listElemNum + 1
                
            listElemNum += 1
        
        # Create new lists containing only the elements to complete one year from the total elements lists
        ventilationEnergyByMonth = ventilationEnergyByMonth[firstMonthToPlotElemNum:lastMonthToPlotElemNum]
        coolingEnergyByMonth = coolingEnergyByMonth[firstMonthToPlotElemNum:lastMonthToPlotElemNum]
        heatingEnergyByMonth = heatingEnergyByMonth[firstMonthToPlotElemNum:lastMonthToPlotElemNum]
        totalEnergyByMonth = totalEnergyByMonth[firstMonthToPlotElemNum:lastMonthToPlotElemNum]
        
        totalCoolingEnergy = sum(map(float,coolingEnergyByMonth))
        totalHeatingEnergy = sum(map(float,heatingEnergyByMonth))
        totalVentilationEnergy = sum(map(float,ventilationEnergyByMonth))
        totalEnergyDemand = sum(map(float,totalEnergyByMonth))
        
        # Data to plot
        sizes = [totalCoolingEnergy, totalHeatingEnergy, totalVentilationEnergy]
        colors = ['blue', 'red', 'green']
        explode = (0.0, 0.0, 0.0)  # explode 1st slice
         
        # Create a circle for the center of the plot
        my_circle = plt.Circle( (0,0), 0.7, color='white')

        # Plot
        plt.pie(sizes, explode=explode, colors=colors,
                autopct='%1.1f%%', shadow=False, startangle=30)
        plt.legend(['Cooling Energy', 'Heating Energy', 'Ventilation Energy'], loc = 2, prop={'size': 8, 'family': 'Arial'})
        plt.title("Location: " + self.ED_csvFileName.split('_')[2], **fontArial)
        plt.text(-0.52, 0, 'Year energy demand = ' + str(int(totalEnergyDemand)) + ' kWh', **fontArial)
        
        plt.axis('equal')
        p=plt.gcf()
        p.gca().add_artist(my_circle)

        
        # Save to the specified route the figure created as a .png
        plt.savefig(self.PNGOneYearEnergyPercentage + self.ED_csvFileName[:-4], dpi = 240, bbox_inches='tight')
        
        # Clear saved figure to avoid next figure overwriting problems
        plt.clf()
        
        print 'One year energy demand percentage ring ' + self.ED_csvFileName + ' generated! \n'
