# General Usage

## Data collection
Data is collected using the script "man_data_collect.py". Launching this script will prompt for what to do next.
In the first screen typin 's' starts a measurement or typing 'x' exits the script.
When a measurement is started there is a 5s warmup before any data is recorded. While data is being recorded press 'q' to quit the measurement and return to the start screen.
Measurements can be written to any folder you like, to change which folder is the destination change the "parent_folder". 
The measurements in the chosen folder destination will automatically be enumerated "measurement_{x}.csv".

## Logging of data
There are two different files for data logging. None of these files are tracked with git, so they have to be updated locally.
- ".exp_metadata.json" - this is a json file for storing metadata about experiments. Currently holds channel index and applied pressure. More fields can be added at will and then loaded from the analysis script.
- ".exp_metadata.txt" - this simply a txt file for general notes about channels etc.

## Data transfer
You don't want all your data to be publicly available in the repo. For that reason directories of the form "Results*" are untracked (e.g. the current "Results_static_pressure" folder). In order to transfer results between the lab pc and your own device use the "./get_data" script (simply type e.g. "./get_data Results_static_pressure" on your own device to download from lab pc). Note: this will overwrite all your local data, so make sure that if you need to edit data files to only do it on the lab pc.

## Data analysis
The python script "txt_for_me.py" contains a number of useful functions for analyzing data. 
Make sure to set the variable "data_directory" within the script to the directory corresponding to the one that was written to with "man_data_collect.py".
Usage of the analysis script requires a metadata file ".exp_metadata.json" to be filled out with relevant information.
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
