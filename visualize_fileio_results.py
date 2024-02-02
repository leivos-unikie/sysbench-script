import matplotlib.pyplot as plt
import numpy as np
import os

from extract_value import *


path_to_data = "./../sysbench_result_data/lenovo-x1/"

# Limit the range of plotted test runs
first_test_run_no = 0   # test runs with lower number won't be shown
last_test_run_no = 13   # test runs with higher number won't be shown


def list_vm_files(file_list, vm_name):
    list_vm = []
    for f in file_list:
        if f.find(vm_name) != -1 and f.split('/')[-1].find('report') != -1:
            list_vm.append(f)
    return list_vm


def list_files(path):
    file_list = []
    for path, subdirs, files in os.walk(path):
        for name in files:
            # print(os.path.join(path, name))
            file_list.append(os.path.join(path, name))
    file_list.sort(key=os.path.getctime)
    return file_list


def extract_values(file_list, report_type, detect_string, start_string, end_string):

    values = [0] * (last_test_run_no + 1)

    for f in file_list:
        if f.endswith(report_type):

            # Print also some file info.
            # time_created = os.path.getctime(f)
            # time_created_h = datetime.datetime.fromtimestamp(time_created)
            # print(time_created_h)
            # print(f)
            # print()

            index = int(f.split('/')[-2].split('_')[0])
            if index > last_test_run_no: continue

            value = float(extract(f, detect_string, start_string, end_string).lstrip(":"))
            values[index] = value

    values_sliced = values[first_test_run_no:]

    return values_sliced


def zero_to_nan(values):
    """Replace every 0 with 'nan' and return a copy."""
    return [float('nan') if x==0 else x for x in values]


def plot_fileio_results(plt):

    file_list = list_files(path_to_data)
    vm_files = list_vm_files(file_list, 'host')

    rd_values = extract_values(vm_files, 'fileio_rd_report', "read, MiB/s:", ":", "\n")
    wr_values = extract_values(vm_files, 'fileio_wr_report', "written, MiB/s:", ":", "\n")

    print("Read:")
    print(rd_values)
    print("Write:")
    print(wr_values)
    print()

    # Here rounding caused errors if 'last_test_run_no + x_offset' was used as stop.
    xpoints = list(np.arange(first_test_run_no, last_test_run_no + 0.9, 1))

    rd_values = zero_to_nan(rd_values)
    wr_values = zero_to_nan(wr_values)

    figure, axis = plt.subplots(2)

    # Plot in separate graphs
    axis[0].scatter(xpoints, rd_values, color='g', label='read', linestyle='dashed', marker='s')
    axis[0].set_title("Read")
    axis[1].scatter(xpoints, wr_values, color='b', label='write', linestyle='dashed', marker='s')
    axis[1].set_title("Write")
    plt.xlabel('Test run')
    figure.supylabel('MiB/s')
    plt.setp(axis, xticks=list(range(first_test_run_no, last_test_run_no + 1, 1)))
    plt.subplots_adjust(hspace=0.4)

    # Plot in same graph
    # plt.scatter(xpoints, rd_values, color='g', label='read', linestyle='dashed', marker='s')
    # plt.scatter(xpoints, wr_values, color='b', label='write', linestyle='dashed', marker='s')
    # plt.legend(loc='lower left')
    # plt.xlabel('Test run')
    # plt.xticks(list(range(first_test_run_no, last_test_run_no + 1, 1)))
    # plt.ylabel('MiB/s')
    # plt.title('fileio read/write test report')

    plt.savefig("{}fileio_plots_from_test_runs_{}-{}.jpg".format(path_to_data, first_test_run_no, last_test_run_no))

    # Print the chart
    plt.show()

    return


plot_fileio_results(plt)