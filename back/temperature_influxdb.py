from datetime import datetime
import time
import pytz
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import configparser

from temperature import Temperature


class TemperatureInfluxDB(Temperature):
    """Extension of Temperature that stores the fetched values in InfluxDB."""

    def __init__(self, config_path: str, gpio_pin=4):
        super().__init__(gpio_pin)
        self.config = self.load_config(config_path)
        self.client = InfluxDBClient(
            url=self.config.get("influxdb", "url"),
            token=self.config.get("influxdb", "token"),
            org=self.config.get("influxdb", "org"),
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.sensor_names = self._load_sensor_names()
    
    def _load_sensor_names(self) -> dict:
        """Load sensor name mappings from config if available."""
        sensor_names = {}
        if self.config.has_section("temperature_sensors"):
            for sensor_id, sensor_name in self.config.items("temperature_sensors"):
                sensor_names[sensor_id] = sensor_name
        return sensor_names

    def load_config(self, config_path: str) -> configparser.ConfigParser:
        parser = configparser.ConfigParser()
        parser.read(config_path)
        return parser

    def save_influxdb(self, temperatures: dict) -> None:
        """
        Save temperature readings to InfluxDB.
        
        Args:
            temperatures: Dictionary mapping sensor_id to temperature in Celsius.
        """
        timestamp = datetime.now(tz=pytz.timezone("Europe/Paris"))

        points = []
        for sensor_id, temp in temperatures.items():
            point = Point("temperature")
            # Tag with sensor ID (unique identifier)
            point.tag("sensor_id", sensor_id)
            # Tag with sensor name/location if configured, otherwise use sensor_id
            sensor_name = self.sensor_names.get(sensor_id, sensor_id)
            point.tag("sensor", sensor_name)
            point.field("celsius", float(temp))
            point.time(timestamp)
            points.append(point)

        if points:
            self.write_api.write(
                bucket=self.config.get("influxdb", "bucket"),
                org=self.config.get("influxdb", "org"),
                record=points,
            )

    def save_temperature(self) -> None:
        """Read temperatures from all sensors and save them to InfluxDB."""
        try:
            temperatures = self.get_temperature()
            if temperatures:
                sensor_info = ", ".join([f"{sid}: {temp:.2f}°C" for sid, temp in temperatures.items()])
                #print(f"Temperatures: {sensor_info}")
                self.save_influxdb(temperatures)
            else:
                print("No temperature readings available")
        except Exception as e:
            print(f"An error occurred while saving temperature: {e}")

