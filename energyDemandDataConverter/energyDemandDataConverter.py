'''
Created on 2018/05/12

Modified on 2018/05/29

@author: Arnau Gatell
'''
# Import necessary libraries
import pandas
import os

class energyDemandDataConverter(object):
    '''
    classdocs
    '''

    def __init__(self, ED_csvFileName):
        '''
        Constructor
        '''
        # Init variables
        self.ED_csvFileName = ED_csvFileName
        self.oneHourSeconds = 3600 
        self.daySeconds = 86400
        
        # Init dictionaries
        self.hourlyLists = {}
        self.dailyLists = {}
        self.monthlyLists = {}
        
        # Inputs/outputs folders
        self.temperaturesDataFolder = 'data/temperaturesData/'
        self.energyDemandDataToPlotFolder = 'dataToRunAndPlot/energyDemandDataToPlot/'
        self.energyDemandDataByHoursFolder = 'data/energyDemandDataByHours/'
        self.energyDemandDataByDaysFolder = 'data/energyDemandDataByDays/'
        self.energyDemandDataByMonthsFolder = 'data/energyDemandDataByMonths/'
        self.energyDemandDataAndAvgTempByMonthsFolder = 'data/energyDemandAndAvgTempDataByMonths/'
        
        # Get file data dates range
        self.firstEDRegisterDateInCsv = self.ED_csvFileName[-21:-13]
        self.lastEDRegisterDateInCsv = self.ED_csvFileName[-12:-4]
        
        # Parse energy demand data csv and create csvs for energy demand by hours, days and months
        self.parse_total_demand_csv_data()
        self.parse_temperature_csv_data()
        self.generate_hourly_demand_csv()
        self.generate_daily_demand_csv()
        self.generate_monthly_demand_csv()
        self.generate_monthly_demand_and_avgMinMax_temp_csv()
                
    def parse_total_demand_csv_data(self):
        '''
        @summary: reads total energy demand csv file, creates a list for each column and saves this lists as self (global within this class) variables.
        '''
        print 'Parsing total energy demand csv file to convert data from ' + self.ED_csvFileName + ' file.'
        
        # Read energy demand CSV
        columnsNames = ['Time', 'Sensor','E_ven','E_cool', 'E_heat']
        columnsDataTypes = {'Time': 'string', 'Sensor': 'string', 'E_ven': 'string', 'E_cool': 'string', 'E_heat': 'string'}
        fileContent = pandas.read_csv(self.energyDemandDataToPlotFolder + self.ED_csvFileName, delimiter = ";", names = columnsNames, dtype = columnsDataTypes)
        
        # Save each CSV column in a list
        self.CSVTimeList = self.convert_list_string_elems_to_float(fileContent.Time.tolist()[1:])
        self.CSVVentilationEnergyList = self.convert_list_string_elems_to_float(fileContent.E_ven.tolist()[1:])
        self.CSVCoolingEnergyList = self.convert_list_string_elems_to_float(fileContent.E_cool.tolist()[1:])
        self.CSVHeatingEnergyList = self.convert_list_string_elems_to_float(fileContent.E_heat.tolist()[1:])
        self.CSVTotalEnergyList = self.calculate_total_energy_demand()
        
    def parse_temperature_csv_data(self):
        '''
        @summary: reads total temperatures csv file, creates a list for each column and saves this lists as self (global within this class) variables.
        '''
        self.temperatureFileName = None
        
        temperaturesFilesList = os.listdir(self.temperaturesDataFolder)
        for temperatureFileName in temperaturesFilesList:
            temperatureFileFirstRegisterDate = temperatureFileName[-21:-13]
            ED_stationCode = self.ED_csvFileName[3:6]
            if ED_stationCode in temperatureFileName and self.firstEDRegisterDateInCsv == temperatureFileFirstRegisterDate:
                self.temperatureFileName = temperatureFileName
                break
        
        if self.temperatureFileName is not None:
            # Read temperature CSV
            columnsNames = ['t', 'temp','date','hour']
            columnsDataTypes = {'t': 'string', 'temp': 'string', 'date': 'string', 'hour': 'string'}
            
            fileContent = pandas.read_csv(self.temperaturesDataFolder + self.temperatureFileName, delimiter = ";", names = columnsNames, dtype = columnsDataTypes)
            
            # Save each temperature CSV column in a list
            self.tempCSVTimeList = self.convert_list_string_elems_to_int(fileContent.t.tolist()[1:])
            self.tempCSVTemperatureList = self.convert_list_string_elems_to_int(fileContent.temp.tolist()[1:])
            self.tempCSVDateList = fileContent.date.tolist()[1:]
            self.tempCSVHourList = fileContent.hour.tolist()[1:]
            
        else:
            print 'ERROR: CSV temperature file from station with code ' + self.ED_csvFileName[2:6] + ' not found.'
    
    def calculate_total_energy_demand(self):
        '''
        @summary: adds the energy demand for each purpose from a float list and creates a list with the addition result.
        '''
        totalEnergyDemand = map(sum, zip(self.CSVVentilationEnergyList, self.CSVCoolingEnergyList, self.CSVHeatingEnergyList))
        
        return totalEnergyDemand
    
    def calculate_hourly_energy_demand(self):
        '''
        @summary: calculates each hour energy demand and adds this information to dict self.hourlyLists.
        '''
        # Init necessary variables
        elemNum = 0
        lastHourTime = 0
        lastHourElem = 0
        currentRegisterHourNumber = 0
        currentRegisterHour = '00:00'
        
        # Init data lists
        timeByHour = []
        timeByDay = []
        ventilationEnergyByHours = []
        coolingEnergyByHours = []
        heatingEnergyByHours = []
        totalEnergyByHours = []
        
        # Get CSV data lists
        dayDate = self.firstEDRegisterDateInCsv
        time = self.CSVTimeList
        ventilationEnergy = self.CSVVentilationEnergyList
        coolingEnergy = self.CSVCoolingEnergyList
        heatingEnergy = self.CSVHeatingEnergyList
        totalEnergy = self.CSVTotalEnergyList
        
        # Iterate over each CSV row element
        for elem in time:
            # Appends one hour data
            if elem > (self.oneHourSeconds + lastHourTime):
                # Get one hour energy demand
                hourVentilationEnergy = ventilationEnergy[elemNum-1] - ventilationEnergy[lastHourElem]
                hourCoolingEnergy = coolingEnergy[elemNum-1] - coolingEnergy[lastHourElem]
                hourHeatingEnergy = heatingEnergy[elemNum-1] - heatingEnergy[lastHourElem]
                hourTotalEnergy = totalEnergy[elemNum-1] - totalEnergy[lastHourElem]
                
                # Append one hour energy demand
                timeByHour.append(currentRegisterHour)
                timeByDay.append(dayDate)
                ventilationEnergyByHours.append(hourVentilationEnergy)
                coolingEnergyByHours.append(hourCoolingEnergy)
                heatingEnergyByHours.append(hourHeatingEnergy)
                totalEnergyByHours.append(hourVentilationEnergy + hourCoolingEnergy + hourTotalEnergy)
                
                # Refresh variables
                currentRegisterHourNumber += 1
                lastHourTime += self.oneHourSeconds
                lastHourElem = elemNum
                
                # Refresh day date
                if currentRegisterHourNumber == 24:
                    currentRegisterHourNumber = 0
                    dayDate = self.refresh_date(dayDate)
                
                # Refresh hour
                currentRegisterHour = self.calculate_current_register_hour(currentRegisterHourNumber)
            else:
                pass
            
            elemNum += 1
        
        # Fill hourly lists dictionary
        self.hourlyLists['timeByDay'] = timeByDay
        self.hourlyLists['timeByHour'] = timeByHour
        self.hourlyLists['ventilationEnergyByHours'] = ventilationEnergyByHours
        self.hourlyLists['coolingEnergyByHours'] = coolingEnergyByHours
        self.hourlyLists['heatingEnergyByHours'] = heatingEnergyByHours
        self.hourlyLists['totalEnergyByHours'] = totalEnergyByHours
    
    def calculate_current_register_hour(self, currentRegisterHourNumber):
        '''
        @summary: calculates the hour that corresponds to the register number in the table of temperatures. Thanks to this, it is ensured that data is properly collected.
        @param: currentRegisterHourNumber: integer containing current temperature register number. Each day has 48 registers of temperature (every half hour).
        '''
        currentRegisterHour = str(currentRegisterHourNumber) + ':00'
         
        if len(currentRegisterHour) < 5:
            currentRegisterHour = '0' + currentRegisterHour
            
        return currentRegisterHour
    
    def calculate_daily_energy_demand(self):
        '''
        @summary: calculates each day energy demand and adds this information to dict self.dailyLists.
        '''
        # Save hourly demand dictionary keys into variables
        timeByDayHourly = self.hourlyLists['timeByDay']
        ventilationEnergyByHours = self.hourlyLists['ventilationEnergyByHours']
        coolingEnergyByHours = self.hourlyLists['coolingEnergyByHours']
        heatingEnergyByHours = self.hourlyLists['heatingEnergyByHours']
        totalEnergyByHours = self.hourlyLists['totalEnergyByHours']
        
        # Init necessary variables
        elemNum = 0
        lastDayDate = 0
        firstIteration = True
        dayVentilationEnergy = 0
        dayCoolingEnergy = 0
        dayHeatingEnergy = 0
        dayTotalEnergy = 0
        
        # Init data lists
        timeByDay = []
        ventilationEnergyByDay = []
        coolingEnergyByDay = []
        heatingEnergyByDay = []
        totalEnergyByDay = []
        
        # Iterate over each hour in lists
        for dayDate in timeByDayHourly:
            currentDay = dayDate
            if currentDay != lastDayDate and firstIteration is False:
                # Append one day data
                timeByDay.append(lastDayDate)
                ventilationEnergyByDay.append(dayVentilationEnergy)
                coolingEnergyByDay.append(dayCoolingEnergy)
                heatingEnergyByDay.append(dayHeatingEnergy)
                totalEnergyByDay.append(dayTotalEnergy)
                
                # Reset one day data to 0
                dayVentilationEnergy = 0
                dayCoolingEnergy = 0
                dayHeatingEnergy = 0
                dayTotalEnergy = 0
                
            else:
                pass
            
            # Add each day energy demand to current month list element
            dayVentilationEnergy += ventilationEnergyByHours[elemNum]
            dayCoolingEnergy += coolingEnergyByHours[elemNum]
            dayHeatingEnergy += heatingEnergyByHours[elemNum]
            dayTotalEnergy += totalEnergyByHours[elemNum]
            
            # Refresh variables
            lastDayDate = currentDay
            firstIteration = False
            elemNum += 1
        
        # Fill daily lists dictionary
        self.dailyLists['timeByDay'] = timeByDay
        self.dailyLists['ventilationEnergyByDay'] = ventilationEnergyByDay
        self.dailyLists['coolingEnergyByDay'] = coolingEnergyByDay
        self.dailyLists['heatingEnergyByDay'] = heatingEnergyByDay
        self.dailyLists['totalEnergyByDay'] = totalEnergyByDay
    
    
    def calculate_monthly_energy_demand(self):
        '''
        @summary: calculates each month energy demand and adds this information to dict self.monthlyLists.
        '''
        # Save daily demand dictionary into variables
        timeByDay = self.dailyLists['timeByDay']
        ventilationEnergyByDay = self.dailyLists['ventilationEnergyByDay']
        coolingEnergyByDay = self.dailyLists['coolingEnergyByDay']
        heatingEnergyByDay = self.dailyLists['heatingEnergyByDay']
        totalEnergyByDay = self.dailyLists['totalEnergyByDay']
        
        # Init necessary variables
        elemNum = 0
        lastMonthDate = 0
        firstIteration = True
        monthVentilationEnergy = 0
        monthCoolingEnergy = 0
        monthHeatingEnergy = 0
        monthTotalEnergy = 0
        
        # Init data lists
        timeByMonth = []
        ventilationEnergyByMonths = []
        coolingEnergyByMonths = []
        heatingEnergyByMonths = []
        totalEnergyByMonths = []
        
        # Iterate over each day in lists
        for dayDate in timeByDay:
            currentMonth = dayDate[:6] # yyyymm
            if currentMonth != lastMonthDate and firstIteration is False:
                # Append one month data
                timeByMonth.append(lastMonthDate)
                ventilationEnergyByMonths.append(monthVentilationEnergy)
                coolingEnergyByMonths.append(monthCoolingEnergy)
                heatingEnergyByMonths.append(monthHeatingEnergy)
                totalEnergyByMonths.append(monthTotalEnergy)
                
                # Reset one month data to 0
                monthVentilationEnergy = 0
                monthCoolingEnergy = 0
                monthHeatingEnergy = 0
                monthTotalEnergy = 0
            
            else:
                pass
            
            # Add each month energy demand to current month list element
            monthVentilationEnergy += ventilationEnergyByDay[elemNum]
            monthCoolingEnergy += coolingEnergyByDay[elemNum]
            monthHeatingEnergy += heatingEnergyByDay[elemNum]
            monthTotalEnergy += totalEnergyByDay[elemNum]
            
            # Refresh variables
            lastMonthDate = currentMonth
            firstIteration = False
            elemNum += 1
        
        # Fill monthly lists dictionary
        self.monthlyLists['timeByMonth'] = timeByMonth
        self.monthlyLists['ventilationEnergyByMonth'] = ventilationEnergyByMonths
        self.monthlyLists['coolingEnergyByMonth'] = coolingEnergyByMonths
        self.monthlyLists['heatingEnergyByMonth'] = heatingEnergyByMonths
        self.monthlyLists['totalEnergyByMonth'] = totalEnergyByMonths
        
    def calculate_monthly_averageMinMax_temperature(self):
        '''
        @summary: calculates each month average max and min temperature and adds this information to dict self.monthlyLists.
        '''
        # Save temperature CSV columns lists
        temperatureByHalfHour = self.tempCSVTemperatureList
        registerDateByHalfHour = self.tempCSVDateList
        
        # Init necessary variables
        elemNum = 0
        oneMonthRegisters = 0
        lastMonthDate = 0
        firstIteration = True
        monthAverageTemp = 0
        monthMaxTemp = -10
        monthMinTemp = 30
        
        # Init data lists
        averageTempTimeByMonth = []
        averageTempByMonth = []
        minTempByMonth = []
        maxTempByMonth = []
        
        # Iterate over each day in lists
        for dateByHalfHour in registerDateByHalfHour:
            currentMonth = dateByHalfHour[:6] # yyyymm
            if currentMonth != lastMonthDate and firstIteration is False:
                # Calculate month average temperature
                monthAverageTemp = monthAverageTemp/oneMonthRegisters
                
                # Append one month data
                averageTempTimeByMonth.append(lastMonthDate)
                averageTempByMonth.append(monthAverageTemp)
                minTempByMonth.append(monthMinTemp)
                maxTempByMonth.append(monthMaxTemp)
                
                # Reset one month data to 0
                monthAverageTemp = 0
                oneMonthRegisters = 0
                monthMaxTemp = -10
                monthMinTemp = 30
            
            else:
                pass
            
            # Add each register temperature
            monthAverageTemp += temperatureByHalfHour[elemNum]
            
            # Modify if necessary max and min month temperatures
            if temperatureByHalfHour[elemNum] > monthMaxTemp:
                monthMaxTemp = temperatureByHalfHour[elemNum]
            if temperatureByHalfHour[elemNum] < monthMinTemp:
                monthMinTemp = temperatureByHalfHour[elemNum]
            
            # Refresh variables
            lastMonthDate = currentMonth
            firstIteration = False
            oneMonthRegisters += 1
            elemNum += 1
        
        # Fill monthly lists dictionary only if month exists
        elem = 0
        firstMonth = 0
        lastMonth = 0
        firstEntrance = True
        
        for month in self.monthlyLists['timeByMonth']:
            if month == averageTempTimeByMonth[elem]:
                if firstEntrance is True:
                    firstMonth = elem
                    firstEntrance = False
                
                lastMonth = elem + 1
            
            elem += 1
        
        self.monthlyLists['averageTempByMonth'] = averageTempByMonth[firstMonth:lastMonth]
        self.monthlyLists['minTempByMonth'] = minTempByMonth[firstMonth:lastMonth]
        self.monthlyLists['maxTempByMonth'] = maxTempByMonth[firstMonth:lastMonth]
    
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
    
    def refresh_date(self, dayDate):
        '''
        @summary: refreshes the date with the immediately following day. Calculations consider each month quantity of days.
        @param: dayDate: date of the day to be refreshed. Format yyyymmdd.
        '''
        day = str(dayDate)[-2:]
        month = str(dayDate)[-4:-2]
        year = str(dayDate)[:4]
        
        if int(month) == 1 or int(month) == 3 or int(month) == 5 or int(month) == 7 or int(month) == 8 or int(month) == 10:
            if int(day) == 31:
                day = "01"
                month = self.add_zeroes_to_date(str(int(month)+1))
            else:
                day = self.add_zeroes_to_date(str(int(day)+1))
            
        elif int(month) == 2:
            if int(day) == 28:
                day = "01"
                month = self.add_zeroes_to_date(str(int(month)+1))
            else:
                day = self.add_zeroes_to_date(str(int(day)+1))
            
        elif int(month) == 4 or int(month) == 6 or int(month) == 9 or int(month) == 11:
            if int(day) == 30:
                day = "01"
                month = self.add_zeroes_to_date(str(int(month)+1))
            else:
                day = self.add_zeroes_to_date(str(int(day)+1))
        
        elif int(month) == 12:
            if int(day) == 31:
                day = "01"
                month = "01"
                year = str(int(year)+1)
            else:
                day = self.add_zeroes_to_date(str(int(day)+1))
        
        dayDate = year + month + day
        
        return dayDate
    
    def add_zeroes_to_date(self, number):
        '''
        @summary: adds a zero to numbers of one only one character
        @param: number: string containing a number character or characters.
        '''
        if len(number) < 2:
            number = '0' + number
        else:
            pass
        
        return number

    def generate_hourly_demand_csv(self):
        '''
        @summary: creates csv file containing one location energy demand by hours.
        '''
        self.calculate_hourly_energy_demand()
        
        # Create hourly demand CSV
        columnsNames = ['day', 'hour', 'E_ven', 'E_cool', 'E_heat', 'E_total']
        df = pandas.DataFrame(data={"day": self.hourlyLists['timeByDay'], "hour": self.hourlyLists['timeByHour'], 
                                    "E_ven": self.hourlyLists['ventilationEnergyByHours'], "E_cool": self.hourlyLists['coolingEnergyByHours'], 
                                    "E_heat": self.hourlyLists['heatingEnergyByHours'], "E_total": self.hourlyLists['totalEnergyByHours']}, columns = columnsNames)
        df.to_csv(self.energyDemandDataByHoursFolder + 'hourly' + self.ED_csvFileName, sep=';',index=False)
    
    def generate_daily_demand_csv(self):
        '''
        @summary: creates csv file containing one location energy demand by days.
        '''
        self.calculate_daily_energy_demand()
        
        # Create hourly demand CSV
        columnsNames = ['day', 'E_ven', 'E_cool', 'E_heat', 'E_total']
        df = pandas.DataFrame(data={"day": self.dailyLists['timeByDay'], "E_ven": self.dailyLists['ventilationEnergyByDay'], 
                                    "E_cool": self.dailyLists['coolingEnergyByDay'], "E_heat": self.dailyLists['heatingEnergyByDay'], 
                                    "E_total": self.dailyLists['totalEnergyByDay']}, columns = columnsNames)
        df.to_csv(self.energyDemandDataByDaysFolder + 'daily' + self.ED_csvFileName, sep=';',index=False)
        
    def generate_monthly_demand_csv(self):
        '''
        @summary: creates csv file containing one location energy demand by months.
        '''
        self.calculate_monthly_energy_demand()
        
        # Create hourly demand CSV
        columnsNames = ['month', 'E_ven', 'E_cool', 'E_heat', 'E_total']
        df = pandas.DataFrame(data={"month": self.monthlyLists['timeByMonth'], "E_ven": self.monthlyLists['ventilationEnergyByMonth'], 
                                    "E_cool": self.monthlyLists['coolingEnergyByMonth'], "E_heat": self.monthlyLists['heatingEnergyByMonth'], 
                                    "E_total": self.monthlyLists['totalEnergyByMonth']}, columns = columnsNames)
        df.to_csv(self.energyDemandDataByMonthsFolder + 'monthly' + self.ED_csvFileName, sep=';',index=False)
        
    def generate_monthly_demand_and_avgMinMax_temp_csv(self):
        '''
        @summary: catches energy demand and temperatures information from dictionary which contains monthly lists and creates a csv with akll information
        '''
        # Check monthly demand has already been calculated and do it if necessary
        if isinstance(self.monthlyLists['timeByMonth'], list) is False:
            self.calculate_monthly_energy_demand()
        
        # Calculate monthly average temperature only if temp file has been found
        if self.temperatureFileName is not None:
            self.calculate_monthly_averageMinMax_temperature()
        
            # Create hourly demand CSV
            columnsNames = ['month', 'E_ven', 'E_cool', 'E_heat', 'E_total', 'AvgTemp', 'MaxTemp', 'MinTemp']
            df = pandas.DataFrame(data={"month": self.monthlyLists['timeByMonth'], "E_ven": self.monthlyLists['ventilationEnergyByMonth'], 
                                        "E_cool": self.monthlyLists['coolingEnergyByMonth'], "E_heat": self.monthlyLists['heatingEnergyByMonth'], 
                                        "E_total": self.monthlyLists['totalEnergyByMonth'], "AvgTemp": self.monthlyLists['averageTempByMonth'],
                                        "MaxTemp": self.monthlyLists['maxTempByMonth'], "MinTemp": self.monthlyLists['minTempByMonth']}, columns = columnsNames)
            df.to_csv(self.energyDemandDataAndAvgTempByMonthsFolder + 'monthly' + self.ED_csvFileName, sep=';',index=False)
        
        else:
            print 'ERROR: Temperature file not found, it has not been possible to create file with monthly average temperature.'
    