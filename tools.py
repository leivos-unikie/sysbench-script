import time


def send_and_receive(channel, cmd, wait_time, recv_buffer):
    channel.send(cmd)
    time.sleep(wait_time)
    resp = channel.recv(recv_buffer)
    output = resp.decode('ascii').split(',')
    print(''.join(output))
    return


def check_hostname(output, expected_hostname):

    if output.find(expected_hostname) != -1:
        print(expected_hostname + " detected")
        return True
    else:
        return False


def run_test(chan, file, vm, build_id, threads):

    send_and_receive(chan, 'sudo chmod 777 sysbench_test\n', 1, 9999)
    send_and_receive(chan, 'ghaf\n', 1, 9999)

    chan.send('./sysbench_test {} {} {}\n'.format(vm, build_id, threads))
    read_output(chan, file)

    return


def read_output(chan, file):
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
            file.write(str(output))
            if output.find("Test finished") != -1:
                return
        else:
            clock += 1
        if clock > 60:
            return


def log_netvm(chan):
    send_and_receive(chan, 'rm ~/.ssh/known_hosts\n', 1, 9999)
    send_and_receive(chan, 'scp ./sysbench_test ghaf@192.168.101.1:/home/ghaf\n', 1, 9999)
    send_and_receive(chan, 'yes\n', 1, 9999)
    send_and_receive(chan, 'ghaf\n', 2, 9999)
    send_and_receive(chan, 'ssh ghaf@192.168.101.1\n', 2, 9999)
    send_and_receive(chan, 'ghaf\n', 1, 9999)
    send_and_receive(chan, 'hostname\n', 1, 9999)


def appvm_from_netvm(chan, file, ip_address, vm, build_id, threads):
    # ip_address: When running from net-vm this can be the dns name or ip of the vm
    # vm: The environment name used in the result directory name
    # build_id: Build job no.
    # threads: Available threads in the environment/vm where the test will be run

    # Copy test_script to the AppVM and ssh into the AppVM
    send_and_receive(chan, 'rm ~/.ssh/known_hosts\n', 1, 9999)
    send_and_receive(chan, 'scp ./sysbench_test ghaf@{}:/home/ghaf\n'.format(ip_address), 1, 9999)
    send_and_receive(chan, 'yes\n', 1, 9999)
    send_and_receive(chan, 'ghaf\n', 2, 9999)
    send_and_receive(chan, 'ssh ghaf@{}\n'.format(ip_address), 2, 9999)
    send_and_receive(chan, 'ghaf\n', 1, 9999)
    send_and_receive(chan, 'hostname\n', 1, 9999)

    print("Ready to run the test script in {}.".format(ip_address))

    run_test(chan, file, vm, build_id, threads)

    # Pull the data to net-vm
    send_and_receive(chan, 'exit\n', 1, 9999)
    send_and_receive(chan, 'scp -r ghaf@{}:/home/ghaf/* ./\n'.format(ip_address), 1, 9999)
    send_and_receive(chan, 'ghaf\n', 2, 9999)

    return


def test_appvms_from_netvm(chan, file, build_id):
    appvm_from_netvm(chan, file, 'chromium-vm', 'chromium-vm', build_id, 4)
    appvm_from_netvm(chan, file, 'gala-vm', 'gala-vm', build_id, 2)
    appvm_from_netvm(chan, file, 'zathura-vm', 'zathura-vm', build_id, 1)
    appvm_from_netvm(chan, file, 'gui-vm', 'gui-vm', build_id, 2)
    return
