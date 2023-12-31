import matplotlib.pyplot as plt
import numpy as np
import os
import datetime

from extract_value import *

test_type = "memory_rd_1thread_report"
# test_type = "memory_wr_1thread_report"
# test_type = "cpu_1thread_report"

path_to_data = "./result_data"


def list_vm_files(file_list, vm_name):
    list_vm = []
    for f in file_list:
        if f.find(vm_name) != -1:
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
    values = []
    for f in file_list:
        if f.endswith(report_type):
            # Print also some file info to help tracking.
            time_created = os.path.getctime(f)
            time_created_h = datetime.datetime.fromtimestamp(time_created)
            print(time_created_h)
            print(f)
            value = float(extract(f, detect_string, start_string, end_string))
            print(value)
            print()

            values.append(value)

    return values


def vm_bar(plt, file_list, vm_name, x_offset, c):
    vm_files = list_vm_files(file_list, vm_name)

    # For memory test results
    vm_values = extract_values(vm_files, test_type, "MiB transferred", "(", " MiB/sec")

    # For cpu test results
    # vm_values = extract_values(vm_files, test_type, "events per second:", "events per second:", "\n")

    # Here rounding caused errors if '1 + x_offset + len(vm_values)' was used as stop.
    xpoints = list(np.arange(1 + x_offset, 0.9 + x_offset + len(vm_values), 1))
    plt.bar(xpoints, vm_values, label=vm_name, color=c, width=0.1)
    return


files_list = list_files(path_to_data)

vm_bar(plt, files_list, "host", 0, 'b')
vm_bar(plt, files_list, "net", 0.1, 'g')
vm_bar(plt, files_list, "gui-vm", 0.2, 'r')
vm_bar(plt, files_list, "chromium-vm", 0.3, 'y')
vm_bar(plt, files_list, "gala-vm", 0.4, 'k')
vm_bar(plt, files_list, "zathura-vm", 0.5, 'm')

plt.legend()
plt.xlabel('Builds')
plt.ylabel('MiB/sec')
plt.title('Details')

# Print the chart
plt.show()
