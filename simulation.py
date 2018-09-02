# dateCoordinator.py
# Channy Hong
#
# Runs the simulation using RNN with LSTM cells. Supports day to day simulation while sanity checking for each simulation day as well (twofold simulation with N^2 simulation days). 


import csv
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Process data from the csv file
csvFileName = input('[Enter the coordinatedData csv file name] : ')
originalData = np.loadtxt('coordinatedData/' + csvFileName, delimiter = ',', dtype='str', skiprows=1)

# Gather parameter values from the user through command prompt 
simulationStartDate = input('[Enter the simulation start date (xxxx-xx-xx)] : ')
startCashAmount = float(input('[Enter the simulation start cash amount in] : '))
sessionRunSize = int(input('[Enter the number of times to run the training session (i.e. 2000)] : '))

trainingRatioType = input('[Enter the training ratio type (Percentage/TestingDuration/Date)] : ')

trainingPercentage = None
testingDuration = None
trainingDate = None
if trainingRatioType == 'Percentage':
    trainingPercentage = float(input('[Enter the training percentage (i.e. 0.7)] : '))
elif trainingRatioType == 'TestingDuration':
    testingDuration = int(input('[Enter the testing duration (# days)] : '))
elif trainingRatioType == 'Date':
    trainingEndDate = input('[Enter the fixed training end date (xxxx-xx-xx)] : ')

sequenceLength = int(input('[Enter the sequence length] : '))
dataDim = int(input('[Enter the data dimension (number of columns in coordinatedData)] : '))

sequence_length = sequenceLength
data_dim = dataDim

output_dim = 1
hidden_dim = 10
learning_rate = 0.01

rowCounter = 0
while (originalData[rowCounter][0] != simulationStartDate):
    rowCounter += 1
    
simulationStartDateRow = rowCounter 

totalSimulationDuration = len(originalData) - simulationStartDateRow + 1




