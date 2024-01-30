To run sysbench tests automatically for ghaf in Lenovo X1 Carbon:
- Clone the repository (to some other machine than the target)
- In NixOS run nix develop (to install the dependencies defined in flake.nix)
- In other OS install the required python libraries (paramiko, matplotlib...)
- Connect Lenovo X1 to same network with the test running machine
- Check IP address of Lenovo X1 and replace target_ip variable with that in main_x1.py
- Run the test: python main_x1.py

Plot the results:
- For now the test script does not copy test result files out from the target machine, so need to do it manually
- When the test is finished copy the result directory 'Test_run_{}' to result_data directory in the repository root, for example
    scp -r ghaf@{}:/home/ghaf/Test_run_{} ./result_data
- Edit the parameters in the beginning of visualize_results.py select the test type and limit test runs to be shown
- Generate plot by running: python visualize_results.py  
