# dateTool.py
# Channy Hong
#
# Toolkit for date calculations

import datetime

# Function that checks whether string is a floatStr or not
def isFloatStr(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Function for getting the number of days in the month, given a year
def getNumDaysInCurrentMonth(year, month):
    if month != '02':
        if (month == '01') or (month == '03') or (month == '05') or (month == '07') or (month == '08') or (month == '10') or (month == '12'):
            return 31
        elif (month == '04') or (month == '06') or (month == '09') or (month == '11'):
            return 30
    elif month == '02':
        if (int(year)%4) != 0:
            return 28
        elif (int(year)%100) != 0:
            return 29
        elif (int(year)%400) != 0:
            return 28
        else:
            return 29
    
# Function for getting the number of days in a year
def getNumDaysInCurrentYear(year):
    if (int(year)%4) != 0:
            return 365
    elif (int(year)%100) != 0:
        return 366
    elif (int(year)%400) != 0:
        return 365
    else:
        return 366

# Date operators
def convertStrToYearMonthDayDate(dateStr):
    year, month, day = dateStr.split('-')
    return datetime.date(int(year), int(month), int(day))

def getThisWeeksMonday(currentDate):
    date = convertStrToYearMonthDayDate(currentDate)
    currentDayOfWeek = date.weekday()
    return str(date - datetime.timedelta(days=currentDayOfWeek))

def getNextMonday(weekStartDate, dayOfWeek): # Here, dayOfWeek should be 0, since it is the weekStartDate and is thus Monday
    date = convertStrToYearMonthDayDate(weekStartDate)
    return str(date + datetime.timedelta(days=7-dayOfWeek))

def getThisMonthsFirst(startDate):
    year, month, day = startDate.split('-')
    return year + '-' + month + '-01'

def getNextMonthsFirst(monthStartDate):
    year, month, _ = monthStartDate.split('-')
    numDaysInCurrentMonth = getNumDaysInCurrentMonth(year, month)
    return getThisMonthsFirst(str(convertStrToYearMonthDayDate(monthStartDate) + datetime.timedelta(days=numDaysInCurrentMonth)))

def getThisYearsFirst(startDate):
    year, month, day = startDate.split('-')
    return year + '-01-01'

def getNextYearsFirst(yearStartDate):
    year, _, _ = yearStartDate.split('-')
    numDaysInCurrentYear = getNumDaysInCurrentYear(year)
    return getThisYearsFirst(str(convertStrToYearMonthDayDate(yearStartDate) + datetime.timedelta(days=numDaysInCurrentYear)))
    
def getDayDifference(newerDate, olderDate):
    return (newerDate - olderDate).days
    
def getNumberOfWeekendsInBetween(newerDate, olderDate):
    dayDifference = getDayDifference(newerDate, olderDate)
    saturdayCount = 0
    for dayCount in range(dayDifference):
        if (olderDate + datetime.timedelta(days=dayCount+1)).weekday() == 5:
            saturdayCount += 1
    return saturdayCount