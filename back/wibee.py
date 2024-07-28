import socket
import time
from datetime import datetime, timedelta, timezone
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS



class WiBeee:
    def __init__(self, config_path):
        # InfluxDB connection parameters
        # Load configuration from config file        
        self.config = self.load_config(config_path)
        self.url = self.config['influxdb']['url']
        self.token = self.config['influxdb']['token']
        self.org = self.config['influxdb']['org']
        self.bucket = self.config['influxdb']['bucket']

        # Define host and port as property variables
        self.host = self.config['wibee']['listen_address']
        self.port = int(self.config['wibee']['listen_port'])

        # Initialize InfluxDB client
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        

    def load_config(self, config_path):
        import configparser
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def start_server(self):

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(1)

        print(f"Server listening on {self.host}:{self.port}")

        while True:
            client_socket, address = server_socket.accept()
            print(f"Connection from {address}")

            data = client_socket.recv(1024).decode('utf-8')
            print(f"Received data: {data}")

            # Parse the received data
            params = dict(param.split('=') for param in data.split('?')[1].split('&'))

            # Extract power, energy, and time parameters
            power_params = {k: v for k, v in params.items() if k.startswith('p')}
            energy_params = {k: v for k, v in params.items() if k.startswith('e')}
            time_param = params.get('time')

            print("Power parameters:")
            for k, v in power_params.items():
                print(f"{k}: {v}")

            print("Energy parameters:")
            for k, v in energy_params.items():
                print(f"{k}: {v}")

            print(f"Timestamp: {time_param}")

            current_time = datetime.now().astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
            response_text = "<<<WBAVG"
            response = (
                "HTTP/1.1 200 OK\r\n"
                f"Date: {current_time}\r\n"
                "Content-Type: application/json\r\n"
                f"Content-Length: {len(response_text)}\r\n"
                "Connection: keep-alive\r\n"
                "Server: nginx\r\n"
                "\r\n"
                f"{response_text}"
            )
            client_socket.send(response.encode('utf-8'))
            # Call the save_influxdb method
            self.save_influxdb(time_param, power_params, energy_params)

            client_socket.close()

    def save_influxdb(self, time_param, power_params, energy_params):
        # Convert timestamp to datetime object
        timestamp = datetime.fromtimestamp(int(time_param))

        # Create data points
        points = []
        for k, v in power_params.items():
            point = Point("power").tag("sensor", k).field("value", float(v)).time(timestamp)
            points.append(point)
        
        for k, v in energy_params.items():
            point = Point("energy").tag("sensor", k).field("value", float(v)).time(timestamp)
            points.append(point)

        # Write data points to InfluxDB
        self.write_api.write(bucket=self.bucket, org=self.org, record=points)

