# General Usage

## Data collection
Data is collected using the script "man_data_collect.py". Launching this script will prompt for what to do next.
In the first screen typin 's' starts a measurement or typing 'x' exits the script.
When a measurement is started there is a 5s warmup before any data is recorded. While data is being recorded press 'q' to quit the measurement and return to the start screen.
The measurements in the chosen folder destination will automatically be enumerated "measurement_{x}.csv".

There are two phases, each writing to its own folder (set the "parent_folder" variable accordingly):
- Pressure-sensor calibration -> "Results_calibration".
- Actual experiments -> "Results_static_pressure".
Keeping them in separate folders means calibration and experiment data never get mixed up during analysis.

## Logging of data
Metadata is stored in JSON files, one per phase. Neither is tracked with git, so they have to be updated locally. The key of each entry must match the csv filename (without ".csv").
- ".cal_metadata.json" (calibration measurements). Each entry holds only "height" - the water column height in centimeters. The applied pressure is computed automatically in "cp" mode as P = rho * g * h (water, rho = 1000 kg/m^3). Calibration is sensor-level, so no channel is needed and the "Channel index" prompt is ignored in "cp" mode. (An explicit "applied_pressure" field is still honored as a fallback if no "height" is given.)
- ".exp_metadata.json" (experiment measurements). Each entry holds whatever parameters describe that measurement, e.g. "channel", "filament_width", "filament_length" and "applied_flowrate" - the flowrate imposed by the syringe pump (the known independent variable). Any field can be added and then used to select measurements at analysis time.

## Data transfer
You don't want all your data to be publicly available in the repo. For that reason directories of the form "Results*" are untracked. In order to transfer results between the lab pc and your own device use the "./get_data" script. It accepts one or more folder names, e.g. "./get_data Results_static_pressure Results_calibration" on your own device to download from the lab pc. Note: this will overwrite all your local data in those folders, so make sure that if you need to edit data files to only do it on the lab pc.

## Data analysis
The python script "analysis.py" analyzes the recorded pressure data.
The script picks its data folder and metadata file automatically from the chosen output type: the "cp" calibration mode reads "Results_calibration"/".cal_metadata.json", every other mode reads "Results_static_pressure"/".exp_metadata.json".
Upon launching the script two things are to be entered; a filter and the type of output you want.
The filter selects which measurements to analyze. A measurement is kept only if it matches every constraint. Examples:
- empty filter -> all measurements.
- "3" -> a single measurement by number (shortcut for measurement_3), e.g. to study one pressure time series on its own.
- "channel=0 filament_width=10 filament_length=5" -> only that geometry (varying flowrate), e.g. to fit a resistance.
The "key=value" tokens are matched against the metadata fields. A bare number is a shortcut for the special "name" field. The filter is ignored in "cp" mode, since calibration is a sensor-level operation.
The Arduino still sends two values per line ("flow,pressure"), but only the pressure column is used. The flowrate is the known value imposed by the syringe pump and is read from the metadata field "applied_flowrate".
A number of different output types are available:
### Calibration
- cp: Calibrate pressure. Maps the known "applied_pressure" from the metadata file to the raw sensor values in the csv data files. This prints two values in the terminal, to be inserted into ".sensor_calibration.json" at their respective positions. This allows the other output functions to produce calibrated data.
### Time series
- tp: Produces a plot of the measured pressure as a function of time.
### Scatter plots
- s: Produces a scatter plot of pressure vs. applied flowrate. This plots all recorded pressure samples for the chosen channel(s) against the applied flowrate. Samples are shown with a rainbow colourmap to indicate time dependence.
- sm: Produces a scatter plot of only the mean pressure against the applied flowrate for each individual measurement.
### Other
- r: Estimates the linear resistance (pressure vs. applied flowrate) based on a series of measurements. Output in the format "{resistance} + {error}".
- w: Writes the applied flowrate, mean pressure and pressure spread for the selected measurements to "export.csv" within this directory.
