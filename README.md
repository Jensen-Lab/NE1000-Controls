# General Usage

## Data collection
Data is collected using the script "man_data_collect.py". Launching this script will prompt for what to do next.
In the first screen typin 's' starts a measurement or typing 'x' exits the script.
When a measurement is started there is a 5s warmup before any data is recorded. While data is being recorded press 'q' to quit the measurement and return to the start screen.
Measurements can be written to any folder you like, to change which folder is the destination change the "parent_folder". 
The measurements in the chosen folder destination will automatically be enumerated "measurement_{x}.csv".

## Data analysis
The python script "txt_for_me.py" contains a number of useful functions for analyzing data. 
Make sure to set the variable "data_directory" within the script to the directory corresponding to the one that was written to with "man_data_collect.py".
Usage of the analysis script requires a metadata file ".exp_metadata.json" to be filled out with relevant information (applied pressure and channel index).
Upon launching the script two things are to entered; the index of the channel(s) (for multiple channels simpy separate with space) you want to analyze data for and the type of output you want.
A number of different output types are available:
### Calibration
- cp: Calibrate pressure. Maps the applied from metadata file to the sensor values in raw csv data files. This will print two values in terminal, these are to be inserted into the file ".sensor_calibration.json" at their respective positions. This allows for the other output functions to produce calibrated data.
- cf: Calibrate flowrate. This requires the metadata field "applied_pressure" to be filled out with applied flowrate rather than pressure. This will like for pressure then print two values to be inserted into ".sensor_calibration", for other functions to produce calibrated data.
### Time series
- tp: Produces a plot of the measured pressure as a function of time.
- tf: Produces a plot of the measured flowrate as a function of time.
### Scatter plots
- s: Produces a scatter plot of pressure vs. flowrate. This will plot all recorded values of pressure and flowrate for the chosen channel(s). Measurements are shown with a rainbow colourmap to indicate time dependence.
- sm: Produces a scatter plot of only the mean pressure and flowrate for each of the individual measurements.
### Other
- r: Estimates the linear resistance based on a series of measurements. Outputtet in the format "{resistance} + {error}".
- w: Writes the mean pressure and flowrates for the chosen channel to a single csv file within this directory. Naming convention of the file is "presflow_{channel index}.csv"