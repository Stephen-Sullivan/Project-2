import socket
import json
import threading
import PySimpleGUI as sg
import time

# Constants
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5001
LED_ON = '●'  # Unicode symbol for LED ON
LED_OFF = '○'  # Unicode symbol for LED OFF


class ServerGUI:
    def __init__(self):
        self.layout = [
            [sg.Text("Temperature: --", key='-TEMP-', size=(25, 1))],
            [sg.Text("Voltage: --", key='-VOLT-', size=(25, 1))],
            [sg.Text("Clock Speed: --", key='-CLOCK-', size=(25, 1))],
            [sg.Text("HDMI Clock Speed: --", key='-HDMI_CLOCK-', size=(25, 1))],
            [sg.Text("GPU Memory Frequency: --", key='-GPU_MEM_FREQ-', size=(25, 1))],  # New element for GPU memory frequency
            [sg.Text(LED_OFF, key='-LED-', font=("Helvetica", 24), text_color='red')],
            [sg.Button("Exit")]
        ]
        self.window = sg.Window("Server Data Display", self.layout, size=(300, 250), finalize=True)

    def update_data(self, data):
        try:
            # Convert data to float and format to one decimal place
            temp = float(data['temp'].split()[0])
            volt = float(data['volt'].split()[0])
            clock_speed = float(data['clock_speed'].split()[0])
            hdmi_clock_speed = float(data['hdmi_clock_speed'].split()[0])
            gpu_mem_freq = float(data['gpu_mem_freq'].split()[0])
            
            # Update GUI elements with formatted data
            self.window['-TEMP-'].update(f"Temperature: {temp:.1f}°C")
            self.window['-VOLT-'].update(f"Voltage: {volt:.1f}V")
            self.window['-CLOCK-'].update(f"Clock Speed: {clock_speed:.1f}MHz")
            self.window['-HDMI_CLOCK-'].update(f"HDMI Clock Speed: {hdmi_clock_speed:.1f}MHz")
            self.window['-GPU_MEM_FREQ-'].update(f"GPU Memory Frequency: {gpu_mem_freq:.1f}MHz")
        except ValueError as e:
            print(f"Error in update_data: {e}")
    def update_led(self, status):
        led_symbol = LED_ON if status else LED_OFF
        self.window['-LED-'].update(led_symbol, text_color='green' if status else 'red')

class Server:
    def __init__(self, gui):
        self.gui = gui
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((SERVER_HOST, SERVER_PORT))
        self.sock.listen(1)
        self.active_connections = 0
        self.led_status = False

    def toggle_led(self):
        while True:
            if self.active_connections > 0:
                self.led_status = not self.led_status
                self.gui.window.write_event_value('-LED-', self.led_status)
            time.sleep(1)


    def handle_client(self, client_socket, address):
        self.active_connections += 1
        self.gui.update_led(True)  # Turn on LED when a client connects
        print(f"Handling new client from {address}")
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                data_json = json.loads(data)
                # Convert data to float and format to one decimal place
                data_json['temp'] = f"{float(data_json['temp'].split()[0]):.1f}"
                data_json['volt'] = f"{float(data_json['volt'].split()[0]):.1f}"
                data_json['clock_speed'] = f"{float(data_json['clock_speed'].split()[0]):.1f}"
                data_json['hdmi_clock_speed'] = f"{float(data_json['hdmi_clock_speed'].split()[0]):.1f}"
                data_json['gpu_mem_freq'] = f"{float(data_json['gpu_mem_freq'].split()[0]):.1f}"
                self.gui.update_data(data_json)
        except Exception as e:
            print(f"An error occurred with {address}: {e}")
        finally:
            client_socket.close()
            print(f"Disconnected from {address}")
            self.gui.update_led(False)  # Turn off LED when client disconnects
            self.active_connections -= 1  # Corrected from += to -=
            
    def run(self):
        led_thread = threading.Thread(target=self.toggle_led)
        led_thread.start()
        while True:
            client_socket, address = self.sock.accept()
            self.led_status = True
            self.gui.update_led(self.led_status)
            print(f"Connection from {address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            client_thread.start()

if __name__ == "__main__":
    gui = ServerGUI()
    server = Server(gui)
    server_thread = threading.Thread(target=server.run)
    server_thread.start()

    while True:
        event, values = gui.window.read()
        if event == sg.WIN_CLOSED or event == "Exit":
            break

    server_thread.join()
    gui.window.close()
