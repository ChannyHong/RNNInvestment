# dateModifier.py
# Channy Hong
#
# Skips over rows without data
# For 'Everyday' implementation, adds every day
# For 'Weekdays' implementation, adds only the data for weekdays

import csv
import sys
import datetime

from dateTool import *

# Data generator according to selected parameter
def dataGenerator(currentRowData, lastRowData, rowToAdd, dayDifference, dataCalculateMode):
    if dataCalculateMode == 'Gradient':
        return lastRowData + ((currentRowData-lastRowData) * ((float(rowToAdd)+1.0)/float(dayDifference)))
    elif dataCalculateMode == 'ConstantAverage':
        return (currentRowData+lastRowData)/2
    elif dataCalculateMode == 'CarryOver':
        return lastRowData
    elif dataCalculateMode == 'LookForward':
        return currentRowData

# Gather input from the user through command prompt
inputFileName = 'indicators/' + raw_input('[Enter the input csv file name] : ')
outputFileName = 'indicators/' + raw_input('[Enter the output csv file name] : ')
dataFillMode = raw_input('[Select the dataFillMode (Everyday/Weekdays)] : ')
dataCalculateMode = raw_input('[Select the dataCalculateMode (Gradient/ConstantAverage/CarryOver/LookForward)] : ')

modifiedData = []
numColumns = None
numRows = None

# Start reading input file
with open(inputFileName, 'rb') as csvInputFile:
    reader = csv.reader(csvInputFile)
    
    firstLine = next(reader)
    numColumns = len(firstLine)
        
    secondLine = None
    
    allCorrectType = False
    while (not allCorrectType):
        secondLine = next(reader)
        incorrectPresent = False
        for columnCount in range(numColumns-1):
            if not isFloatStr(secondLine[columnCount+1]):
                incorrectPresent = True
        if not incorrectPresent:
            allCorrectType = True
    
    lastRow = secondLine

    for columnCount in range(numColumns):
        modifiedData.append([firstLine[columnCount], secondLine[columnCount]])
    
    numRows = 2
    
    # Everyday mode
    if dataFillMode == 'Everyday':
        for row in reader:
            
            # Chek for validity of all data in the row
            allCorrectType = True
            for columnCount in range(numColumns-1):
                if not isFloatStr(row[columnCount+1]):
                    allCorrectType = False
            
            if allCorrectType:
                dayDifference = getDayDifference(convertStrToYearMonthDayDate(row[0]), convertStrToYearMonthDayDate(lastRow[0]))
                
                # Consecutive case
                if dayDifference == 1:
                    for columnCount in range(numColumns):
                        modifiedData[columnCount].append(row[columnCount])
                    numRows += 1
                
                # Non-consecutive case
                elif dayDifference > 1:
                    # add the in between data
                    for rowToAdd in range(dayDifference-1):
                        # add generated date first
                        modifiedData[0].append(str(convertStrToYearMonthDayDate(lastRow[0]) + datetime.timedelta(rowToAdd+1)))
                        
                        # then add generated datapoints
                        for columnCount in range(numColumns-1):
                            modifiedData[columnCount+1].append(dataGenerator(float(row[columnCount+1]), float(lastRow[columnCount+1]), rowToAdd, dayDifference, dataCalculateMode))
                        numRows += 1
                    
                    # then add the current row
                    for columnCount in range(numColumns):
                        modifiedData[columnCount].append(row[columnCount])
                    numRows += 1
                        
                lastRow = row
        
    # Weekday mode
    elif dataFillMode == 'Weekdays':
        lastRowDay = convertStrToYearMonthDayDate(lastRow[0]).weekday()
        
        # if the first row of the data happened to be a weekend data, remove that one and try the next one
        while (lastRowDay == 5) or (lastRowDay == 6):
            lastRow = next(reader)
            
            # Chek for validity of all data in the new lastRow
            allCorrectType = True
            for columnCount in range(numColumns-1):
                if not isFloatStr(lastRow[columnCount+1]):
                    allCorrectType = False
            
            if allCorrectType:
                for columnCount in range(numColumns):
                    _ = modifiedData[columnCount].pop(len(modifiedData[columnCount])-1)
                    modifiedData[columnCount].append(lastRow[columnCount])
                    lastRowDay = convertStrToYearMonthDayDate(lastRow[0]).weekday()
            
        for row in reader:
            
            # Chek for validity of all data in the row
            allCorrectType = True
            for columnCount in range(numColumns-1):
                if not isFloatStr(row[columnCount+1]):
                    allCorrectType = False

            if allCorrectType:
                currentRowDay = convertStrToYearMonthDayDate(row[0]).weekday()
    
                # only care about the rows for weekdays
                if (currentRowDay == 0) or (currentRowDay == 1) or (currentRowDay == 2) or (currentRowDay == 3) or (currentRowDay == 4):
                    
                    numberOfWeekendsSinceLastRow = getNumberOfWeekendsInBetween(convertStrToYearMonthDayDate(row[0]), convertStrToYearMonthDayDate(lastRow[0]))
                    dayDifference = getDayDifference(convertStrToYearMonthDayDate(row[0]), convertStrToYearMonthDayDate(lastRow[0])) - (2*numberOfWeekendsSinceLastRow)
                    
                    if dayDifference == 1:
                        for columnCount in range(numColumns):
                            modifiedData[columnCount].append(row[columnCount])
                        numRows += 1
                    
                    elif dayDifference > 1:
                        # add the in between data
                        weekendBuffer = 0
                        
                        for rowToAdd in range(dayDifference-1):
                            # add generated date first (skip over weekend)
                            if (convertStrToYearMonthDayDate(lastRow[0]) + datetime.timedelta(rowToAdd+weekendBuffer+1)).weekday() == 5:
                                weekendBuffer += 2
                                
                            modifiedData[0].append(str(convertStrToYearMonthDayDate(lastRow[0]) + datetime.timedelta(rowToAdd+weekendBuffer+1)))
    
                            # then add generated datapoints
                            for columnCount in range(numColumns-1):
                                modifiedData[columnCount+1].append(dataGenerator(float(row[columnCount+1]), float(lastRow[columnCount+1]), rowToAdd, dayDifference, dataCalculateMode))
                            numRows += 1
                        
                        # then add the current row
                        for columnCount in range(numColumns):
                            modifiedData[columnCount].append(row[columnCount])
                        numRows += 1
                            
                    lastRow = row

# Create the output file
with open(outputFileName, 'wb') as csvOutputFile:
    writer = csv.writer(csvOutputFile)
    
    for rowCount in range(numRows):
        row = []
        
        for columnCount in range(numColumns):
            row.append(modifiedData[columnCount][rowCount])

        writer.writerow(row)