'''
Created on 2018/04/03

Modified on 2018/05/29

@author: Arnau Gatell
'''
# Import necessary libraries
import os
import requests
import csv
import datetime
import unicodedata
import time
from bs4 import BeautifulSoup
from collections import deque
    

class station(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.region = ""
        self.city = ""
        self.name = ""
        self.code = ""
        self.latitude = ""
        self.longitude = ""
        self.altitude = ""
        self.tempData = {}


class dayData(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.day = ""
        self.month = ""
        self.year = ""
        self.tempByHourDict = {}
    
        
class HTMLParserAndCSVGenerator(object):
    '''
    classdocs
    '''

    def __init__(self, url):
        '''
        Constructor
        '''
        self.stationsListurl = url
        self.stationsList = [] # List of station objects
        self.now = datetime.datetime.now()
        
        # Inputs/outputs folders
        self.stationsDataFolder = 'data/stationsData/'
        self.temperaturesDataFolder = 'data/temperaturesData/'
        
        
    def init_stations_list(self):
        '''
        @summary: fills the meteo stations dictionary with as many keys as stations.
                    Each dictionary key is the station name and its content a station object containing all station information
        '''
        self.stationsListHtml = self.get_url_html(self.stationsListurl)
        if self.stationsListHtml is not None:
            self.stationsListSoup = self.create_soup(self.stationsListHtml)
            operativeStationsNum = self.get_operative_stations_number()
            if operativeStationsNum != 0:
                currentStationNum = 0
                while currentStationNum < operativeStationsNum:
                    self.stationsList.append(station())
                    currentStationNum += 1
                
            else:
                print('There are no operative weather stations available.')
            
        else:
            print (str(self.stationsListurl) + " not available.")
    
    
    def fill_stations_list(self):
        '''
        @summary: fills the content within every station object in the stations dict.
        '''
        stationNum = 0
        station = self.stationsListSoup.tbody.find('td', string="Operativa").parent
        
        while stationNum < len(self.stationsList):
            
            stationRegion = station.find('td')
            stationCity = stationRegion.next_sibling.next_sibling
            stationName = stationCity.next_sibling.next_sibling.find('a')
            stationLatitude = stationName.parent.next_sibling.next_sibling
            stationLongitude = stationLatitude.next_sibling.next_sibling
            stationAltitude = stationLongitude.next_sibling.next_sibling
            stationCode = stationName.string[-3:-1]
            
            self.stationsList[stationNum].region = self.remove_accent(stationRegion.string)
            self.stationsList[stationNum].city = self.remove_accent(stationCity.string)
            self.stationsList[stationNum].name = self.remove_accent(stationName.string).replace(" ", "")[:-4]
            self.stationsList[stationNum].code = stationCode
            self.stationsList[stationNum].latitude = stationLatitude.string
            self.stationsList[stationNum].longitude = stationLongitude.string
            self.stationsList[stationNum].altitude = stationAltitude.string
            
            stationNum += 1
            if stationNum == len(self.stationsList):
                break
            
            station = station.next_sibling.next_sibling
            while station.find('td', string='Operativa') is None:
                station = station.next_sibling.next_sibling
        
        self.generate_stationsList_csv()
    
    
    def remove_accent(self, stringToConvert):
        '''
        @summary: accepts a unicode string, and return a normal string without any accent marks.
        @param: stringToConvert: string to remove its accents.
        '''
        return unicodedata.normalize('NFKD', stringToConvert).encode('ASCII', 'ignore')

    
    def generate_stationsList_csv(self):
        '''
        @summary: creates a csv file and fills it with self.stationsList stations information.
        '''
        with open(self.stationsDataFolder + 'meteocatStations.csv', 'w+') as csvFile:
            writer = csv.writer(csvFile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            
            writer.writerow(['region', 'city', 'name', 'code', 'latitude', 'longitude', 'altitude(m)'])
            
            for station in self.stationsList:
                writer.writerow([str(station.region), str(station.city), str(station.name), str(station.code), str(station.latitude), str(station.longitude), str(station.altitude)])
        
        csvFile.close()
        
    
    def fill_stations_temperature_data (self):
        '''
        @summary: fills the tempData dictionary of a station object.
                    Each dictionary key is the iterationDate and its content a dayData object.
        '''
        iterationDate, iterYear, iterMonth, iterDay, firstIterationDate, currentDate = self.set_current_and_min_date()
        lastIterationDate = None
        
        # Loop to get all temperature data from two years ago till now
        while (int(iterationDate) <= int(currentDate)):
            urlIterationDate = iterYear+"-"+iterMonth+"-"+iterDay
            
            # Loop to get temperature data for each station
            for station in self.stationsList:
                existingFile, modifyFile, time, firstRegisterDateInCsv, currentCsvName, newCsvName = self.check_if_file_exists_before_append_data(iterationDate, station)
                print iterationDate, station.code, station.name, time
                
                # Request to the server temperature information only if necessary. If it is already in the temperature data csv file it will not be requested.
                if (existingFile is False) or (existingFile is True and modifyFile is True):
                    noDataInUrl = False
                    stationDayDataHtml = self.get_url_html("http://www.meteo.cat/observacions/xema/dades?codi="+str(station.code)+"&dia="+urlIterationDate+"T00:00Z")
                    
                    timerToGetHtml = 0
                    while stationDayDataHtml is None and timerToGetHtml < 20:
                        stationDayDataHtml = self.get_url_html("http://www.meteo.cat/observacions/xema/dades?codi="+str(station.code)+"&dia="+urlIterationDate+"T00:00Z")
                        timerToGetHtml += 1
                        
                    if stationDayDataHtml is not None:
                        stationDayDataSoup = self.create_soup(stationDayDataHtml)
                         
                        station.tempData[iterationDate] = dayData()
                        station.tempData[iterationDate].day = iterDay
                        station.tempData[iterationDate].month = iterMonth
                        station.tempData[iterationDate].year = iterYear
                         
                        numberTempRegisters = 48
                        currentTempRegister = 1
                        currentdayregistersAvgTemperature = 0
                         
                        while(currentTempRegister <= numberTempRegisters):
                            currentRegisterHour = self.calculate_current_register_hour(currentTempRegister)
                             
                            try:
                                stationHalfHourTempHour = str(stationDayDataSoup.find("table", class_="tblperiode").find_all("tr")[currentTempRegister].th.string).strip().replace(' ', '')[:5]
                                if stationHalfHourTempHour != currentRegisterHour:
                                    raise IndexError
                                
                                stationHalfHourTempData = str(stationDayDataSoup.find("table", class_="tblperiode").find_all("tr")[currentTempRegister].find('td').string.split('.')[0])
                                if 's/d' in stationHalfHourTempData:
                                    raise ValueError
                                
                            except IndexError:
                                stationHalfHourTempHour = currentRegisterHour
                                stationHalfHourTempData = int(currentdayregistersAvgTemperature)
                            except ValueError:
                                stationHalfHourTempData = int(currentdayregistersAvgTemperature)
                            except AttributeError:
                                print 'WARNING: NO DATA on ' + "http://www.meteo.cat/observacions/xema/dades?codi="+str(station.code)+"&dia="+urlIterationDate+"T00:00Z"
                                noDataInUrl = True
                                if existingFile is True and lastIterationDate is not None and modifyFile is True:
                                    station.tempData[iterationDate].tempByHourDict = station.tempData[lastIterationDate].tempByHourDict
                                break
                                 
                            print stationHalfHourTempHour, stationHalfHourTempData
                            station.tempData[iterationDate].tempByHourDict[stationHalfHourTempHour] = stationHalfHourTempData
                             
                            currentdayregistersAvgTemperature = ((currentdayregistersAvgTemperature*(currentTempRegister-1)) + int(stationHalfHourTempData)) / float(currentTempRegister)
                             
                            currentTempRegister += 1
                    
                    else:
                        noDataInUrl = True
                        if existingFile is True and lastIterationDate is not None and modifyFile is True:
                            station.tempData[iterationDate] = dayData()
                            station.tempData[iterationDate].day = iterDay
                            station.tempData[iterationDate].month = iterMonth
                            station.tempData[iterationDate].year = iterYear
                            
                            station.tempData[iterationDate].tempByHourDict = station.tempData[lastIterationDate].tempByHourDict
                        print "WARNING: " + str(station.name) + " day " + iterationDate + " is not available."
                    
                        
                    if existingFile is True and modifyFile is True:
                        os.rename(self.temperaturesDataFolder + currentCsvName, self.temperaturesDataFolder + newCsvName)
                        self.append_dayStationTempRegister_to_csv(station, firstRegisterDateInCsv, iterationDate, existingFile, time) 
                    elif existingFile is False and noDataInUrl is True:
                        pass
                    elif existingFile is False and noDataInUrl is False:
                        self.append_dayStationTempRegister_to_csv(station, iterationDate, iterationDate, existingFile, time)
                      
                else:
                    pass
            
            lastIterationDate = iterationDate    
            iterDay, iterMonth, iterYear = self.refresh_iterDate(iterDay, iterMonth, iterYear)
            iterationDate = iterYear + iterMonth + iterDay
    
    def calculate_current_register_hour(self, currentTempRegister):
        '''
        @summary: calculates the hour that corresponds to the register number in the table of temperatures. Thanks to this, it is ensured that data is properly collected.
        @param: currentTempRegister: integer containing current temperature register number. Each day has 48 registers of temperature (every half hour).
        '''
        if currentTempRegister % 2 == 0:
            currentRegisterHour = str((currentTempRegister-1)/2) + ':30'
        else:
            currentRegisterHour = str((currentTempRegister-1)/2) + ':00'
         
        if len(currentRegisterHour) < 5:
            currentRegisterHour = '0' + currentRegisterHour
            
        return currentRegisterHour
    
    def set_current_and_min_date(self):
        '''
        @summary: sets the current date and the maximum date in order to specify the date range of temperatures data.
        '''
        minYearRegistered = int(self.now.year) - 2
        iterDay = self.add_zeroes_to_date(str(self.now.day))
        iterMonth = self.add_zeroes_to_date(str(self.now.month))
        iterYear = str(minYearRegistered)
        iterationDate = iterYear + iterMonth + iterDay
        firstIterationDate = iterationDate
        maxDay = self.add_zeroes_to_date(str(int(self.now.day)-1))
        maxMonth = self.add_zeroes_to_date(str(self.now.month))
        maxYear = str(int(self.now.year))
        maxDate = maxYear + maxMonth + maxDay
        
        return iterationDate, iterYear, iterMonth, iterDay, firstIterationDate, maxDate
        
    def add_zeroes_to_date(self, number):
        '''
        @summary: adds a zero to numbers of one only one character.
        @param: number: string containing a number character or characters.
        '''
        if len(number) < 2:
            number = '0' + number
        else:
            pass
        
        return number      
                
    def append_dayStationTempRegister_to_csv(self, station, firstRegisterDate, lastRegisterDate, existingFile, time):
        '''
        @summary: creates a csv file for a station data and fills it with time in seconds and temperature in degrees celsius of the station during a specified period.
                    Sorts the tempData dictionary of the station object by the date and fills the time in seconds beginning the counter in the first register and adding
                    the time passed in seconds between each temperature register. In this case, temperatures registers are every half hour, so between each register 1800
                    seconds are added.
        @param: station: station object.
        @param: firstRegisterDate: date of the first temperature register in format yyyymmdd.
        @param: lastRegisterDate: date of the last temperature register in format yyyymmdd.
        @param: existingFile: boolean that is True if a file exists and False if not.
        @param: time: in case the file exists it is the time of the last registered time with the seconds of the current iteration already added (+1800 seconds).
        '''
        # Open or create csv file
        with open(self.temperaturesDataFolder + station.code + '_' + station.name + '_' + firstRegisterDate + '-' + lastRegisterDate + '.csv', 'a+') as csvFile:
            writer = csv.writer(csvFile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            
            # Write column titles only if file does not exist previously
            if existingFile is False:
                writer.writerow(['t', 'temp', 'date', 'hour'])
            
            # Sort one day temperature registers by hour before writing them to the csv file
            orderedByHoursKeysList = sorted(station.tempData[lastRegisterDate].tempByHourDict)
            # Loop to write all temperature registers of a day
            for halfHour in orderedByHoursKeysList:
                halfHourTempData = station.tempData[lastRegisterDate].tempByHourDict[halfHour]
                writer.writerow([str(time), str(halfHourTempData), str(lastRegisterDate), str(halfHour)])
                time += 1800
        
        # Close csv file
        csvFile.close()           
    
    def check_if_file_exists_before_append_data(self, iterationDate, station):
        '''
        @summary: checks if file exists before appending or creating new data file. If file exists, it collects its last time register.
        @param: iterationDate: yyyymmdd format date.
        @param: station: station object.
        '''
        # Init some variables
        time = 0
        existingFile = False
        modifyFile = False
        firstRegisterDateInCsv = None
        oldName = None
        newName = None
        
        # Create a list of all files within the temperatures data folder and set the station name to look for
        existingFileNamesList = os.listdir(self.temperaturesDataFolder)
        fileNameToLookFor = station.code + '_' + station.name + '_'
        
        # Loop to find the station filename in all filenames list
        for fileName in existingFileNamesList:
            if fileNameToLookFor in fileName:
                existingFile = True
                firstRegisterDateInCsv = fileName[-21:-13]
                lastRegisterDateInCsv = fileName[-12:-4]
                # Get last register time in seconds if file exists and has to be modified
                if int(iterationDate) > int(lastRegisterDateInCsv):
                    modifyFile = True
                    oldName = fileName
                    newName = fileName[:-12] + iterationDate + '.csv'
                    fileContent = open(self.temperaturesDataFolder + oldName, 'r')
                    reader = csv.reader(fileContent, delimiter = ";")
                    lastRegisteredTimeInCsv = int(deque(reader, 1)[0][0])
                    time = lastRegisteredTimeInCsv + 1800
                    fileContent.close()
                else:
                    modifyFile = False
                break
            else:
                pass
        
        return existingFile, modifyFile, time, firstRegisterDateInCsv, oldName, newName
    
    def refresh_iterDate(self, iterDay, iterMonth, iterYear):
        '''
        @summary: refreshes the date of the iteration with the immediately following day. Calculations consider each month quantity of days.
        @param: iterDay: current iteration day.
        @param: iterMonth: current iteration month.
        @param: iterYear: current iteration year.
        '''
        if int(iterMonth) == 1 or int(iterMonth) == 3 or int(iterMonth) == 5 or int(iterMonth) == 7 or int(iterMonth) == 8 or int(iterMonth) == 10:
            if int(iterDay) == 31:
                iterDay = "01"
                iterMonth = self.add_zeroes_to_date(str(int(iterMonth)+1))
            else:
                iterDay = self.add_zeroes_to_date(str(int(iterDay)+1))
            
        elif int(iterMonth) == 2:
            if int(iterDay) == 28:
                iterDay = "01"
                iterMonth = self.add_zeroes_to_date(str(int(iterMonth)+1))
            else:
                iterDay = self.add_zeroes_to_date(str(int(iterDay)+1))
            
        elif int(iterMonth) == 4 or int(iterMonth) == 6 or int(iterMonth) == 9 or int(iterMonth) == 11:
            if int(iterDay) == 30:
                iterDay = "01"
                iterMonth = self.add_zeroes_to_date(str(int(iterMonth)+1))
            else:
                iterDay = self.add_zeroes_to_date(str(int(iterDay)+1))
        
        elif int(iterMonth) == 12:
            if int(iterDay) == 31:
                iterDay = "01"
                iterMonth = "01"
                iterYear = str(int(iterYear)+1)
            else:
                iterDay = self.add_zeroes_to_date(str(int(iterDay)+1))
        
        return iterDay, iterMonth, iterYear
    
    def get_url_html (self, url):
        '''
        @summary: gets the whole url webpage html source code.
        @param: url: url address of the webpage to get the html source code.
        '''
        try:
            webHtml = requests.get(url, headers={'Connection': 'close'}, timeout = 5).text
        except:
            time.sleep(8)
            webHtml = requests.get(url, headers={'Connection': 'close'}).text
        
        if webHtml:
            return webHtml
        else:
            return None
    
    def create_soup (self, webHtml):
        '''
        @summary: creates the soup from the html text.
        @param: webHtml: HTML file.
        '''
        return BeautifulSoup(webHtml, 'html.parser')
    
    def get_operative_stations_number (self):
        '''
        @summary: finds and returns the number of operative weather stations within the html file.
        '''
        operativeStationsNum = len(self.stationsListSoup.tbody.find_all('td', string="Operativa"))
        
        return operativeStationsNum
    