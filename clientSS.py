"""
client
"""
import socket
import json
import time
import subprocess
import PySimpleGUI as sg
from sys import platform
from threading import Thread

# Verify running on a Raspberry Pi
if not platform.startswith('linux'):
    sg.PopupError("This client script can only be run on a Raspberry Pi.")
    exit()

# Constants
SERVER_HOST = '127.0.0.1'  # The server's hostname or IP address
SERVER_PORT = 5001         # The port used by the server
DATA_SEND_INTERVAL = 2     # seconds
TOTAL_ITERATIONS = 50

def execute_vcgencmd(command):
    """Execute a vcgencmd command and return the output."""
    try:
        result = subprocess.run(['vcgencmd', command], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error executing vcgencmd: {e}")
        return "N/A"

# Data Collection Functions
def get_temperature():
    output = execute_vcgencmd('measure_temp')
    return output.replace('temp=', '').replace("'C", '')

def get_voltage():
    output = execute_vcgencmd('measure_volts')
    return output.replace('volt=', '').replace('V', '')

def get_clockspeed():
    output = execute_vcgencmd('measure_clock arm')
    clock_speed = float(output.split('=')[1]) / 1e6  # Convert from Hz to MHz
    return f"{clock_speed} MHz"

def get_hdmi_clockspeed():
    output = execute_vcgencmd('measure_clock hdmi')
    hdmi_clock_speed = float(output.split('=')[1]) / 1e6  # Convert from Hz to MHz
    return f"{hdmi_clock_speed} MHz"

def get_gpu_memory_frequency():
    """Retrieves the GPU memory frequency."""
    output = execute_vcgencmd('measure_clock v3d')
    gpu_mem_freq = float(output.split('=')[1]) / 1e6  # Convert from Hz to MHz
    return f"{gpu_mem_freq} MHz"


# GUI for Connection Status using PySimpleGUI
class ClientGUI:
    def __init__(self):
        self.layout = [
            [sg.Text("Not Connected", key='-STATUS-', text_color="red", size=(20, 1))],
            [sg.Button("Exit")]
        ]
        self.window = sg.Window("Client Status", self.layout, finalize=True)

    def update_status(self, text, color):
        self.window['-STATUS-'].update(text, text_color=color)

    def close(self):
        self.window.close()

# Client Class
class Client:
    def __init__(self, gui):
        self.gui = gui
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((SERVER_HOST, SERVER_PORT))
            self.gui.update_status("Connected", "green")
        except socket.error as e:
            print(f"Connection Error: {e}")
            self.gui.update_status("Connection Error", "red")
            time.sleep(3)
            self.gui.close()
            exit()

    def send_data(self):
        try:
            for _ in range(TOTAL_ITERATIONS):
                data = {
                    "temp": get_temperature(),
                    "volt": get_voltage(),
                    "clock_speed": get_clockspeed(),
                    "hdmi_clock_speed": get_hdmi_clockspeed(),
                    "gpu_mem_freq": get_gpu_memory_frequency()
                }
                self.sock.sendall(json.dumps(data).encode('utf-8'))
                time.sleep(DATA_SEND_INTERVAL)
        except socket.error as e:
            print(f"Error sending data: {e}")
        finally:
            self.sock.close()
            self.gui.update_status("Disconnected", "red")

    def run(self):
        self.connect()
        Thread(target=self.send_data, daemon=True).start()

# Main
if __name__ == "__main__":
    gui = ClientGUI()
    client = Client(gui)
    Thread(target=client.run, daemon=True).start()

    # Event loop
    while True:
        event, values = gui.window.read()
        if event == sg.WIN_CLOSED or event == "Exit":
            break
    gui.close()
