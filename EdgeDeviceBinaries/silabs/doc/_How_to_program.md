## Brief
![Alt text]( ./00_TLDR_Silabs_programming.gif "How to program SiLabs DK board")

## Step by step
1) Open Commander utility and select device from drop-down list.
![Alt text]( ./01_open_and_select_kit.PNG)

2) View DeviceInfo to make sure the board is accessible. Check your board type (G21/G24, flash size).
![Alt text]( ./02_view_device_info.PNG)

3) Add files that you wish to program:  
   1) Silabs_MFG (from EdgeDeviceProvisioning)
   2) application (from EdgeDeviceBinaries)  

Remember to select binaries that match your board type (e.g. G21/G24, flash size) ! 

![text]( ./03_flash_MFG.PNG )
![text]( ./03b_flash_application.PNG )

4) After programming the board, open RTT terminal and see logs flowing
![Alt text]( ./04_rtt_configure.PNG)
![Alt text]( ./04_rtt_logs_flow.PNG)