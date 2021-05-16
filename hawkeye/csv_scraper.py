import matplotlib.pyplot as plt
import glob
import os
import csv
import numpy as np

def get_data_from_csv(csvdir):
    csvfiles = glob.glob(os.path.join(csvdir, '*.csv'))
    
    csvdicts = {}

    for csvfile in csvfiles:
        with open(csvfile, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['Test Information'] == 'END EXECUTION TIME':
                    end_execution_time = row['Value']
                if row['Test Information'] == 'SOURCE PROBE NAME':
                    source_probe = row['Value']
                if row['Test Information'] == 'DESTINATION PROBE NAME':
                    destination_probe = row['Value']
                if row['Test Information'] == 'TEST DURATION':
                    test_duration = int(row['Value'])
                if row['Test Information'] == 'TEST STATUS': #Ghetto method of stopping the loop lmao XD
                    key = source_probe + ":" + destination_probe
                    if key in csvdicts:
                        csvdicts[key][end_execution_time] = csvfile
                    else:
                        csvdicts[key] = {end_execution_time : csvfile}                    
                    break

    return_dict = {}
    
    for key in csvdicts:
        
        sorted_dict = sorted(csvdicts[key])
        i = 0
        time_value_dict = {}
        first_row_passed = False
        
        for inner_key in sorted_dict:
            with open(csvdicts[key][inner_key], mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    if row['Test Information'] == 'Delay (ms)':
                        if not first_row_passed:
                            first_row_passed = True
                        else:
                            time_value_dict[test_duration*i + int(row[None][0])] = row[None][1]
        
            i += 1
            first_row_passed = False
            

        title = csvdir.split("/")[0].replace("_", " ")

        results = list(map(int, time_value_dict.values()))

        avg = sum(results)/len(results)

        legend = "From " + key.split(":")[0] + " to " + key.split(":")[1] + ", Average: " + str(round(avg, 3)) + " ms" + " : " + title 

        return_dict[legend] = time_value_dict

    return return_dict


def movingaverage(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')


def plotcsvdir(csvdir):
    dict_ = get_data_from_csv(csvdir)
    plt.rcParams["figure.figsize"] = (8,6)
    legends = []
    window_size = 100

    sorted_dict = sorted(dict_)
    plt.xlabel("Time since start [s]")
    plt.ylabel("Delay [ms]")
    plt.xlim(0, 3200)
    plt.ylim(0, 45)
    title = None

    for d in sorted_dict:
        legend, title = d.split(" : ")
        legends.append(legend)
        tuple_x_y = [(k,int(v)) for k, v in sorted(dict_[d].items(), key=lambda item: item[0])]
        x_vals = [x[0] for x in tuple_x_y]
        y_vals = [x[1] for x in tuple_x_y]
        y_av = movingaverage(y_vals, window_size)
        x_vals = x_vals[int(window_size/2):][:-int(window_size/2)]
        y_av = y_av[int(window_size/2):][:-int(window_size/2)]
        plt.plot(x_vals, y_av)
        
    plt.title(title)
    plt.legend(legends)    
    plt.savefig(title)
    #plt.show()
    plt.clf()

def compare_dir(dirs, route_to_compare):

    legends = []
    plt.rcParams["figure.figsize"] = (8,6)
    plt.xlabel("Time since start [s]")
    plt.ylabel("Delay [ms]")
    window_size = 100
    plt.xlim(0, 3200)
    plt.ylim(0, 45)
    plt.title(route_to_compare)

    for dir_ in dirs:
        csvdict = get_data_from_csv(dir_)
        for key in csvdict:
            if key.split(",")[0] == route_to_compare:
                splitting = key.split(",")[1].split(" : ")
                legends.append(splitting[1] + ", " +  splitting[0])
                tuple_x_y = [(k,int(v)) for k, v in sorted(csvdict[key].items(), key=lambda item: item[0])]
                x_vals = [x[0] for x in tuple_x_y]
                y_vals = [x[1] for x in tuple_x_y]
                y_av = movingaverage(y_vals, window_size)
                x_vals = x_vals[int(window_size/2):][:-int(window_size/2)]
                y_av = y_av[int(window_size/2):][:-int(window_size/2)]
                plt.plot(x_vals, y_av)
                
    plt.legend(legends)
    plt.savefig("comparison_" + route_to_compare)
    #plt.show()
    plt.clf()

def plot_induvidual_files():
    plotcsvdir("Lab_no_commands")
    plotcsvdir("Lab_with_commands")
    plotcsvdir("Office_no_commands")
    plotcsvdir("Office_with_commands")

def plot_comparisons():
    dirs = ["Office_no_commands", "Office_with_commands", "Lab_no_commands", "Lab_with_commands"]
    compare_dir(dirs, "From raspberrypi-5G to raspberrypi-AAS")
    compare_dir(dirs, "From raspberrypi-AAS to raspberrypi-5G")
    compare_dir(dirs, "From andreas to raspberrypi-AAS")
    compare_dir(dirs, "From raspberrypi-AAS to andreas")


#plot_induvidual_files()
plot_comparisons()