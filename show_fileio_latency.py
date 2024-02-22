import matplotlib.pyplot as plt
import numpy as np
import os

from extract_value import *


path_to_data = "./../sysbench_result_data/lenovo-x1/"

# Limit the range of plotted test runs
first_test_run_no = 0   # test runs with lower number won't be shown
last_test_run_no = 18   # test runs with higher number won't be shown


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


def extract_values(file_list, report_type):

    values = [[0 for i in range(last_test_run_no + 1)] for j in range(6)]

    for f in file_list:
        if f.endswith(report_type):

            # Omit the test runs which have index out of the range limits.
            index = int(f.split('/')[-2].split('_')[0])
            if index > last_test_run_no or index < first_test_run_no: continue

            values[0][index] = float(extract(f, "read, MiB/s:", ":", "\n").lstrip(":"))
            values[1][index] = float(extract(f, "written, MiB/s:", ":", "\n").lstrip(":"))
            values[2][index] = float(extract(f, "min:", ":", "\n").lstrip(":"))
            values[3][index] = float(extract(f, "avg:", ":", "\n").lstrip(":"))
            values[4][index] = float(extract(f, "max:", ":", "\n").lstrip(":"))
            values[5][index] = float(extract(f, "95th percentile:", ":", "\n").lstrip(":"))

    values_sliced = [x[first_test_run_no:] for x in values]

    return values_sliced


def zero_to_nan(values):
    """Replace every 0 with 'nan' and return a copy."""
    return [float('nan') if x==0 else x for x in values]


def plot_fileio_results(plt):

    file_list = list_files(path_to_data)
    vm_files = list_vm_files(file_list, 'host')

    rd_values = extract_values(vm_files, 'fileio_rd_report')
    wr_values = extract_values(vm_files, 'fileio_wr_report')

    print("Read:")
    print(rd_values)
    print("Write:")
    print(wr_values)
    print()

    # Here rounding caused errors if 'last_test_run_no + x_offset' was used as stop.
    xpoints = list(np.arange(first_test_run_no, last_test_run_no + 0.9, 1))

    # Plot only non-zero values. Consequently min values are not shown unless they are > 0.
    for i in range(0, 6):
        rd_values[i] = zero_to_nan(rd_values[i])
        wr_values[i] = zero_to_nan(wr_values[i])

    figure, axis = plt.subplots(5)

    # Plot in separate graphs
    axis[0].scatter(xpoints, rd_values[0], color='g', label='read', linestyle='dashed', marker='s')
    axis[0].set_title("Read")
    axis[1].scatter(xpoints, wr_values[1], color='b', label='write', linestyle='dashed', marker='s')
    axis[1].set_title("Write")
    axis[2].plot(xpoints, rd_values[4], color='#00aaaa', label='rd max', linestyle='solid', marker='s')
    axis[2].plot(xpoints, wr_values[4], color='#bbbb00', label='wr max', linestyle='solid', marker='s')
    axis[2].set_title("Read/Write latency max")
    axis[3].plot(xpoints, rd_values[2], color='#000000', label='min', linestyle='solid', marker='s')
    axis[3].plot(xpoints, rd_values[3], color='#cc11cc', label='avg', linestyle='solid', marker='s')
    axis[3].plot(xpoints, rd_values[5], color='#33aa66', label='95th', linestyle='solid', marker='s')
    axis[3].set_title("Read latency stats")
    axis[4].plot(xpoints, wr_values[2], color='#000000', label='min', linestyle='solid', marker='s')
    axis[4].plot(xpoints, wr_values[3], color='#cc11cc', label='avg', linestyle='solid', marker='s')
    axis[4].plot(xpoints, wr_values[5], color='#33aa66', label='95th', linestyle='solid', marker='s')
    axis[4].set_title("Write latency stats")
    plt.xlabel('Test run')
    figure.supylabel('Latency (ms)')
    plt.setp(axis, xticks=list(range(first_test_run_no, last_test_run_no + 1, 1)))
    plt.subplots_adjust(hspace=0.4)
    plt.legend(loc='lower left')

    plt.savefig("{}fileio_plots_from_test_runs_{}-{}.jpg".format(path_to_data, first_test_run_no, last_test_run_no))

    # Print the chart
    plt.show()

    return


plot_fileio_results(plt)