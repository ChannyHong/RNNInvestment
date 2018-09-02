# dateCoordinator.py
# Channy Hong
#
# This program coordinates multiple by-date-data csv files into one csv file.
# It only adds data for a date where the date is present in all data columns to get.
# It skips over any non-numerical data point (such as 'none')

import csv
import sys

from dateTool import *

# Function for checking if number is even
def isEven(number):
    return number % 2 == 0

# Configures data according to wanted type; returns None if the dataList is empty
def configureData (dataList, type):
    if len(dataList) == 0:
        return None
    else:
        if type == 'Average':
            return sum(dataList) / len(dataList)
        if type == 'Start':
            return dataList[0]
        if type == 'End':
            return dataList[len(dataList)-1]
        if type == 'Median':
            if isEven(len(dataList)):
                return (dataList[len(dataList)-1] + dataList[len(dataList)]) / 2
            else:
                return dataList[len(dataList)/2]
        else:
            print("Error: Wrong type!")

# Listen for data coordination configurations from the user
outputFileName = raw_input('[Enter the output csv file name] : ')
startDate = raw_input('[Enter the start date in the form of YYYY-MM-DD] : ')
endDate = raw_input('[Enter the end date in the form of YYYY-MM-DD] : ')    #ADD WRONG DATE ENTRY ERROR HANDLER
numData = int(raw_input('[Enter the number of data to coordinate] : '))    #ADD WRONG DATE ENTRY ERROR HANDLER
interval = raw_input('[Enter the interval to compute (Daily/Weekly/Monthly/Yearly)] : ')
type = raw_input('[Enter the type to compute (Average/Start/End/Median)] : ')

# Storage of data names for later use (for output file)
topRow = ['Date']

# Read data into the rawData table
rawData = [] # where to load all non-universal-entry-filtered lists
for dataNum in range(numData): 
    rawInputPrompt = '[Enter the filename for data ' + str(dataNum+1) + '] : '
    fileNameRaw = raw_input(rawInputPrompt)
    fileName = 'indicators/' + fileNameRaw
    columnName = raw_input('[Enter column to choose data from] : ')
    
    topRow.append(fileNameRaw + '(' + columnName + ')')
    
    with open(fileName, 'rb') as csvInputFile:
        reader = csv.reader(csvInputFile)
        
        firstLine = next(reader)
        columnToGet = None
        rawData.append([])
        
        for columnCount in range(len(firstLine)):
            if (firstLine[columnCount] == columnName) :
                columnToGet = columnCount
        
        # Daily mode
        if (interval == 'Daily'):
            for row in reader:
                if ((startDate <= row[0]) and (row[0] <= endDate) and (isFloatStr(row[columnToGet]))): # only add to rawData table if is in the date range
                    rawData[dataNum].append([row[0],row[columnToGet]])
        
        # Weekly mode
        if (interval == 'Weekly'):
            weekData = []
            
            # Get first line of the data and update startDate to first date in the data file to avoid date mess
            secondLine = next(reader)
            if secondLine[0] > startDate:
                startDate = secondLine[0]
            
            # Calculate current week's Monday and next Monday
            weekStartDate = getThisWeeksMonday(startDate)
            nextMonday = getNextMonday(weekStartDate, 0)
            
            # Add datapoint to weekData . Do not need to care whether at the start or the end of the time interval (since at least one value needed per time interval anyways)
            if ((startDate <= secondLine[0]) and (secondLine[0] <= endDate) and (isFloatStr(secondLine[columnToGet]))):
                weekData.append(float(secondLine[columnToGet]))
            
            # Add rest of the data to rawData
            for row in reader:
                if ((row[0] >= nextMonday) or (row[0] > endDate)):
                    configuredData = configureData(weekData, type)
                    if (configuredData != None):
                        rawData[dataNum].append([weekStartDate, str(configuredData)])
                    weekStartDate = nextMonday
                    nextMonday = getNextMonday(weekStartDate, 0)
                    weekData = []
                if ((startDate <= row[0]) and (row[0] <= endDate) and (isFloatStr(row[columnToGet]))):
                    weekData.append(float(row[columnToGet]))
        
        # Monthly mode (refer to parallel comments in Weekly mode section)
        if (interval == 'Monthly'):
            monthData = []
            secondLine = next(reader)
            if secondLine[0] > startDate:
                startDate = secondLine[0]
            monthStartDate = getThisMonthsFirst(startDate)
            nextMonthsFirst = getNextMonthsFirst(monthStartDate)
            if ((startDate <= secondLine[0]) and (secondLine[0] <= endDate) and (isFloatStr(secondLine[columnToGet]))):
                monthData.append(float(secondLine[columnToGet]))
            for row in reader:
                if ((row[0] >= nextMonthsFirst) or (row[0] > endDate)):
                    configuredData = configureData(monthData, type)
                    if (configuredData != None):
                        rawData[dataNum].append([monthStartDate, str(configuredData)])
                    monthStartDate = nextMonthsFirst
                    nextMonthsFirst = getNextMonthsFirst(monthStartDate)
                    monthData = []
                if ((startDate <= row[0]) and (row[0] <= endDate) and (isFloatStr(row[columnToGet]))):
                    monthData.append(float(row[columnToGet]))
                
        # Yearly mode (refer to parallel comments in Weekly mode section)
        if (interval == 'Yearly'):
            yearData = []
            secondLine = next(reader)
            if secondLine[0] > startDate:
                startDate = secondLine[0]
            yearStartDate = getThisYearsFirst(startDate)
            nextYearsFirst = getNextYearsFirst(yearStartDate)
            if ((startDate <= secondLine[0]) and (secondLine[0] <= endDate) and (isFloatStr(secondLine[columnToGet]))):
                yearData.append(float(secondLine[columnToGet]))
            for row in reader:
                if ((row[0] >= nextYearsFirst) or (row[0] > endDate)):
                    configuredData = configureData(yearData, type)
                    if (configuredData != None):
                        rawData[dataNum].append([yearStartDate, str(configuredData)])
                    yearStartDate = nextYearsFirst
                    nextYearsFirst = getNextYearsFirst(yearStartDate)
                    yearData = []
                if ((startDate <= row[0]) and (row[0] <= endDate) and (isFloatStr(row[columnToGet]))):
                    yearData.append(float(row[columnToGet]))
        
