# Investment Decision Analyzer

This project aims to create a model with Recurrent Neural Network using Long Short Term Memory that analyzes financial time series data
and make predictions of price movement.


simulation.py (best run with Python3, Tensorflow activated)
- runs the simulation of with simple buy-all/sell-all scheme after making up/down predictions of the stock value

dataCoordinator.py (best run with Python2)
- coordinates several different financial data files into single one csv file for simulation.py

dataModifier.py (best run with Python2)
- preprocesses the data by filling in data as specified as needed

dateTool.py (best run with Python2)
- houses date calculating functions used by dataModifier.py and dataCoordinator.py



coordinatedData folder
- houses the coordinated data files created by dataCoordinator.py

indicators folder
- houses the raw (straight from Yahoo Finance) financial data csv files or modified versions made by dataModifier.py

simulationResults folder
- houses the simulation result csv files made by simulation.py



Instructions:
1. Gather all financial time series data from Yahoo Finance ("Historical Price") into the 'indicators' folder as deemed necessary.
2. Run dataModifier.py as needed on the gathered financial data to preprocess.
3. Run dataCoordinator.py on the financial time series data files to consider to organize into one file.
4. With Tensorflow activated, run simulation.py and enter appropriate parameters.