# Start writing the result csv file
outputFileName = 'simulationResults/' + input('[Enter the simulation output csv file name] : ')
with open(outputFileName, 'w') as csvOutputFile:
    writer = csv.writer(csvOutputFile)

    # Write preliminary information to the result
    writer.writerow(['Coordinated Data Filename : ' + str(csvFileName)])
    writer.writerow(['Data Dimension : ' + str(dataDim)])
    writer.writerow(['Original Data Length : ' + str(len(originalData))])
    
    writer.writerow([])
    
    writer.writerow(['Sequence Length : ' + str(sequenceLength)])
    writer.writerow(['Session Run Size : ' + str(sessionRunSize)])
    
    writer.writerow([])
    
    writer.writerow(['Simulation Start Date : ' + str(simulationStartDate)])
    writer.writerow(['Start Cash Amount : ' + str(startCashAmount)])
    
    writer.writerow([])
    
    if trainingRatioType == 'Percentage':
        writer.writerow(['Training Percentage : ' + str(trainingPercentage)])
    elif trainingRatioType == 'TestingDuration':
        writer.writerow(['Testing Duration : ' + str(testingDuration)])
    elif trainingRatioType == 'Date':
        writer.writerow(['Training End Date : ' + str(trainingEndDate)])
        
    writer.writerow([])
    writer.writerow([])
    writer.writerow([])
    
    # Define the variables for the real simulation
    realCash = startCashAmount
    realNumberOfStock = 0
    realNetValue = None
    realCurrentStatus = "empty" # as opposed to "full"
    
    realTrueCount = 0.0
    realFalseCount = 0.0
    
    realNetValueList = []
    
    previousRealPredictComp = ''
    realTrueCount = 0.0
    realFalseCount = 0.0
    previousRealUpDownCorrectRate = 0.0
    
    
    
    
    # Run each simulation day
    for simulationDay in range(totalSimulationDuration):
        
        rawTemp = originalData[0:simulationStartDateRow + simulationDay, 1:] #skip the first column (which is dates)
        raw = rawTemp.astype(float)

        train_size = None
        if trainingRatioType == 'Percentage':
            train_size = int(len(raw) * trainingPercentage)
        elif trainingRatioType == 'TestingDuration':
            train_size = len(raw) - testingDuration
        elif trainingRatioType == 'Date':
            trainingRowCounter = 0
            while (raw[trainingRowCounter][0] != trainingEndDate):
                trainingRowCounter += 1
            train_size = trainingRowCounter + 1
    
        # Normalize the big difference between min and max for some input over others (as in standardize all inputs)
        scaler = MinMaxScaler()
        xy = scaler.fit_transform(raw)
        
        x = xy
        y = xy[:, [-1]] # this attaches the last element as label
        
        data_X = []
        data_Y = []
        
        for i in range(0, len(y)-sequence_length):
            _x = x[i:i + sequence_length] # inclusive:exclusive
            _y = y[i + sequence_length] 
            
            data_X.append(_x)
            data_Y.append(_y)
        
        finalInput = np.array([x[len(y)-sequence_length:len(y)]])
            
        train_X, test_X = np.array(data_X[0:train_size]), np.array(data_X[train_size:len(data_X)])
        train_Y, test_Y = np.array(data_Y[0:train_size]), np.array(data_Y[train_size:len(data_Y)])
        
        testDataRawPosition = train_size + sequence_length
        
        # Define the necessary LSTM components
        X = tf.placeholder(tf.float32, [None, sequence_length, data_dim])
        Y = tf.placeholder(tf.float32, [None, 1])
        
        cell = tf.contrib.rnn.BasicLSTMCell(num_units = hidden_dim, state_is_tuple = True)
        
        outputs, _states = tf.nn.dynamic_rnn(cell, X, dtype=tf.float32)
        
        Y_prediction = tf.contrib.layers.fully_connected(outputs[:, -1], output_dim, activation_fn=None) # we use the last cell's output's last value ('Close') as Y Prediction
        nextEstimate_prediction = tf.contrib.layers.fully_connected(outputs[:, -1], output_dim, activation_fn=None) # TEST: a copy of Y_prediction... maybe not necessary and can just use Y Prediction...
        
        loss = tf.reduce_sum(tf.square(Y_prediction - Y))
        
        optimizer = tf.train.AdamOptimizer(learning_rate)
        train = optimizer.minimize(loss)
    
    
         
        # Train and test
        sess = tf.Session()
        sess.run(tf.global_variables_initializer())
        
        for i in range(sessionRunSize): #this is the real training...
            _, l = sess.run([train, loss], feed_dict={X:train_X, Y:train_Y})

        # Prediction values
        testPredict = sess.run(Y_prediction, feed_dict={X: test_X})
        
        # Plug in the finalInput to the model to get the nextEstimate
        nextEstimate = sess.run(Y_prediction, feed_dict={X: finalInput})
        
        
        
        
        # Now, testing the validity of this simulation day before we make the actual estimate, as sanity check!
        cash = startCashAmount
        numberOfStock = 0
        netValue = None
        currentStatus = "empty" # as opposed to "full"

        trueCount = 0.0
        falseCount = 0.0
        
        netValueList = []
    
        # Run the simulation of the simulation (sanity check second tier simulation)
        for i in range(len(test_Y)-1):
            
            decision = None
            if currentStatus == "empty":
                if testPredict[i+1] > testPredict[i]: #This is with current time as 'i' and 'i+1' is the +1 lookahead date of estimate
                    decision = "buy"
                elif testPredict[i+1] <= testPredict[i]:
                    decision = "hold"
            elif currentStatus == "full":
                if testPredict[i+1] > testPredict[i]:
                    decision = "hold"
                elif testPredict[i+1] <= testPredict[i]:
                    decision = "sell"
                    
            if decision == "buy":
                numberToBuy = int(cash/raw[testDataRawPosition+i][-1])
                numberOfStock += numberToBuy
                cash -= raw[testDataRawPosition+i][-1] * numberToBuy
                currentStatus = "full"
                    
            elif decision == "sell":
                numberToSell = numberOfStock
                cash += raw[testDataRawPosition+i][-1] * numberToSell
                numberOfStock -= numberToSell
                currentStatus = "empty"
            
            netValue = cash + (numberOfStock * raw[testDataRawPosition+i][-1])
    
            GTComp = ''
            PredictComp = ''
            if test_Y[i+1] > test_Y[i]:
                GTComp = 'Up'
            elif test_Y[i+1] < test_Y[i]:
                GTComp = 'Down'
            if testPredict[i+1] > testPredict[i]:
                PredictComp = 'Up'
            elif testPredict[i+1] < testPredict[i]:
                PredictComp = 'Down'
                
            if GTComp==PredictComp:
                trueCount += 1.0
            elif GTComp!=PredictComp:
                falseCount += 1.0
            
            netValueList.append(netValue)
    
        # Finalizing the simulation of the simulation data
        upDownCorrectRate = 100.0 * trueCount/(trueCount+falseCount)
        netValueAverage = sum(netValueList) / len(netValueList)
        
        
        
        # Now, calculate the first tier simulation data
        realDecision = None
        
        if realCurrentStatus == "empty":
            if nextEstimate[0] > testPredict[len(test_Y)-1]:
                realDecision = "buy"
            elif nextEstimate[0] <= testPredict[len(test_Y)-1]:
                realDecision = "hold"
        elif realCurrentStatus == "full":
            if nextEstimate[0] > testPredict[len(test_Y)-1]:
                realDecision = "hold"
            elif nextEstimate[0] <= testPredict[len(test_Y)-1]:
                realDecision = "sell"
        
        if realDecision == "buy":
            realNumberToBuy = int(realCash/raw[testDataRawPosition+len(test_Y)-1][-1])
            realNumberOfStock += realNumberToBuy
            realCash -= raw[testDataRawPosition+len(test_Y)-1][-1] * realNumberToBuy
            realCurrentStatus = "full"
                
        elif realDecision == "sell":
            realNumberToSell = realNumberOfStock
            realCash += raw[testDataRawPosition+len(test_Y)-1][-1] * realNumberToSell
            realNumberOfStock -= realNumberToSell
            realCurrentStatus = "empty"
        
        realNetValue = realCash + (realNumberOfStock * raw[testDataRawPosition+len(test_Y)-1][-1])


        # Note: Unlike the second tier simulation, here we are checking the up/down correctness of previous simulation day's prediction (since we cannot see into the future)
        previousRealComp = ''
        if test_Y[len(test_Y)-1] > test_Y[len(test_Y)-2]:
            previousRealComp = 'Up'
        elif test_Y[len(test_Y)-1] <= test_Y[len(test_Y)-2]:
            previousRealComp = 'Down'

        realPredictComp = ''
        if nextEstimate[0] > testPredict[len(test_Y)-1]:
            realPredictComp = 'Up'
        elif nextEstimate[0] < testPredict[len(test_Y)-1]:
            realPredictComp = 'Down'
        
        if previousRealPredictComp != '': # skip if it is the first time and there hasn't been a previous prediction comparison
            if previousRealComp == previousRealPredictComp:
                realTrueCount += 1.0
            elif previousRealComp != previousRealPredictComp:
                realFalseCount += 1.0

            previousRealUpDownCorrectRate = 100.0 * realTrueCount/(realTrueCount+realFalseCount)
            
        previousRealPredictComp = realPredictComp

        realNetValueList.append(realNetValue)
        
        realNetValueAverage = sum(realNetValueList) / len(realNetValueList)
        
        # Write the analysis of each simulation day to the result file
        writer.writerow(["[Number: " + str(simulationDay+1) + "]", "[Date of Simulation: " + str(originalData[simulationStartDateRow + simulationDay][0]) + "]", "[Final Net Value: " + str(netValue) + "]", "[Up/Down Correct Rate: " + str(upDownCorrectRate) + "]", "[Final Net Value Average: " + str(netValueAverage) + "]", "[Real Net Value: " + str(realNetValue) + "]", "[Real Prediction: " + str(realPredictComp) + "]", "[Previous Real Up/Down Correct Rate: " + str(previousRealUpDownCorrectRate) + "]", "[Real Net Value Average: " + str(realNetValueAverage) + "]"])
        
        # Reset tensorflow graphs
        tf.reset_default_graph()