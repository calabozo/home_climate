from air_vent import open_vent, close_vent, get_vent_status
from flask import Flask, jsonify, render_template
import os
import configparser
import random
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/air_vent/open/<int:vent_id>')
def open_air_vent(vent_id):
    """Open the selected vent and record its status."""
    open_vent(vent_id)
    return jsonify(status="open", vent=vent_id)


@app.route('/air_vent/close/<int:vent_id>')
def close_air_vent(vent_id):
    """Close the selected vent and record its status."""
    close_vent(vent_id)
    return jsonify(status="closed", vent=vent_id)


@app.route('/air_vent/status/<int:vent_id>')
def air_vent_status(vent_id):
    """Return the current status for the requested vent."""
    status = "open" if get_vent_status(vent_id) else "closed"
    return jsonify(status=status, vent=vent_id)


def _load_ip_address():
    config_path = os.getenv("HC_CONFIG", "config.ini")
    parser = configparser.ConfigParser()
    parser.read(config_path)
    return parser.get("WiBeee", "ip_address")


def _fetch_power(ip_address):
    url = f"http://{ip_address}/en/status.xml?rnd={random.random()}"
    response = requests.get(url)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    return float(root.find("fase4_p_activa").text)


@app.route('/power')
def current_power():
    """Return the current power consumption directly from the WiBeee sensor."""

    try:
        ip_address = _load_ip_address()
        value = _fetch_power(ip_address)
    except Exception:
        value = None

    return jsonify(value=value)


if __name__ == '__main__':
    app.run(debug=True)
