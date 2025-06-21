from datetime import datetime
import random
import xml.etree.ElementTree as ET
from typing import Dict, List
import time
import configparser
import requests
import pytz
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


class WiBee:
    """Base class used to communicate with a WiBeee sensor."""

    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.ip_address = self.config.get("WiBeee", "ip_address")

    def load_config(self, config_path: str) -> configparser.ConfigParser:
        parser = configparser.ConfigParser()
        parser.read(config_path)
        return parser

    def fetch(self) -> Dict[str, List[float]]:
        url = f"http://{self.ip_address}/en/status.xml?rnd={random.random()}"
        response = requests.get(url)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        data = {
            "time": float(root.find("time").text),
            "p_activa": [],
            "p_aparent": [],
            "energia_activa": [],
        }

        for fase in range(1, 5):
            data["p_activa"].append(float(root.find(f"fase{fase}_p_activa").text))
            data["p_aparent"].append(float(root.find(f"fase{fase}_p_aparent").text))
            data["energia_activa"].append(float(root.find(f"fase{fase}_energia_activa").text))

        return data


class WiBeeInfluxDB(WiBee):
    """Extension of WiBee that stores the fetched values in InfluxDB."""

    def __init__(self, config_path: str):
        super().__init__(config_path)
        self.client = InfluxDBClient(
            url=self.config.get("influxdb", "url"),
            token=self.config.get("influxdb", "token"),
            org=self.config.get("influxdb", "org"),
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def save_influxdb(
        self, time_param: float, active_power: List[float], apparent_power: List[float], energy: List[float]
    ) -> None:
        timestamp = datetime.fromtimestamp(int(time_param), tz=pytz.timezone("Europe/Paris"))

        points = []
        for i, (active, apparent) in enumerate(zip(active_power, apparent_power), 1):
            point = Point("power").tag("probe", f"probe{i}")
            point.field("active", float(active))
            point.field("apparent", float(apparent))
            point.time(timestamp)
            points.append(point)

        for i, e in enumerate(energy, 1):
            point = Point("energy").tag("probe", f"probe{i}")
            point.field("active", float(e))
            point.time(timestamp)
            points.append(point)

        self.write_api.write(
            bucket=self.config.get("influxdb", "bucket"),
            org=self.config.get("influxdb", "org"),
            record=points,
        )

    def run(self) -> None:
        while True:
            try:
                data = self.fetch()
                print(f"Time: {data['time']} Power: {data['p_activa'][3]:.2f}")
                self.save_influxdb(
                    data["time"],
                    data["p_activa"],
                    data["p_aparent"],
                    data["energia_activa"],
                )
            except Exception as e:
                print(f"An error occurred: {e}")

            time.sleep(30)
