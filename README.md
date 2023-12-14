
## README for TPRG2131 Project
Overview
This project includes a server and client application designed to monitor and display system metrics from a Raspberry Pi. The server displays data in a GUI, and the client collects and sends data to the server.

Features
Server Application: Runs on a PC or Raspberry Pi, displaying temperature, voltage, clock speed, HDMI clock speed, and GPU memory frequency.
Client Application: Executes on Raspberry Pi, collecting system metrics and sending them to the server.
Real-time Data Display: Server GUI updates with the latest metrics from the client.
LED Indicator: A virtual LED in the server GUI indicates active connection status.
Exit Button: Both applications feature an exit button for graceful shutdown.
Requirements
Raspberry Pi (for client)
Python 
PySimpleGUI
Network connectivity between server and client
Usage
Start the Server: Run ServerSS.py on your PC or Raspberry Pi.
Run the Client: Execute clientSS.py on the Raspberry Pi.
Monitor Metrics: View real-time system metrics on the server GUI.
Troubleshooting
Ensure network connectivity and correct IP settings. For any errors, refer to the console logs.
