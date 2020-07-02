# espDroneController

This controller works with https://github.com/Simaho99/espDrone.git

Requiremets

All up-to-date
1. Python 3.7 +
2. Kivy
3. Kivy garden graph
4. pyModbusIP

You will also need
Buildozer to build into mobile app (tested)
Kivy_ios for ios app (tested)

There are two ways to connect to the app
1. Using Local IP to control drone (192.168.4.1 and Port 502 for ModbusIP) usually connects automatically
after WiFi Connection.
2. Set a public IP per your requirement (on SETTING page), you will need get the right SSID and Password from 
the arduino code

Currently you can set the PID variables from the app interractively and read the ourput on the app
in form of graphs. The output is the angles, input angle, set angle and the PID angle our output angle

The read speed matters a lot and it is fast enough than the arduino, the graph values changes so fast 
thats why, we store each of 100 values and can be accesses by the order of 100, like a screen snapshots.

***STILL ON DEVELOPMENT STAGE***
