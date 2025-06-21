from datetime import datetime
import requests
import random
import xml.etree.ElementTree as ET
from typing import Dict, List
import time
import configparser
import os
import sys
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import pytz

class WiBeee:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.ip_address = self.config.get('WiBeee', 'ip_address')

        # Initialize InfluxDB client
        self.client = InfluxDBClient(url=self.config.get('influxdb', 'url'), 
                                     token=self.config.get('influxdb', 'token'), 
                                     org=self.config.get('influxdb', 'org'))
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        

    def load_config(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def fetch(self) -> Dict[str, List[float]]:
        url = f"http://{self.ip_address}/en/status.xml?rnd={random.random()}"
        response = requests.get(url)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        
        data = {
            "time": float(root.find("time").text),
            "p_activa": [],
            "p_aparent": [],
            "energia_activa": []
        }

        for fase in range(1, 5):
            data["p_activa"].append(float(root.find(f"fase{fase}_p_activa").text))
            data["p_aparent"].append(float(root.find(f"fase{fase}_p_aparent").text))
            data["energia_activa"].append(float(root.find(f"fase{fase}_energia_activa").text))

        return data
    
    
    def save_influxdb(self, time_param, active_power, apparent_power, energy):
        # Convert timestamp to datetime object
        timestamp = datetime.fromtimestamp(int(time_param), tz=pytz.timezone('Europe/Paris'))

        # Create data points
        points = []
        for i, (active, apparent) in enumerate(zip(active_power, apparent_power), 1):
            point = Point("power")
            point.tag("probe", f"probe{i}")
            point.field("active", float(active))
            point.field("apparent", float(apparent))
            point.time(timestamp)
            points.append(point)
        
        for i, e in enumerate(energy, 1):
            point = Point("energy")
            point.tag("probe", f"probe{i}")
            point.field("active", float(e))
            point.time(timestamp)
            points.append(point)

        # Write data points to InfluxDB
        self.write_api.write(bucket=self.config.get('influxdb', 'bucket'), 
                             org=self.config.get('influxdb', 'org'), 
                             record=points)
      
    def run(self):
        while True:
            try:
                wibeee_data = self.fetch()
                print(f"Time: {wibeee_data['time']} Power: {wibeee_data['p_activa'][3]:.2f} ")
                
                # Save the wibeee_data in InfluxDB
                self.save_influxdb(
                    wibeee_data['time'],
                    wibeee_data['p_activa'],
                    wibeee_data['p_aparent'],
                    wibeee_data['energia_activa']
                )
            except Exception as e:
                print(f"An error occurred: {e}")
            
            time.sleep(30)
