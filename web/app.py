from air_vent import open_vent, close_vent, get_vent_status
from flask import Flask, jsonify, render_template
import os
from wibeee import WiBeee

app = Flask(__name__)

# Load WiBeee configuration once
wibeee = WiBeee(os.getenv("HC_CONFIG", "config.ini"))




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


if __name__ == '__main__':
    app.run(debug=True)