# Create an output file and write to it using parallel problem solving
outputFileDirecotry = 'coordinatedData/' + outputFileName
with open(outputFileDirecotry, 'wb') as csvOutputFile:
    writer = csv.writer(csvOutputFile)
    
    # Write each data name at the very top
    writer.writerow(topRow)
    
    done = False
    
    columnCounterList = []
    columnDoneList = []
    for dataNum in range(numData):
        columnCounterList.append(0)
        columnDoneList.append(False)
        
    while not done:
        currentMaxDate = 0
        
        # First, check whether columns have reached their end and what the current maximum date is
        for dataNum in range(numData):
            if ((columnCounterList[dataNum]+1) == len(rawData[dataNum])):
                columnDoneList[dataNum] = True
            
            if (currentMaxDate < rawData[dataNum][columnCounterList[dataNum]][0]):
                currentMaxDate = rawData[dataNum][columnCounterList[dataNum]][0]
                
        # Then check whether if success (as in all numbers are the same)
        successCase = True
        for dataNum in range(numData):
            if (rawData[dataNum][columnCounterList[dataNum]][0] < currentMaxDate): #smaller than max date case
                if (columnDoneList[dataNum] == True): #check if done here
                    sys.exit()
                successCase = False
                columnCounterList[dataNum] += 1
                
            if (rawData[dataNum][columnCounterList[dataNum]][0] > currentMaxDate):
                print("something went terribly wrong!\n")
        
        # If success case, then write it to the output file
        if successCase:
            row = [currentMaxDate]
            for dataNum in range(numData):
                row.append(rawData[dataNum][columnCounterList[dataNum]][1])
                columnCounterList[dataNum] += 1
            writer.writerow(row)
            
            # Check if done here as well
            for dataNum in range(numData):
                if (columnDoneList[dataNum] == True):
                    done = True
        
# Exit program when done
sys.exit()
        
        
