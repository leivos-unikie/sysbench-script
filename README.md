To run sysbench tests automatically for ghaf in Lenovo X1 Carbon:
- Clone the repository (to some other machine than the target)
- In NixOS run nix develop (to install the dependencies defined in flake.nix)
- In other OS install the required python libraries (paramiko, matplotlib...)
- Connect Lenovo X1 to same network with the test running machine
- Check IP address of Lenovo X1 and replace target_ip variable with that in main_x1.py
- Run the test: python main_x1.py

Show results of a single test type:
- Edit parameters in the beginning of visualize_results.py
  - path to data
  - test type
  - test run range to be shown
- Generate plot by running: python visualize_results.py  

Save plots of all test types as .jpg files
- Edit parameters in the beginning of visualize_results2.py
  - path to data
  - test run range to be shown
- Save plots by running: python visualize_results2.py