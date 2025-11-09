from datetime import datetime
import time
from typing import List
import pytz
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from wibeee import WiBeee


class WiBeeeInfluxDB(WiBeee):
    """Extension of WiBeee that stores the fetched values in InfluxDB."""

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

    def save_power(self) -> None:        
        try:
            data = self.fetch()
            #print(f"Time: {data['time']} Power: {data['p_activa'][3]:.2f}")
            self.save_influxdb(
                data["time"],
                data["p_activa"],
                data["p_aparent"],
                data["energia_activa"],
            )
        except Exception as e:
            print(f"An error occurred: {e}")

