# Ev3 Tracked Explorer Mark II
The Ev3 Tracked Explorer Mark II is a rover built with Lego Mindstorms Ev3 and Lego Technic parts. I've replaced the firmware running on the Ev3 brick with [ev3dev](https://www.ev3dev.org) firmware, which let you program the Ev3 brick with Python (among other prossible choices).

Main features of the Ev3 Tracked Explorer Mark II **vehicle**:
- N.2 Ev3 Large Motors for driving
- N.1 Ev3 Medium Motor to rotate the *head*
- N.1 Ev3 Infrared sensor mounted on the rotating head to scan the envirnoment for obstacles

Main features of the Ev3 Tracked Explorer Mark II **software**:
- The rover can be controlled from a desktop app running on a Windows PC
- The rover streams sensor and motors telemetry to the desktop app

There are two projectes in this repository:
- **Remote Control App** is a Universal Windows Application that connects to the rover via *UDP/IP* protocol to send driving commands and to receive telemetry data. From this application the rover you can control the rover with a *PS4 Dual Shock Controller*.
- **Rover App** contains the Python scripts that run on the Ev3-brick. These scripts wait for commands from the Remote Control App, drive the rover accordingly, and send back telemetry data.

Have a look at the [Smallrobots.it](https://www.smallrobots.it/) blog for details.

![Ev3 Tracked Explorer](pictures/TE_MarkII.png)
