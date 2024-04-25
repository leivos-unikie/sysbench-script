# SPDX-FileCopyrightText: 2022-2024 Technology Innovation Institute (TII)
# SPDX-License-Identifier: Apache-2.0

import time


def result_dir(chan, file, test_run, long_build_description):
    # Create directory for the test results and move there
    send_and_receive(chan, file, 'mkdir Test_run_{}\n'.format(test_run), 1, 999)
    send_and_receive(chan, file, 'mv sysbench_test ./Test_run_{}\n'.format(test_run), 2, 999)
    send_and_receive(chan, file, 'cd Test_run_{}\n'.format(test_run), 2, 999)
    send_and_receive(chan, file, 'echo "{}" >> build_description.txt\n'.format(long_build_description), 2, 999)


def send_and_receive(chan, file, cmd, wait_time, recv_buffer, expected=''):

    chan.send(cmd)

    clock = 0
    while True:

        data = chan.recv_ready()
        if data:
            clock = 0
            resp = chan.recv(recv_buffer)
            # print(str(resp))
            output = resp.decode('utf-8')
            # output = resp.decode('ascii').split(',')
            print(output)

            # appending all output to output file
            # file.write(str(output))
            if output.find(expected) != -1:
                time.sleep(0.5)
                return True
        else:
            time.sleep(1)
            print(clock)
            clock += 1
        if clock > wait_time:
            return False


def check_hostname(output, expected_hostname):

    if output.find(expected_hostname) != -1:
        print(expected_hostname + " detected")
        return True
    else:
        return False


def run_test(chan, file, vm, test_run, threads):

    if send_and_receive(chan, file, 'sudo chmod 777 sysbench_test\n', 5, 999, 'password'):
        send_and_receive(chan, file, 'ghaf\n', 5, 999)
        chan.send('./sysbench_test {} {} {}\n'.format(vm, test_run, threads))
        read_test_output(chan, file)

    return


def read_test_output(chan, file):
    clock = 0
    while True:
        time.sleep(1)
        print(clock)
        data = chan.recv_ready()
        if data:
            clock = 0
            resp = chan.recv(999)
            # print(str(resp))
            output = resp.decode('utf-8')
            print(output)

            # appending all output to output file
            # file.write(str(output))
            if output.find("Test finished") != -1:
                return
        else:
            clock += 1
        if clock > 60:
            return


def log_netvm(chan, file):
    send_and_receive(chan, file, 'rm ~/.ssh/known_hosts\n', 5, 9999)
    if send_and_receive(chan, file, 'scp ./sysbench_test ghaf@192.168.101.1:/home/ghaf\n', 5, 9999, 'Are you sure you want to continue connecting'):
        if send_and_receive(chan, file, 'yes\n', 5, 9999, 'assword'):
            send_and_receive(chan, file, 'ghaf\n', 5, 9999)
    time.sleep(1)
    if send_and_receive(chan, file, 'ssh ghaf@192.168.101.1\n', 5, 9999, 'assword'):
        send_and_receive(chan, file, 'ghaf\n', 5, 9999)
        send_and_receive(chan, file, 'hostname\n', 5, 9999)


def appvm_from_netvm(chan, file, ip_address, vm, test_run, threads):
    # ip_address: When running from net-vm this can be the dns name or ip of the vm
    # vm: The environment name used in the result directory name
    # test_run: Build job no.
    # threads: Available threads in the environment/vm where the test will be run

    # Copy test_script to the AppVM and ssh into the AppVM
    send_and_receive(chan, file, 'rm ~/.ssh/known_hosts\n', 5, 9999)
    if send_and_receive(chan, file, 'scp ./sysbench_test ghaf@{}:/home/ghaf\n'.format(ip_address), 5, 9999, 'Are you sure you want to continue connecting'):
        if send_and_receive(chan, file, 'yes\n', 5, 9999, 'assword'):
            send_and_receive(chan, file, 'ghaf\n', 5, 9999)
    time.sleep(1)
    if send_and_receive(chan, file, 'ssh ghaf@{}\n'.format(ip_address), 2, 9999, 'assword'):
        send_and_receive(chan, file, 'ghaf\n', 5, 9999)
        send_and_receive(chan, file, 'hostname\n', 5, 9999)

    print("Ready to run the test script in {}.".format(ip_address))

    run_test(chan, file, vm, test_run, threads)

    # Pull the data to net-vm
    send_and_receive(chan, file, 'exit\n', 5, 9999)
    if send_and_receive(chan, file, 'scp -r ghaf@{}:/home/ghaf/* ./\n'.format(ip_address), 5, 9999, 'assword'):
        send_and_receive(chan, file, 'ghaf\n', 5, 9999)
        time.sleep(2)

    return


def test_appvms_from_netvm(chan, file, test_run):
    appvm_from_netvm(chan, file, 'chromium-vm', 'chromium-vm', test_run, 4)
    appvm_from_netvm(chan, file, 'gala-vm', 'gala-vm', test_run, 2)
    appvm_from_netvm(chan, file, 'zathura-vm', 'zathura-vm', test_run, 1)
    appvm_from_netvm(chan, file, 'gui-vm', 'gui-vm', test_run, 2)
    # appvm_from_netvm(chan, file, 'element-vm', 'element-vm', test_run, 1)
    appvm_from_netvm(chan, file, 'ids-vm', 'ids-vm', test_run, 1)
    # appvm_from_netvm(chan, file, 'audio-vm', 'audio-vm', test_run, 1)
    return


# IPs have to be checked after each boot if going to use this.
def test_appvms_by_ip(chan, file, test_run):
    appvm_from_netvm(chan, file, '192.168.100.4', 'chromium-vm', test_run, 4)
    appvm_from_netvm(chan, file, '192.168.100.3', 'gala-vm', test_run, 2)
    appvm_from_netvm(chan, file, '192.168.100.5', 'zathura-vm', test_run, 1)
    appvm_from_netvm(chan, file, '192.168.100.2', 'gui-vm', test_run, 2)
    return