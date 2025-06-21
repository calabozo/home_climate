import random
import xml.etree.ElementTree as ET
from typing import Dict, List
import configparser
import requests


class WiBeee:
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


