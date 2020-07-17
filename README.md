# espDroneApp

This controller works with https://github.com/SimahoJr/espDrone.git

Requiremets

All up-to-date
1. Python 3.7 +
2. Kivy
3. Kivy garden graph
4. pyModbusIP

You will also need
1. Buildozer to build into mobile app (tested)
2. Kivy_ios for ios app (tested)

There are two ways to connect to the app
1. Using Local IP to control drone (192.168.4.1 and Port 502 for ModbusIP) usually connects automatically
after WiFi Connection.
2. Set a public IP per your requirement (on SETTING page), you will need also get the right SSID and Password from 
the arduino code

What it does
1. Currently you can set the PID variables from the app interractively and see the output on the app in form of graphs on the same screen. 
The output are the angles; input angle, set angle and the PID angle output angle

2. The app also stores the output(Angles) in the order of 100. These can be accesses by the users as snapshots.

3. The snapshots then can be zoomed.

4. You can not zoom the current readings only the snapshots (*bug)

***STILL ON DEVELOPMENT STAGE***
