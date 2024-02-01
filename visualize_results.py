import matplotlib.pyplot as plt
import numpy as np
import os
import datetime

from extract_value import *


# Limit the range of plotted test runs
first_test_run_no = 6   # test runs with lower number won't be shown
last_test_run_no = 13   # test runs with higher number won't be shown

# Select which test type to plot: 0-5
test = '5'
test_type = None
if test == '0':
    test_type = "memory_rd_1thread_report"
elif test == '1':
    test_type = "memory_wr_1thread_report"
elif test == '2':
    test_type = "memory_rd_report"
elif test == '3':
    test_type = "memory_wr_report"
elif test == '4':
    test_type = "cpu_1thread_report"
elif test == '5':
    test_type = "cpu_report"
else:
    exit(1)

path_to_data = "./../sysbench_result_data/lenovo-x1/"


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

            value = float(extract(f, detect_string, start_string, end_string))

            values[index] = value

    values_sliced = values[first_test_run_no:]

    return values_sliced


def vm_bar(plt, file_list, vm_name, x_offset, c):
    vm_files = list_vm_files(file_list, vm_name)

    if test == '0' or test == '1' or test == '2' or test == '3':
        # For memory test results
        vm_values = extract_values(vm_files, test_type, "MiB transferred", "(", " MiB/sec")
    elif test == '4' or test == '5':
        # For cpu test results
        vm_values = extract_values(vm_files, test_type, "events per second:", "events per second:", "\n")
    else:
        return

    print("List of " + vm_name + " results")
    print(vm_values)
    print()

    # Here rounding caused errors if 'last_test_run_no + x_offset' was used as stop.
    xpoints = list(np.arange(first_test_run_no + x_offset, last_test_run_no + x_offset + 0.9, 1))
    plt.bar(xpoints, vm_values, label=vm_name, color=c, width=0.1)
    return


files_list = list_files(path_to_data)

vm_bar(plt, files_list, "host", 0, 'b')
vm_bar(plt, files_list, "net-vm", 0.1, 'g')
vm_bar(plt, files_list, "gui-vm", 0.2, 'r')
vm_bar(plt, files_list, "chromium-vm", 0.3, 'y')
vm_bar(plt, files_list, "gala-vm", 0.4, 'k')
vm_bar(plt, files_list, "zathura-vm", 0.5, 'm')
vm_bar(plt, files_list, "ids-vm", 0.6, 'lime')
vm_bar(plt, files_list, "audio-vm", 0.7, 'pink')

plt.legend(loc='lower left')
plt.xlabel('Test run')
plt.xticks(np.arange(first_test_run_no, last_test_run_no + 1, step=1))

if int(test) < 4:
    # For cpu test
    plt.ylabel('Events per second')
else:
    # For memory test
    plt.ylabel('MiB/sec')

plt.title(test_type)

# Print the chart
plt.show()
