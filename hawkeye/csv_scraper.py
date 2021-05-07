import matplotlib.pyplot as plt
import glob
import os
import csv
import numpy as np

def get_data_from_csv(csvdir):
    csvfiles = glob.glob(os.path.join(csvdir, '*.csv'))
    csvdict = {}
    first_csv = True

    source_probe = None
    destination_probe = None
    test_duration = 0

    for csvfile in csvfiles:
        with open(csvfile, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['Test Information'] == 'SOURCE PROBE NAME' and first_csv:
                    source_probe = row['Value']
                if row['Test Information'] == 'DESTINATION PROBE NAME' and first_csv:
                    destination_probe = row['Value']
                if row['Test Information'] == 'TEST DURATION' and first_csv:
                    test_duration = int(row['Value'])
                if row['Test Information'] == 'END EXECUTION TIME':
                    csvdict[row['Value']] = csvfile
                if row['Test Information'] == 'TEST STATUS': #Ghetto method of stopping the loop lmao XD
                    first_csv = False
                    break

    sorted_csvs_keys = sorted(csvdict)

    i = 0
    time_value_dict = {}
    first_row_passed = False

    for key in sorted_csvs_keys:
        with open(csvdict[key], mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['Test Information'] == 'Delay (ms)':
                    if not first_row_passed:
                        first_row_passed = True
                    else:
                        time_value_dict[test_duration*i + int(row[None][0])] = row[None][1]
     
        i += 1
        first_row_passed = False

        if source_probe == "andreas":
            source_probe = "frontend"
        if destination_probe == "andreas":
            destination_probe = "frontend"

        command = csvdir.split("/")[0].replace("_", " ")

        results = list(map(int, time_value_dict.values()))

        avg = sum(results)/len(results)

        legend = "From " + source_probe + " to " + destination_probe + " " + command + ", Average: " + str(avg) + " ms"

    return legend, time_value_dict

def movingaverage(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')

legends = []
window_size = 10

legend, time_value_dict= get_data_from_csv("no_commands/aas_5g")
legends.append(legend)
tuple_x_y = [(k,int(v)) for k, v in sorted(time_value_dict.items(), key=lambda item: item[0])]
x_vals = [x[0] for x in tuple_x_y]
y_vals = [x[1] for x in tuple_x_y]
y_av = movingaverage(y_vals, window_size)
x_vals = x_vals[int(window_size/2):][:-int(window_size/2)]
y_av = y_av[int(window_size/2):][:-int(window_size/2)]
plt.plot(x_vals, y_av)

legend, time_value_dict= get_data_from_csv("with_commands/aas_5g")
legends.append(legend)
tuple_x_y = [(k,int(v)) for k, v in sorted(time_value_dict.items(), key=lambda item: item[0])]
x_vals = [x[0] for x in tuple_x_y]
y_vals = [x[1] for x in tuple_x_y]
y_av = movingaverage(y_vals, window_size)
x_vals = x_vals[int(window_size/2):][:-int(window_size/2)]
y_av = y_av[int(window_size/2):][:-int(window_size/2)]
plt.plot(x_vals, y_av)


plt.xlabel("Time since start [s]")
plt.ylabel("Delay [ms]")
plt.legend(legends)
plt.show()