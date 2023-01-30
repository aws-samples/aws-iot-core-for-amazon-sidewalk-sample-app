## Brief
![Alt text]( ./00_TLDR_Nordic_programming.gif "How to program Nordic DK board")

## Step by step
1) Open nRF Connect utility and select Programmer
![Alt text]( ./01_open_nrf_connect.PNG)

2) Select device from drop-down list. Wait for board to initialize.
![Alt text]( ./02a_select_device.PNG)

3) Add files that you wish to program:  
   1) Nordic_MFG (from EdgeDeviceProvisioning)
   2) soft_device.hex (from EdgeDeviceBinaries)
   3) application.hex (from EdgeDeviceBinaries)
![text]( ./03_all_files_to_program.PNG )

4) Erase & Write the binaries.
![Alt text]( ./04_program.PNG)

5) After programming the board, open RTT terminal and see logs flowing
![Alt text]( ./05a_rtt_logs_open.PNG)
![Alt text]( ./05b_rtt_logs_configuration.PNG)
![Alt text]( ./05c_rtt_logs_flowing.PNG)