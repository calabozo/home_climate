from air_vent import open_vent, close_vent, get_vent_status
from flask import Flask, jsonify, render_template
import os
from wibeee import WiBeee
from influxdb_client import InfluxDBClient
import configparser

app = Flask(__name__)

# Load WiBeee configuration once
wibeee = WiBeee(os.getenv("HC_CONFIG", "config.ini"))

# Load InfluxDB configuration
config_path = os.getenv("HC_CONFIG", "config.ini")
config = configparser.ConfigParser()
config.read(config_path)

# Initialize InfluxDB client
influxdb_client = InfluxDBClient(
    url=config.get("influxdb", "url"),
    token=config.get("influxdb", "token"),
    org=config.get("influxdb", "org"),
)




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





@app.route('/power')
def current_power():
    """Return the current power consumption directly from the WiBeee sensor."""

    try:
        data = wibeee.fetch()
        value = data["p_activa"][3]
    except Exception:
        value = None

    return jsonify(value=value)


@app.route('/power/history')
def power_history():
    """Return power consumption data from InfluxDB for the last hour."""
    try:
        query_api = influxdb_client.query_api()
        
        bucket = config.get("influxdb", "bucket")
        
        # Query for probe4 (total consumption) - based on app.py line 48 using index 3
        # Using relative time "-1h" for the last hour
        query = f'''
        from(bucket: "{bucket}")
          |> range(start: -1h)
          |> filter(fn: (r) => r["_measurement"] == "power")
          |> filter(fn: (r) => r["probe"] == "probe1")
          |> filter(fn: (r) => r["_field"] == "active")
          |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''
        
        result = query_api.query(org=config.get("influxdb", "org"), query=query)
        
        # Parse results into time series data
        times = []
        values = []
        
        for table in result:
            for record in table.records:
                times.append(record.get_time().isoformat())
                values.append(record.get_value())
        
        return jsonify({
            "times": times,
            "values": values
        })
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/temperature/history')
def temperature_history():
    """Return temperature data from InfluxDB for the last 6 hours."""
    try:
        query_api = influxdb_client.query_api()
        
        bucket = config.get("influxdb", "bucket")
        
        # Query for all temperature sensors for the last 6 hours
        # Aggregate by 5-minute windows to reduce data points
        query = f'''
        from(bucket: "{bucket}")
          |> range(start: -6h)
          |> filter(fn: (r) => r["_measurement"] == "temperature")
          |> filter(fn: (r) => r["_field"] == "celsius")
          |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
          |> yield(name: "mean")
        '''
        
        result = query_api.query(org=config.get("influxdb", "org"), query=query)
        
        # Parse results grouped by sensor
        # Structure: {sensor_name: {times: [...], values: [...]}}
        # InfluxDB groups results by tags, so each table represents one sensor
        sensor_data = {}
        
        for table in result:
            # Get sensor name from the first record (all records in a table have same tags)
            sensor_name = "unknown"
            if table.records:
                first_record = table.records[0]
                # Try to get sensor name from record values (tags are in values dict)
                sensor_name = first_record.values.get("sensor") or first_record.values.get("sensor_id", "unknown")
            
            if sensor_name not in sensor_data:
                sensor_data[sensor_name] = {"times": [], "values": []}
            
            for record in table.records:
                time_iso = record.get_time().isoformat()
                value = record.get_value()
                sensor_data[sensor_name]["times"].append(time_iso)
                sensor_data[sensor_name]["values"].append(value)
        
        return jsonify(sensor_data)
    except Exception as e:
        return jsonify(error=str(e)), 500


if __name__ == '__main__':
    app.run(debug=True)

