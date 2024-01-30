import paramiko
import os
import time
from tools import *

target_ip = '10.0.0.10'
output_file = 'ssh.log'
test_run = 13

# This will be saved to root of the main result directory
long_build_description = """Test PR#406 PowerControl over ssh
"""

# This could optionally be used as an arbitrary name of the ghaf build under test.
# Build labels could show on the x-axis of the plot produced by visualize_results.py
# May be left empty
# build_label = ""

def main():
    start_time = time.time()
    print('Sysbench test run started.')
    try:
        file = open(output_file, "a")
        port = 22

        # Remove old ssh key from known_hosts
        # os.system('ssh-keygen -f "/home/samuli/.ssh/known_hosts" -R "10.0.0.10"')

        # created client using paramiko
        client = paramiko.SSHClient()

        # here we are loading the system
        # host keys
        # client.load_system_host_keys()

        # This is needed for paramiko to accept connection with unknown key (not using ssh keys)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        # connecting paramiko using target_ip and password
        client.connect(target_ip, port=port, username='ghaf', password='ghaf')

        chan = client.invoke_shell()

        scp = client.open_sftp()
        # scp.put('/home/samuli/repos/sysbench_script/sysbench_test', '/home/ghaf/sysbench_test')
        # scp.put('./sysbench_test', '/home/ghaf/sysbench_test')
        scp.put('/home/samuli/repos/sysbench_script/sysbench_test', '/home/ghaf/sysbench_test')

        time.sleep(2)
        # Close the SCP client
        scp.close()

        # Passing the commands to run the tests on VMs depends on where the network interface is (ghaf-host / net-vm).

        chan.send(b'hostname\n')
        time.sleep(1)
        resp = chan.recv(9999)
        output = resp.decode('ascii').split(',')
        print(''.join(output))

        if check_hostname(''.join(output), 'ghaf-host'):
            # Create directory for the test results and move there
            result_dir(chan, file, test_run, long_build_description)

            # Run test first on ghaf-host
            run_test(chan, file, 'host', test_run, 20)

            # Copy test_script to net-vm and ssh into net-vm
            log_netvm(chan, file)

            # Run test in ids-vm 192.168.100.3
            # appvm_from_netvm(chan, file, '192.168.100.3', 'ids-vm', test_run, 1)

            # Run test in net-vm
            run_test(chan, file, 'net-vm', test_run, 1)

            # Run test in other VMs
            test_appvms_from_netvm(chan, output_file, test_run)

            # Before enabling this ensure that IPs in tools.test_appvms_by_ip match with the hostnames.
            # test_appvms_by_ip(chan, output_file, test_run)

            # Pull the data from net-vm to host
            time.sleep(2)
            send_and_receive(chan, file, 'exit\n', 5, 9999)
            if send_and_receive(chan, file, 'scp -r ghaf@192.168.101.1:/home/ghaf/* ./\n', 5, 9999, 'assword'):
                send_and_receive(chan, file, 'ghaf\n', 5, 9999)
                time.sleep(3)

        elif check_hostname(''.join(output), 'net-vm'):

            # Create directory for the test results and move there
            result_dir(chan, file, test_run, long_build_description)

            # Run test in ids-vm 192.168.100.3
            # appvm_from_netvm(chan, file, '192.168.100.3', 'ids-vm', test_run, 1)

            test_appvms_from_netvm(chan, file, test_run)
            run_test(chan, file, 'net-vm', test_run, 1)

            # Test also on ghaf-host and pull data
            appvm_from_netvm(chan, file, '192.168.101.2', 'host', test_run, 20)

        else:
            print("Unknown hostname.")

        # Pull the data out
        # Does not work with *
        # Should zip the files first but no zip available on ghaf
        # scp = client.open_sftp()
        # scp.get('/home/ghaf/*', './result_data/')
        # time.sleep(2)
        # Close the SCP client
        # scp.close()

    finally:
        file.close()
        client.close()

    end_time = time.time()
    execution_time = end_time - start_time

    print("Sysbench test finished.")
    print("Elapsed time: " + str(execution_time))


main()

# Pull the result files out from the target machine.
# os.system("sshpass -p 'ghaf' scp -r ghaf@{}:/home/ghaf/Test_run_{} ./result_data\n".format(target_ip, test_run))
