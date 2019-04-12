'''
Created on 2018/05/06

Modified on 2018/06/02

@author: Arnau Gatell
'''
# Import necessary libraries
from mpl_toolkits.basemap import Basemap
import pandas
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class mapsGenerator(object):
    '''
    classdocs
    '''

    def __init__(self, ED_csvFileNamesList):
        '''
        Constructor
        '''
        # Init variables
        self.ED_csvFileNamesList = ED_csvFileNamesList
        self.totalDemandList = []
        self.stationsData = {}
        
        # Inputs/outputs folders
        self.meteocatStationsFile = 'data/stationsData/meteocatStations.csv'
        self.energyDemandDataByMonthsFolder = 'data/energyDemandDataByMonths/'
        self.catalunyaShapeFilesFolder = 'PNGGraphs/catalunyaShapefiles/'
        self.PNGGraphsFolder = 'PNGGraphs/'
        
        # Parse meteocat stations data and total demand data
        self.parse_stations_csv_data()
                
    def parse_stations_csv_data(self):
        '''
        @summary: reads stations data csv file, creates a list for each column and saves this lists as self (global within this class) variables.
        '''
        print 'Parsing meteocat stations information file.'
        
        # Read energy demand CSV
        columnsNames = ['region', 'city', 'name', 'code', 'latitude', 'longitude', 'altitude']
        columnsDataTypes = {'region': 'string', 'city': 'string', 'name': 'string', 'code': 'string', 'latitude': 'string', 'longitude': 'string', 'altitude': 'string'}
        fileContent = pandas.read_csv(self.meteocatStationsFile, delimiter = ";", names = columnsNames, dtype = columnsDataTypes)
        
        # Save each CSV column in a list
        longitudesList = self.convert_list_string_elems_to_float(fileContent.longitude.tolist()[1:])
        latitudesList = self.convert_list_string_elems_to_float(fileContent.latitude.tolist()[1:])
        altitudeList = fileContent.altitude.tolist()[1:]
        labelsList = fileContent.city.tolist()[1:]
        codesList = fileContent.code.tolist()[1:]
        
        # Init data lists
        self.longitudesList = []
        self.latitudesList = []
        self.altitudeList = []
        self.labelsList = []
        
        # Fill data lists of the stations to plot
        elem = 0
        for stationCode in codesList:
            if any(stationCode+'_' in s for s in self.ED_csvFileNamesList):
                self.longitudesList.append(longitudesList[elem])
                self.latitudesList.append(latitudesList[elem])
                self.labelsList.append(labelsList[elem])
                
                self.parse_total_demand_csv_data('_' + stationCode + '_')
                
            elem += 1
        
    def parse_total_demand_csv_data(self, stationCode):
        '''
        @summary: reads total energy demand csv file, creates a list for each column and saves total demand list as a self (global within this class) variable.
        @param: stationCode: string containing the station code and two underscores "_XX_".
        '''
        # Iterate over the list of stations files to plots
        for stationFileName in self.ED_csvFileNamesList:
            if stationCode in stationFileName:
                stationName = stationFileName
        
        print 'Parsing monthly total energy demand csv file to plot in a map from ' + stationName + ' file.'
        
        # Read energy demand CSV
        columnsNames = ['month','E_ven','E_cool', 'E_heat', 'E_total']
        columnsDataTypes = {'month': 'string', 'E_ven': 'string', 'E_cool': 'string', 'E_heat': 'string', 'E_total': 'string'}
        fileContent = pandas.read_csv(self.energyDemandDataByMonthsFolder + 'monthly' + stationName, delimiter = ";", names = columnsNames, dtype = columnsDataTypes)
        
        # Save each CSV column in a list
        totalYearDemand = self.convert_list_string_elems_to_float(fileContent.E_total.tolist()[1:])
        timeByMonth = fileContent.month.tolist()[1:]
        
        # Divide data to plot only complete years
        listElemNum = 0
        firstMonthFound = False
        for monthName in timeByMonth:
            monthNameToFind = monthName[4:] + '-' + monthName[0:4]
            if '01-' in monthNameToFind and firstMonthFound is False:
                firstMonthToPlotElemNum = listElemNum
                firstMonthFound = True
            if '12-' in monthNameToFind:
                lastMonthToPlotElemNum = listElemNum + 1
                
            listElemNum += 1
        
        # Calculate one year demand by adding each month demand data from a list
        oneYearDemand = sum(map(float,totalYearDemand[firstMonthToPlotElemNum:lastMonthToPlotElemNum]))
        
        self.totalDemandList.append(oneYearDemand)
        
    def convert_list_string_elems_to_float(self, stringsList):
        '''
        @summary: converts all string elements in a list into float type.
        @param: stringsList: list of string elements.
        '''
        floatsList = [float(i.replace(',','.')) for i in stringsList]
        
        return floatsList

    def generate_locations_one_year_energy_demand_map(self):
        '''
        @summary: creates a map of Catalunya region and plots a marker in each location. The mark has a different size and different color
                    according to the yearly energy demand.
        '''
        fontArial = {'fontname':'Arial', 'fontsize':'12'}
        
        # Create map
        locationMap = Basemap(llcrnrlon=-0.5,llcrnrlat=39.8,urcrnrlon=4.,urcrnrlat=43.,resolution='h', projection='mill', lat_0 = 39.5, lon_0 = 1)
        
        # Prepare map
        locationMap.drawmapboundary(fill_color='#46bcec')
        locationMap.drawcoastlines()
        locationMap.fillcontinents(color='#f6b436',lake_color='#46bcec')
        locationMap.drawmapboundary()
        
        # Save two variables with longitudes and latitudes list properly sorted
        lons = self.longitudesList
        lats = self.latitudesList
        
        # Read Catalunya regions shape files
        locationMap.readshapefile(self.catalunyaShapeFilesFolder + 'catalunya_comarques', 'comarques')
        
         
        labels = self.labelsList
        x_offset = 10000
        y_offset = -4000
        
        # Prepare map markers legend
        demand1 = mpatches.Patch(color='#3F0BE5', label='demand <= 300')
        demand2 = mpatches.Patch(color='#560BC9', label='300 <= demand < 400')
        demand3 = mpatches.Patch(color='#6E0BAD', label='400 <= demand < 500')
        demand4 = mpatches.Patch(color='#860B91', label='500 <= demand < 600')
        demand5 = mpatches.Patch(color='#9D0B75', label='600 <= demand < 700')
        demand6 = mpatches.Patch(color='#B50B59', label='700 <= demand < 800')
        demand7 = mpatches.Patch(color='#CD0B3D', label='800 <= demand < 900')
        demand8 = mpatches.Patch(color='#E50B21', label='demand >= 900')
        
        # Plot map markers legend
        plt.legend(handles=[demand1,demand2,demand3,demand4,demand5,demand6,demand7,demand8],loc="lower right", prop={'family': 'Arial', 'size':8})
        
        # Plot map title
        plt.title("2017 locations energy demand [kWh]", **fontArial)
        
        # Plot location markers along the map
        for label, lon, lat, demand in zip(labels, lons, lats, self.totalDemandList):
            marker_color = ''
            marker_size = 0
            x,y = locationMap(lon, lat)
            marker_color, marker_size = self.get_marker_color_and_size(int(demand))
            locationMap.plot(x, y, marker='o', color=marker_color, markersize=marker_size)
        
        # Save a file only with locations markers as a .png
        plt.savefig(self.PNGGraphsFolder + '2017locationsEnergyDemandNoLabels', dpi = 400, bbox_inches='tight')
        
        # Plot location labels next to markers along the map
        for label, lon, lat, demand in zip(labels, lons, lats, self.totalDemandList):
            x,y = locationMap(lon, lat)
            stationText = plt.text(x+x_offset, y+y_offset, label+'\n'+str(int(demand))+' kWh', fontsize=4)
            stationText.set_bbox(dict(facecolor='white', alpha=0.8, edgecolor='white'))
        
        # Save a file both with locations markers and labels as a .png
        plt.savefig(self.PNGGraphsFolder + '2017locationsEnergyDemand', dpi = 400, bbox_inches='tight')
        
        # Clear saved figure to avoid next figure overwriting problems
        plt.clf()
    
    def get_marker_color_and_size(self, demand):
        '''
        @summary: calculates the color and size of the map mark depending on the yearly energy consumption.
        @param: demand: float value of a station energy demand in a year.
        '''
        if demand <= 300:
            marker_color = '#3F0BE5'
            marker_size = 4
        elif 300 <= demand < 400:
            marker_color = '#560BC9'
            marker_size = 5
        elif 400 <= demand < 500:
            marker_color = '#6E0BAD'
            marker_size = 6
        elif 500 <= demand < 600:
            marker_color = '#860B91'
            marker_size = 7
        elif 600 <= demand < 700:
            marker_color = '#9D0B75'
            marker_size = 8
        elif 700 <= demand < 800:
            marker_color = '#B50B59'
            marker_size = 9
        elif 800 <= demand < 900:
            marker_color = '#CD0B3D'
            marker_size = 10
        elif demand >= 900:
            marker_color = '#E50B21'
            marker_size = 11
        
        return marker_color, marker_size
        