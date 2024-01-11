import paramiko
import os
import time
from tools import *

target_ip = '10.0.0.10'
output_file = 'ssh.log'
build_id = 3


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
            # Run test first on ghaf-host
            run_test(chan, file, 'host', build_id, 20)

            # Copy test_script to net-vm and ssh into net-vm
            log_netvm(chan, file)

            # Run test in ids-vm 192.168.100.3
            # appvm_from_netvm(chan, file, '192.168.100.3', 'ids-vm', build_id, 1)

            # Run test in net-vm
            run_test(chan, file, 'net-vm', build_id, 1)

            # Run test in other VMs
            test_appvms_from_netvm(chan, output_file, build_id)

            # Pull the data from net-vm to host
            time.sleep(2)
            send_and_receive(chan, file, 'exit\n', 5, 9999)
            if send_and_receive(chan, file, 'scp -r ghaf@192.168.101.1:/home/ghaf/* ./\n', 5, 9999, 'assword'):
                send_and_receive(chan, file, 'ghaf\n', 5, 9999)
                time.sleep(3)

        else:
            if check_hostname(''.join(output), 'net-vm'):

                # Run test in ids-vm 192.168.100.3
                # appvm_from_netvm(chan, file, '192.168.100.3', 'ids-vm', build_id, 1)

                test_appvms_from_netvm(chan, file, build_id)
                run_test(chan, file, 'net-vm', build_id, 1)

                # Test also on ghaf-host and pull data
                appvm_from_netvm(chan, file, '192.168.101.2', 'host', build_id, 20)

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
# os.system("sshpass -p 'ghaf' scp -r ghaf@{}:/home/ghaf/* ./result_data\n".format(target_ip))
